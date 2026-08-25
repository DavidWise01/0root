#!/usr/bin/env python3
"""Adversarial stress-to-failure harness for the synthetic CRISPR baseline."""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import resource
import time
from pathlib import Path

import benchmark as baseline

MEMORY_LIMIT_MIB = int(os.environ.get("CRISPR_STRESS_MEMORY_MIB", "12288"))
CASE_TIMEOUT_SECONDS = int(os.environ.get("CRISPR_STRESS_TIMEOUT_SECONDS", "60"))


def worker(case: dict, connection) -> None:
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_MIB << 20, MEMORY_LIMIT_MIB << 20))
    started = time.perf_counter()
    try:
        if case["mode"] == "scan":
            length = case["length"]
            if case["pattern"] == "dense":
                sequence = "G" * length
            else:
                sequence = baseline.synthetic_sequence(length, baseline.SEED + length)
            hits = baseline.discover(sequence)
            digest = hashlib.sha256(str(len(hits)).encode()).hexdigest()
            detail = {"hits": len(hits), "digest": digest}
        elif case["mode"] == "edit":
            length = case["length"]
            a = "A" * length
            b = "A" * (length - 1) + "C"
            detail = {"distance": baseline.edit_distance(a, b)}
        else:
            raise ValueError("unknown stress mode")
        connection.send({"status": "PASS", "seconds": round(time.perf_counter() - started, 6), "detail": detail})
    except MemoryError:
        # Do not allocate a traceback or queue feeder thread while the address-space
        # limit is exhausted. The parent maps this reserved exit code to the result.
        os._exit(42)
    except BaseException as exc:
        connection.send({"status": "ERROR", "seconds": round(time.perf_counter() - started, 6), "error": f"{type(exc).__name__}: {exc}"})
    finally:
        connection.close()


def isolated(case: dict) -> dict:
    parent_connection, child_connection = mp.Pipe(duplex=False)
    process = mp.Process(target=worker, args=(case, child_connection))
    process.start()
    child_connection.close()
    process.join(CASE_TIMEOUT_SECONDS)
    if process.is_alive():
        process.terminate()
        process.join()
        result = {"status": "TIMEOUT", "seconds": CASE_TIMEOUT_SECONDS}
    elif process.exitcode == 42:
        result = {"status": "MEMORY_FAILURE"}
    elif parent_connection.poll():
        try:
            result = parent_connection.recv()
        except EOFError:
            result = {"status": "PROCESS_FAILURE", "exitcode": process.exitcode}
    else:
        result = {"status": "PROCESS_FAILURE", "exitcode": process.exitcode}
    parent_connection.close()
    return {**case, **result}


def capability_matrix() -> list[dict]:
    cases = [
        {"family": "SpCas9", "material": "DNA", "pam": "NGG", "guide_length": 20, "supported": True},
        {"family": "SaCas9", "material": "DNA", "pam": "NNGRRT", "guide_length": 21, "supported": False},
        {"family": "Cas12a", "material": "DNA", "pam": "TTTV", "guide_length": 23, "supported": False},
        {"family": "Cas13", "material": "RNA", "pam": "PFS/context", "guide_length": 28, "supported": False},
        {"family": "base editor", "material": "DNA", "pam": "configurable", "guide_length": 20, "supported": False},
        {"family": "prime editor", "material": "DNA/RNA", "pam": "configurable", "guide_length": "pegRNA", "supported": False},
    ]
    return cases


def invariant_attacks() -> list[dict]:
    attacks = []

    def record(name: str, expected: object, actual: object) -> None:
        attacks.append({"name": name, "pass": actual == expected, "expected": expected, "actual": actual})

    for value in ("", "ACGTN", "acgt", "AUGG"):
        try:
            baseline.validate(value)
            actual = "accepted"
        except ValueError:
            actual = "rejected"
        record(f"alphabet veto {value!r}", "rejected", actual)

    fixture = "A" * 20 + "AGG"
    record("minimum complete target", True, any(x[0] == 0 for x in baseline.discover(fixture)))
    record("one-base truncation", 0, len(baseline.discover(fixture[:-1])))
    record("reverse-complement conservation", fixture, baseline.reverse_complement(baseline.reverse_complement(fixture)))
    return attacks


def main() -> None:
    functional = invariant_attacks()
    capabilities = capability_matrix()

    scan_cases = []
    for pattern in ("seeded-random", "dense"):
        for length in (1_000_000, 2_000_000, 4_000_000, 8_000_000, 16_000_000,
                       32_000_000, 64_000_000, 128_000_000):
            result = isolated({"mode": "scan", "pattern": pattern, "length": length})
            scan_cases.append(result)
            if result["status"] != "PASS":
                break

    edit_cases = []
    for length in (128, 256, 512, 1024, 2048, 4096, 8192, 16384):
        result = isolated({"mode": "edit", "length": length})
        edit_cases.append(result)
        if result["status"] != "PASS":
            break

    unsupported = [x["family"] for x in capabilities if not x["supported"]]
    first_runtime_failure = next((x for x in scan_cases + edit_cases if x["status"] != "PASS"), None)
    report = {
        "benchmark": "CRISPR-E2E-STRESS-TO-FAILURE-1.0",
        "pid": os.getpid(),
        "scope": "synthetic computational stress only",
        "limits": {"per_case_memory_mib": MEMORY_LIMIT_MIB, "per_case_timeout_seconds": CASE_TIMEOUT_SECONDS},
        "functional_attacks": functional,
        "capability_matrix": capabilities,
        "scan_ladder": scan_cases,
        "edit_distance_ladder": edit_cases,
        "first_scope_failure": {
            "class": "CAPABILITY_BOUNDARY",
            "detail": f"baseline implements only fixed-length SpCas9/NGG DNA; unsupported: {', '.join(unsupported)}",
        },
        "first_runtime_failure": first_runtime_failure,
        "status": "BROKEN_AS_FULL_SCOPE",
        "baseline_regression": "PASS" if all(x["pass"] for x in functional) else "FAIL",
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    report["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    Path("crispr-e2e-benchmark/stress-result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    mp.set_start_method("fork")
    main()
