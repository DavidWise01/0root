# CRISPR end-to-end computational benchmark

This is a deterministic, synthetic benchmark for CRISPR analysis software. It does not use an organism, patient, pathogen, real genomic locus, or experimentally deployable target.

It measures:

- input validation;
- reverse-complement handling;
- PAM-adjacent candidate discovery on both strands;
- mismatch and single-bulge distance behavior;
- specificity-score invariants;
- mutation sensitivity;
- deterministic output and hashing;
- scaling at 10 kB, 100 kB, and 1 MB;
- runtime and peak resident memory.

Run:

```sh
python3 crispr-e2e-benchmark/benchmark.py
```

`result.json` is the authoritative run record. This benchmark evaluates computational behavior only. It does not establish biological editing efficiency, off-target safety, clinical validity, or fitness for laboratory use.
