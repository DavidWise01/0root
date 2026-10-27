# ROOT0 Hallway — Threaded Persistent Loom (Gate 14)

Canonical source: [TOPH append-only loom ledger](https://github.com/DavidWise01/toph-cortex/blob/main/memory/corpus-spine/loom-events.jsonl).  
Public reader: https://davidwise01.github.io/persist-cortex/loom/  
Independent authenticated receiver: [Hallway loom-anchor workflow](https://github.com/DavidWise01/0root/actions/workflows/loom-anchor.yml).

This folder's `loom/<event_hash>.json` receipts are **one-way historical anchors**. The receiver reads the entire public loom journal and verifies its global SHA chain, `.dlw` watermark, per-thread predecessor, A/B/C independent witness predecessor, temporal phase ordering, cross-thread causality and the exact lowercase `cubit` constant in COPY or DISTILL transformations. It then exclusively creates a new independent receipt file and commits it to **0root**, without changing TOPH.

No such receipt is fabricated merely because the endpoint exists. An authorized user must invoke the Hallway action with an event sequence and exact hash after TOPH's manual witness append succeeds.

## Manual verification

```sh
python3 memory-bridge/loom_anchor.py verify-local
python3 -m unittest discover -s memory-bridge -p 'test_loom_anchor.py' -v
```

Previously accepted receipt files are protected by the Hallway Git-parent append-only audit, also used by other memory gates. A source Git branch may be rewritten by an administrator or force push outside these normal workflows; independent receipts make such divergence detectable while the Hallway's own history is preserved.

A/B/C are **separate witness lanes**, never votes. No quorum, agreement filter or automatic command execution. The `cubit` constant remains exact lowercase. `.dlw` identifies provenance; it is not a replacement for `cubit` or a signature by itself. GitHub Pages is a visualization, not an agent running in the background.
