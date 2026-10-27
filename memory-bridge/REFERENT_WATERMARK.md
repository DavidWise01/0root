# Gate 13: one-way referent watermark reception

**Canonical source:** [TOPH referent-events.jsonl](https://github.com/DavidWise01/toph-cortex/blob/main/memory/corpus-spine/referent-events.jsonl)  
**Public reader:** https://davidwise01.github.io/persist-cortex/referents/  
**Hallway receiving action:** https://github.com/DavidWise01/0root/actions/workflows/referent-anchor.yml

The Hallway independently fetches TOPH's append-only referent ledger, validates the SHA-256 event chain and deterministic provenance watermark, and accepts an explicitly selected source event by its full SHA-256 hash. This creates a **new** `memory-bridge/referents/<event_hash>.json` in the Hallway repository. The original TOPH record remains untouched.

Records may include network delay and HTTP Date readings, but these are **witnessed measurements or server assertions**, not proof of article authorship, independent UTC notarization, scientific priority, or relativistic time dilation. The precise user-supplied Scientific American/Navier–Stokes referent is preserved in TOPH's research note without fabricated article-content bytes.

No voting, no quorum, no retroactive edits, no automatic synchronization. The Hallway read-only replay and Git-parent ancestry audit preserve accepted receipts. The receiver requires explicit authenticated owner action; an empty receipt collection means none have been made.

To validate the receiver code locally:

```sh
python3 memory-bridge/referent_anchor.py verify-local
python3 -m unittest discover -s memory-bridge -p 'test_referent_anchor.py' -v
```
