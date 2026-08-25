#!/usr/bin/env python3
"""
CRISPR off-target PROBE  -  the bulge-tolerant search that replaces the toy stub.

|||  ALL DATA HERE IS SYNTHETIC. Every sequence is machine-generated noise, not a
|||  real genome, organism, pathogen, or deployable target. The ||| brand marks
|||  synthetic data and pipeline outputs so they can NEVER be mistaken for real
|||  biological sequence. This tool benchmarks a search ALGORITHM; it makes no
|||  biological efficacy, safety, or clinical claim.

What the old specificity_score was: a hand-made 0.06 / 0.12 per-mismatch penalty -
a stub. This removes it. The real frontier is two things the stub skipped:
  1. SEARCH with BULGES  -  off-targets differ from the guide not only by mismatches
     but by DNA/RNA bulges (indels). Mismatch-only search is easy; bulge-tolerant
     search is the combinatorially expensive open problem. That is the probe.
  2. A POSITION-WEIGHTED score (CFD-style product) - PAM-proximal seed mismatches
     cost more than distal ones. The STRUCTURE is real; the weights here are a
     documented, monotonic ILLUSTRATIVE profile, NOT fitted Doench-2016 values.
     Fitting real weights needs a published matrix / training data - out of scope,
     and that is the honest boundary of what software alone can claim.
"""
from __future__ import annotations

import hashlib
import json
import random
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path

SYNTH_BRAND = "|||"          # pure synthetic data (machine-generated noise)
COLLAB_BRAND = "|||."        # synthetic WITH human collaboration (the dot = the human hand)
SEED = 0xC9
ALPHABET = "ACGT"
GUIDE_LEN = 20


def brand_banner() -> str:
    return (f"{SYNTH_BRAND} SYNTHETIC DATA - not a real genome - computational benchmark only {SYNTH_BRAND}\n"
            f"{COLLAB_BRAND} tool provenance: synthetic + human collab (David Lee Wise directed, AVAN built) {COLLAB_BRAND}")


def validate(seq: str) -> None:
    # The ||| brand lives in metadata, never inside a sequence: sequences are ACGT only.
    if not seq or any(base not in ALPHABET for base in seq):
        raise ValueError("sequence must contain only A/C/G/T (the ||| brand is metadata, not sequence)")


def reverse_complement(seq: str) -> str:
    return seq.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def synthetic_sequence(length: int, seed: int) -> str:
    """Deterministic synthetic noise. Provenance is branded ||| by the caller, not inline."""
    rng = random.Random(seed)
    return "".join(rng.choice(ALPHABET) for _ in range(length))


# ----- the real position-weighted score (replaces the stub) -----

def position_penalty(i: int) -> float:
    """Per-mismatch penalty at guide index i (0 = PAM-distal, GUIDE_LEN-1 = PAM-proximal seed).
    Monotonic: seed mismatches cost more. ILLUSTRATIVE profile, not fitted CFD weights."""
    frac = i / (GUIDE_LEN - 1)
    return 0.02 + 0.18 * frac


BULGE_FACTOR = 0.5  # each bulge multiplies the score (indels are penalised, illustrative)


def specificity_score(guide: str, target: str, bulges: int = 0) -> float:
    """CFD-style product model. Exact match -> 1.0; PAM-proximal mismatches cost more;
    each bulge multiplies by BULGE_FACTOR. Computational only - NOT a biological efficacy model."""
    if len(guide) != len(target):
        # length differs => forced indel(s); fall back to edit-distance-scaled score
        bulges = max(bulges, abs(len(guide) - len(target)))
        n = min(len(guide), len(target))
        guide, target = guide[:n], target[:n]
    score = 1.0
    for i, (a, b) in enumerate(zip(guide, target)):
        if a != b:
            score *= (1.0 - position_penalty(i))
    score *= BULGE_FACTOR ** max(0, bulges)
    return round(score, 6)


# ----- the probe: bulge-tolerant alignment + off-target search -----

