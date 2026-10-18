# ROOT0 · QUANTA shadow corpus — reference manifest v1

**Role:** shadow *index*, **not** a second physical dataset or a duplicated corpus. Source of truth stays in `DavidWise01/oasis`.

## Pairing
- **Primary / canonical:** [TESSY QUANTA corpus specification](https://github.com/DavidWise01/oasis/blob/main/docs/mnp-3d/QUANTA_CORPUS_ALIGNMENT_V1.md).
- **Metadata inventory:** [ROOT0 master discovery](https://github.com/DavidWise01/oasis/blob/main/docs/mnp-3d/ROOT0_MASTER_DISCOVERY_20261018.json), 2,144 repository **metadata** records, not independent observations.
- **Adapter:** [Quanta observer and prediction adapter](https://github.com/DavidWise01/oasis/blob/main/docs/mnp-3d/quanta-corpus-v1.js).
- **State / Space / Time:** [Complete SST specification](https://github.com/DavidWise01/oasis/blob/main/docs/mnp-3d/STATE_SPACE_TIME_MACHINE.md).
- **Validation:** [17 regression tests](https://github.com/DavidWise01/oasis/blob/main/docs/mnp-3d/test-quanta-corpus-v1.cjs).
- **Observer visual:** [Pinned-0 ripple](https://davidwise01.github.io/oasis/docs/mnp-3d/observer-ripple/).

## Shadow semantics
```text
0root.ai :: SHADOW CORPUS / READ-ONLY PROVENANCE ROUTE
oasis    :: CANONICAL CORPUS + QUANTA MODEL

0@[v,w,x,y,z]  pinned observer
x = state       y = space       z = time / what happened
-d read/verify  -d+ evaluate    +d append
OBSERVE → RECORD → ESTIMATE → PREDICT → WITNESS → UPDATE
```

The shadow exposes a pointer to the canonical corpus without duplicating records, taking authority from the canonical store, or generating outcomes from metadata alone.

Site principle maintained: **one host, no mirror**; no changes to sealed `.dlw` files, established worlds, lineage, or manifests. Count and contents are a dated reference to 2026-10-18, not a live count. New empirical observations need explicit original evidence and distinct witness records. No claim of physical quantum advantage.
