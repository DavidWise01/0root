# CRISPR synthetic stress-to-failure report

## Verdict

**BROKEN_AS_FULL_SCOPE**, while the original baseline regression remains **PASS**.

The earliest break is a declared capability boundary: the baseline implements
only fixed-length, SpCas9-like DNA targets adjacent to NGG. It does not implement
SaCas9, Cas12a, Cas13/RNA targeting, base-editor outcome models, or prime-editor
pegRNA models. This is an honest unsupported-feature result, not a biological
performance claim.

## Resource failure witnesses

Each case ran in an isolated process capped at 12,288 MiB of address space and
60 seconds. The sandbox hard ceiling was 15,032,385,536 bytes; the case cap
reserved operating headroom.

| Workload | Largest pass | First failure | Failure |
|---|---:|---:|---|
| Seeded-random sequence scan | 64,000,000 bases (50.364 s) | 128,000,000 bases | 60 s timeout |
| Dense-hit sequence scan | 32,000,000 bases (34.542 s) | 64,000,000 bases | 60 s timeout |
| Edit distance | 8,192 × 8,192 (18.047 s) | 16,384 × 16,384 | 60 s timeout |

Dense input produced 31,999,978 retained hit tuples at 32 million bases. No
case hit the raised memory ceiling; time became the first runtime boundary.
The edit-distance implementation exhibits quadratic work and storage, with the
doubling from 8,192 to 16,384 crossing the 60-second gate.

## Correctness attacks

All seven targeted invariants passed: empty/ambiguous/lowercase/RNA-like inputs
were rejected, the minimum complete target was found, a one-base truncation was
not found, and double reverse-complement was conserved.

## Reproduction

```sh
python3 crispr-e2e-benchmark/stress.py
python3 crispr-e2e-benchmark/benchmark.py
```

Stress result SHA-256:
`f3b1c3b754ee770c4c5471eb2fe90502e92438f7018ffe4eedec40be64fc6aa8`.

This suite uses synthetic strings only. It does not evaluate wet-lab editing,
delivery, cell viability, efficacy, clinical safety, or real-genome specificity.