def align(guide: str, window: str) -> tuple[int, int]:
    """Minimum-edit global alignment of guide to a candidate window.
    Returns (mismatches, bulges) of the fewest-edit alignment (unit costs).
    bulges = number of gap columns (indels). O(len(guide) * len(window))."""
    n, m = len(guide), len(window)
    INF = 10 ** 9
    # dp[i][j] = (edits, gaps) minimising edits, tie-break fewer gaps
    dp = [[(INF, INF)] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = (0, 0)
    for j in range(1, m + 1):
        dp[0][j] = (j, j)          # leading gaps in guide
    for i in range(1, n + 1):
        dp[i][0] = (i, i)          # trailing gaps
        gi = guide[i - 1]
        for j in range(1, m + 1):
            sub_e, sub_g = dp[i - 1][j - 1]
            cand = (sub_e + (gi != window[j - 1]), sub_g)          # match / mismatch
            up_e, up_g = dp[i - 1][j]
            cand = min(cand, (up_e + 1, up_g + 1))                 # gap (bulge)
            left_e, left_g = dp[i][j - 1]
            cand = min(cand, (left_e + 1, left_g + 1))             # gap (bulge)
            dp[i][j] = cand
    edits, gaps = dp[n][m]
    return edits - gaps, gaps     # mismatches = edits not attributable to gaps


@dataclass
class Hit:
    pos: int
    strand: str
    mismatches: int
    bulges: int
    score: float
    brand: str = SYNTH_BRAND


def search_offtargets(guide: str, seq: str, max_mm: int, max_bulge: int) -> list[Hit]:
    """Find PAM-adjacent (NGG) sites where the guide aligns within max_mm mismatches
    and max_bulge bulges, on both strands. This is the expensive, bulge-tolerant core."""
    validate(guide)
    validate(seq)
    hits: list[Hit] = []
    for strand, text in (("+", seq), ("-", reverse_complement(seq))):
        for pos in range(GUIDE_LEN, len(text) - 2):
            if text[pos + 1: pos + 3] == "GG":                     # NGG PAM at pos..pos+2
                lo = max(0, pos - GUIDE_LEN - max_bulge)
                window = text[lo: pos]
                mm, bulges = align(guide, window[-(GUIDE_LEN + max_bulge):])
                if mm <= max_mm and bulges <= max_bulge:
                    aligned = window[-GUIDE_LEN:] if len(window) >= GUIDE_LEN else window
                    hits.append(Hit(pos, strand, mm, bulges, specificity_score(guide, aligned, bulges)))
    return hits


def aggregate_specificity(on_target_pos: int, hits: list[Hit]) -> float:
    """MIT-style guide specificity 0..100. Higher = fewer/weaker off-targets."""
    off = sum(h.score for h in hits if not (h.strand == "+" and h.pos == on_target_pos))
    return round(100.0 / (100.0 + 100.0 * off), 4)


# ----- checks -----

@dataclass
class Check:
    name: str
    passed: bool
    detail: object


def functional_checks() -> list[Check]:
    checks: list[Check] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append(Check(name, bool(passed), detail))

    guide = "ACGTACGTACGTACGTACGT"

    # exact score is the maximum
    check("exact score maximum", specificity_score(guide, guide) == 1.0, specificity_score(guide, guide))
    # PAM-proximal (seed) mismatch costs more than PAM-distal
    distal = guide[:1].translate(str.maketrans("A", "T")) + guide[1:]   # mismatch at index 0
    seed = guide[:-1] + ("A" if guide[-1] != "A" else "C")              # mismatch at index 19
    check("seed costs more than distal", specificity_score(guide, seed) < specificity_score(guide, distal),
          {"seed": specificity_score(guide, seed), "distal": specificity_score(guide, distal)})
    # a bulge lowers the score below a pure mismatch
    check("bulge penalised", specificity_score(guide, guide, bulges=1) < specificity_score(guide, distal), None)

    # the probe finds an exact on-target next to an NGG PAM
    on = guide + "AGG" + synthetic_sequence(60, SEED)
    hits = search_offtargets(guide, on, max_mm=0, max_bulge=0)
    check("on-target found (0 mm, 0 bulge)", any(h.mismatches == 0 and h.bulges == 0 for h in hits), len(hits))

    # a 1-mismatch off-target is found only when max_mm >= 1
    off1 = guide[:5] + ("A" if guide[5] != "A" else "C") + guide[6:] + "AGG" + "C" * 40
    check("mismatch off-target requires budget",
          len(search_offtargets(guide, off1, 0, 0)) < len(search_offtargets(guide, off1, 1, 0)),
          {"mm0": len(search_offtargets(guide, off1, 0, 0)), "mm1": len(search_offtargets(guide, off1, 1, 0))})

    # a BULGE off-target (guide vs a target with one extra base) is found only when max_bulge >= 1
    bulged = guide[:10] + "A" + guide[10:] + "AGG" + "C" * 40        # 1-nt DNA bulge before PAM
    found_no_bulge = any(h.bulges == 0 and h.mismatches == 0 for h in search_offtargets(guide, bulged, 3, 0))
    found_with_bulge = any(h.bulges == 1 for h in search_offtargets(guide, bulged, 3, 1))
    check("bulge off-target requires bulge budget", (not found_no_bulge) and found_with_bulge,
          {"exact_without_bulge": found_no_bulge, "with_bulge": found_with_bulge})

    # PAM is required
    no_pam = guide + "AAA" + "C" * 40
    check("PAM required", not any(h.mismatches == 0 and h.pos == GUIDE_LEN for h in search_offtargets(guide, no_pam, 0, 0)), None)

    # determinism + brand
    seq = synthetic_sequence(5000, SEED)
    a = search_offtargets(guide, seq, 3, 1)
    b = search_offtargets(guide, seq, 3, 1)
    check("deterministic search", [asdict(h) for h in a] == [asdict(h) for h in b], len(a))
    check("all data branded |||", all(h.brand == SYNTH_BRAND for h in a) and SYNTH_BRAND == "|||", SYNTH_BRAND)
    return checks


def search_stress() -> list[dict]:
    """Push the bulge-tolerant search to its wall. Bulge tolerance is the expensive axis."""
    guide = "ACGTACGTACGTACGTACGT"
    rows = []
    for max_bulge in (0, 1, 2):
        for size in (20_000, 80_000, 320_000):
            seq = synthetic_sequence(size, SEED + size)
            start = time.perf_counter()
            hits = search_offtargets(guide, seq, max_mm=4, max_bulge=max_bulge)
            elapsed = time.perf_counter() - start
            rows.append({
                "max_bulge": max_bulge,
                "input_bases": size,
                "hits": len(hits),
                "seconds": round(elapsed, 4),
                "bases_per_second": round(size / elapsed) if elapsed else None,
                "brand": SYNTH_BRAND,
            })
    return rows


def main() -> None:
    print(brand_banner())
    started = time.time()
    checks = functional_checks()
    stress = search_stress()

    # frontier readout: cost multiplier from adding bulge tolerance at the largest size
    by_bulge = {}
    for r in stress:
        if r["input_bases"] == 320_000:
            by_bulge[r["max_bulge"]] = r["seconds"]
    bulge_cost_multiplier = (round(by_bulge.get(2, 0) / by_bulge[0], 2)
                             if by_bulge.get(0) else None)

    result = {
        "benchmark": "CRISPR-OFFTARGET-PROBE-1.0",
        "data_class": f"SYNTHETIC {SYNTH_BRAND}",
        "synthetic_brand": SYNTH_BRAND,
        "provenance": f"{COLLAB_BRAND} synthetic + human collab (David Lee Wise directed, AVAN built)",
        "scope": "computational off-target SEARCH with mismatches + bulges; synthetic sequences only",
        "removed": "the toy specificity_score stub (fixed 0.06/0.12 per-mismatch penalty)",
        "now": "bulge-tolerant search + position-weighted CFD-style score (illustrative weights, not fitted)",
        "status": "PASS" if all(c.passed for c in checks) else "FAIL",
        "checks": {"passed": sum(c.passed for c in checks), "total": len(checks),
                   "items": [asdict(c) for c in checks]},
        "search_stress": stress,
        "frontier": {
            "hard_axis": "bulge (indel) tolerance - combinatorial, the genuinely expensive part",
            "bulge2_vs_bulge0_cost_multiplier_at_320kb": bulge_cost_multiplier,
            "unsolved_biologically": "true off-target ACTIVITY prediction has no closed form; the score here is a computational model, not wet-lab validated",
        },
        "wall_seconds": round(time.time() - started, 4),
        "limitations": [
            "|||  All sequences are synthetic noise, not a real genome or organism",
            "Scoring model is illustrative and position-weighted, NOT fitted Doench-2016 CFD values",
            "No biological editing efficacy, off-target safety, or clinical validity is established",
            "Measures search-algorithm correctness and compute cost only",
        ],
    }
    canonical = json.dumps({k: v for k, v in result.items() if k != "wall_seconds"},
                           sort_keys=True, separators=(",", ":")).encode()
    result["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    Path("probe-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(brand_banner())
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
