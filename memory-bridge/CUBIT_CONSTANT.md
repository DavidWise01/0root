# ROOT0 / Hallway — `cubit` is a constant

The exact lowercase token **`cubit`** is immutable when ROOT0 symbolic content is **copied or distilled**. No renaming, case normalization, plural substitution, or implicit change to `qubit`. `qubit` remains a distinct physics/hardware term.

The canonical contract is [TOPH's `cubit-constant.json`](https://github.com/DavidWise01/toph-cortex/blob/main/memory/corpus-spine/cubit-constant.json). Hallway has a direct copy of [the lexical validator](cubit_constant.py) and [its regression tests](test_cubit_constant.py) for offline verification of artifacts passing this bridge.

```sh
python3 memory-bridge/cubit_constant.py --source original.md --output copy.md --mode copy
python3 memory-bridge/cubit_constant.py --source original.md --output distilled.md --mode distill
python3 -m unittest discover -s memory-bridge -p 'test_cubit_constant.py' -v
```

Copies must keep the number of exact standalone `cubit` occurrences. Distillations must keep at least one `cubit` if the source contains it. Lexical validation cannot prove full semantic equivalence; a human or a stronger referent-aware pipeline still checks meaning.

The `.dlw` token is a separate provenance marker, not a replacement or synonym for `cubit`. The three witness lanes A/B/C remain independent, append-only, and without quorum.

Validation in this repository does not imply that every other DavidWise01 repository has a check installed. Reuse this exact contract at each corpus handoff.
