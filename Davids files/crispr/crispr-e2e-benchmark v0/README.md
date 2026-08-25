# CRISPR end-to-end computational benchmark

`|||` **All data here is synthetic** — machine-generated noise, never a real genome,
organism, patient, pathogen, or deployable target. The `|||` brand is stamped on every
synthetic dataset and pipeline output so it can never be mistaken for real biological
sequence. `|||.` marks anything **synthetic with human collaboration** (the dot is the
human hand). Sequences themselves stay A/C/G/T; the brand lives in metadata and banners.

This is a deterministic, synthetic benchmark for CRISPR analysis software. It does not use an organism, patient, pathogen, real genomic locus, or experimentally deployable target.

The real off-target **probe** (bulge-tolerant search + position-weighted score, replacing
the old toy stub) is `probe.py` — see `PROBE-REPORT.md`.

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

Adversarial stress-to-failure run:

```sh
python3 crispr-e2e-benchmark/stress.py
```

The max-cap stress run defaults to 12,288 MiB and 60 seconds per isolated case.
Override these with `CRISPR_STRESS_MEMORY_MIB` and
`CRISPR_STRESS_TIMEOUT_SECONDS`. Its
authoritative output is `stress-result.json`; `STRESS-REPORT.md` summarizes the
observed capability and resource boundaries. “Full scope” here means a software
capability audit, not experimental validation.
