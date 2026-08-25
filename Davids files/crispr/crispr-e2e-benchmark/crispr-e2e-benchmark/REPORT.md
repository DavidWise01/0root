# CRISPR-E2E-SYNTHETIC-1.0 — Run Report

Status: **PASS**

## Result

| Measure | Result |
| --- | ---: |
| Functional and mutation checks | 11/11 PASS |
| 10,000-base median throughput | 2,414,935 bases/s |
| 100,000-base median throughput | 2,721,703 bases/s |
| 1,000,000-base median throughput | 2,276,747 bases/s |
| Peak resident memory | 42,028 KiB |
| Total wall time | 1.797737 s |
| Deterministic seed | 201 (`0xC9`) |

Result SHA-256:

`13e31e1d9c53c7b1b16b925815e8b9a39ea30152f34cf1195c8aa12d8499eb6e`

## Passed gates

1. Reverse-complement involution
2. Invalid alphabet veto
3. PAM candidate discovery
4. PAM-loss mutation
5. Exact Hamming distance
6. Single-bulge edit distance
7. Exact-match score maximum
8. Mismatch monotonicity
9. PAM-proximal mismatch penalty
10. Deterministic output
11. Stable output digest

## Evidence classification

This is an executed computational benchmark over deterministic synthetic input. It tests software correctness, mutation sensitivity, reproducibility, throughput, and memory behavior. It is not an experimental genome-editing result and does not establish biological efficacy, off-target safety, clinical validity, or laboratory fitness.
