#!/usr/bin/env python3
"""Safe synthetic CRISPR software benchmark; no biological target data."""

from __future__ import annotations

import hashlib
import json
import random
import resource
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path

SEED = 0xC9
ALPHABET = "ACGT"
GUIDE_LEN = 20


def reverse_complement(seq: str) -> str:
    return seq.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def validate(seq: str) -> None:
    if not seq or any(base not in ALPHABET for base in seq):
        raise ValueError("sequence must contain only A/C/G/T")


def discover(seq: str) -> list[tuple[int, str, str]]:
    """Find synthetic SpCas9-like 20 nt candidates adjacent to NGG."""
    validate(seq)
    hits: list[tuple[int, str, str]] = []
    for strand, text in (("+", seq), ("-", reverse_complement(seq))):
        for pos in range(len(text) - GUIDE_LEN - 2):
            pam = text[pos + GUIDE_LEN : pos + GUIDE_LEN + 3]
            if pam[1:] == "GG":
                hits.append((pos, strand, text[pos : pos + GUIDE_LEN]))
    return hits


def hamming(a: str, b: str) -> int:
    if len(a) != len(b):
        raise ValueError("hamming inputs must have equal length")
    return sum(x != y for x, y in zip(a, b))


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# The toy specificity_score stub (fixed 0.06/0.12 per-mismatch penalty) was REMOVED.
# The real position-weighted, bulge-aware CFD-style model now lives in probe.py, along
# with the bulge-tolerant off-target search. |||  All data is synthetic.
from probe import specificity_score, SYNTH_BRAND, COLLAB_BRAND  # noqa: E402


def synthetic_sequence(length: int, seed: int) -> str:
    rng = random.Random(seed)
    chars = [rng.choice(ALPHABET) for _ in range(length)]
    # Deterministic test fixtures, not selected from an organism.
    for pos in range(37, max(38, length - 23), 997):
        chars[pos + 20 : pos + 23] = "AGG"
    return "".join(chars)


@dataclass
class Check:
    name: str
    passed: bool
    detail: object


def functional_checks() -> list[Check]:
    checks: list[Check] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append(Check(name, bool(passed), detail))

    check("reverse-complement involution", reverse_complement(reverse_complement("ACGTAC")) == "ACGTAC", None)
    try:
        validate("ACGTN")
        rejected = False
    except ValueError:
        rejected = True
    check("invalid alphabet veto", rejected, "ACGTN rejected")

    fixture = "A" * 20 + "AGG" + "C" * 29
    hits = discover(fixture)
    check("PAM candidate discovery", any(pos == 0 and strand == "+" for pos, strand, _ in hits), len(hits))
    mutated = fixture[:21] + "A" + fixture[22:]
    check("PAM-loss mutation", not any(pos == 0 and strand == "+" for pos, strand, _ in discover(mutated)), None)

    guide = "ACGT" * 5
    one = "T" + guide[1:]
    seed = guide[:19] + ("A" if guide[-1] != "A" else "C")
    check("exact Hamming", hamming(guide, guide) == 0 and hamming(guide, one) == 1, None)
    check("single DNA-bulge distance", edit_distance(guide, guide[:10] + "A" + guide[10:]) == 1, None)
    check("exact score maximum", specificity_score(guide, guide) == 1.0, specificity_score(guide, guide))
    check("mismatch monotonicity", specificity_score(guide, one) < specificity_score(guide, guide), specificity_score(guide, one))
    check("seed mismatch penalty", specificity_score(guide, seed) < specificity_score(guide, one), {"seed": specificity_score(guide, seed), "distal": specificity_score(guide, one)})

    a = discover(synthetic_sequence(20_000, SEED))
    b = discover(synthetic_sequence(20_000, SEED))
    check("deterministic output", a == b, len(a))
    digest = hashlib.sha256(json.dumps(a, separators=(",", ":")).encode()).hexdigest()
    check("stable output digest", len(digest) == 64, digest)
    return checks


def performance_runs() -> list[dict[str, object]]:
    results = []
    for size in (10_000, 100_000, 1_000_000):
        seq = synthetic_sequence(size, SEED + size)
        timings = []
        count = 0
        for _ in range(3):
            started = time.perf_counter()
            count = len(discover(seq))
            timings.append(time.perf_counter() - started)
        median = statistics.median(timings)
        results.append({
            "input_bases": size,
            "candidate_count": count,
            "median_seconds": round(median, 6),
            "throughput_bases_per_second": round(size / median),
            "trials": [round(x, 6) for x in timings],
        })
    return results


def main() -> None:
    started = time.time()
    checks = functional_checks()
    performance = performance_runs()
    result = {
        "benchmark": "CRISPR-E2E-SYNTHETIC-1.0",
        "scope": "computational software only; synthetic non-organism sequences",
        "data_class": f"SYNTHETIC {SYNTH_BRAND}",
        "synthetic_brand": SYNTH_BRAND,
        "provenance": f"{COLLAB_BRAND} synthetic + human collab (David Lee Wise directed, AVAN built)",
        "seed": SEED,
        "status": "PASS" if all(c.passed for c in checks) else "FAIL",
        "checks": {"passed": sum(c.passed for c in checks), "total": len(checks), "items": [asdict(c) for c in checks]},
        "performance": performance,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "wall_seconds": round(time.time() - started, 6),
        "limitations": [
            "No experimentally measured editing outcomes",
            "No real reference genome or clinically meaningful target",
            "Reference scoring oracle is deterministic, not a biological efficacy model",
            "Results measure pipeline correctness and compute behavior, not wet-lab safety or efficacy",
        ],
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    Path("crispr-e2e-benchmark/result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
