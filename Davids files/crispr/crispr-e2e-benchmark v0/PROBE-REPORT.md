# CRISPR off-target PROBE — report

`|||` **All data is synthetic** — machine-generated noise, not a real genome, organism,
pathogen, or deployable target. `|||.` **Tool provenance: synthetic + human collab**
(David Lee Wise directed, AVAN built). The `|||` brand is metadata on every record and
pipe output; it is never inside a sequence (sequences are A/C/G/T only).

## What changed

**Removed:** the toy `specificity_score` stub — a fixed `0.06 / 0.12` per-mismatch
penalty that modelled nothing.

**Built (the probe):** a **bulge-tolerant off-target search** plus a **position-weighted
CFD-style score**. The search finds PAM-adjacent (NGG) sites where a guide aligns within
a mismatch budget **and** a bulge (indel) budget, on both strands, via minimum-edit
alignment. The score is a product model where PAM-proximal seed mismatches cost more than
distal ones, and each bulge multiplies the score down.

## Why bulges are the point

Mismatch-only search is easy. The genuinely hard, open problem is **bulge (indel)
tolerance** — an off-target can differ from the guide by an insertion/deletion, and those
are invisible to mismatch-only tools. The probe surfaces exactly those:

| bulge budget | 320 kb synthetic scan | off-targets found |
|---:|---:|---:|
| 0 | 5.17 s | **0** |
| 1 | 5.50 s | **1** |
| 2 | 5.65 s | **5** |

Five off-targets at bulge=2 that mismatch-only search (bulge=0) **cannot see**. That is
the capability the stub lacked entirely.

## The honest boundary

- The scoring **structure** is real (position-weighted product + bulge penalty). The
  **weights are illustrative and monotonic — NOT the fitted Doench-2016 CFD values.**
  Real weights need the published matrix or a training set.
- True off-target **activity** prediction has no closed form. This is a *computational
  specificity model*, not a wet-lab-validated efficacy model.
- Measures search-algorithm correctness and compute cost on synthetic strings only.

## Checks

9 / 9 PASS: exact-score maximum, seed-costs-more-than-distal, bulge penalised,
on-target found, mismatch off-target requires budget, **bulge off-target requires bulge
budget**, PAM required, deterministic search, and **all data branded `|||`**.

## Reproduce

```sh
python3 probe.py        # native; needs no 'resource' module
python3 benchmark.py    # now imports the real scorer from probe.py (stub removed)
```

Authoritative output: `probe-result.json` (carries `synthetic_brand: "|||"` and
`provenance: "|||."`).
