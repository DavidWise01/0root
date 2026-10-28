# Gate 16 — Independent Hallway Prefix Audit

**Scope:** ROOT0 / TOPH Threaded Persistent Loom → independently preserved 0root Hallway Git history.

**Direction:** one-way, append-only. **Attribution:** `.dlw`. **Immutable lexical constant:** `cubit`. **Witnesses:** independent A/B/C, no votes, no quorum.

## Why this bound exists

A SHA chain that verifies only within the source repository can be replaced in its entirety by somebody with sufficient write privileges. A previously accepted receipt in a *separate* repository is a retained reference against which new source states can be checked.

Gate 16 adds a **source-prefix conservation requirement**:

```text
canonical TOPH / memory/corpus-spine/loom-events.jsonl
      ↓ replay version 14 + global SHA / thread / witness / .dlw / cubit
remote_events[receipt.event.seq - 1]
      ║
      ╚══ must equal independently accepted Hallway receipt.event
                 │
             NO MATCH → HALT NEW ACCEPTANCE
             MATCH    → may receive a different signed-source event
                 │
        new create-only memory-bridge/loom/<event-hash>.json
```

The check runs in [`loom_anchor.py`](loom_anchor.py) immediately **before any new Hallway receipt is written**. It validates the entire current source loom chain, replays all locally retained receipts, and checks each receipt against the same numbered source event. It refuses:

- **SOURCE ROLLBACK:** a previously anchored event's sequence no longer exists in TOPH.
- **SOURCE DIVERGENCE:** the event at that sequence differs, even if the replacement source chain has newly computed and internally valid hashes.
- **Duplicate historical receipts:** a repeated event sequence or SHA cannot be counted twice.

This is independent *observation* and historical conflict detection. It does not automatically rewrite TOPH, delete disputed receipts, send instructions to other GitHub repositories or synthesize witness claims.

## State observed October 27, 2026

The canonical TOPH journal contains one real event:

```text
loom_seq    : 1
thread      : tessy-1
kind        : OPEN
witness     : A
phase       : PAST_OBSERVES
event_hash  : 9368d3921ec95ad4c1ba02ce79f4bdde89516a1449d69a8f81dfbc1fa3e53780
```

The independent `memory-bridge/loom/` folder was not found in 0root when this protocol was drafted; **no successful independent receipt can be claimed**. The live UI must recheck both histories and propose the earliest source event lacking a matching receipt, never invent one.

## Manual independent anchoring

1. Open [Hallway Loom Anchor workflow](https://github.com/DavidWise01/0root/actions/workflows/loom-anchor.yml). Authenticate as the authorized GitHub owner.
2. Enter `loom_seq=1` and the **exact** hash above if the current TOPH ledger still has the same event at sequence 1. If another entry was added, refresh the source first.
3. The receiver obtains the current public TOPH chain, verifies the historical prefix, exclusively creates the one receipt file, then attempts a non-force Git push to the **0root** default branch.
4. Inspect the workflow's actual result and verify the receiver Git file exists before considering the receipt independently anchored.

For future additions, existing receipt checks remain mandatory: an old receipt cannot be silently replaced with the new source version.

## Verification

```sh
# Pure local file/history replay: does not contact TOPH.
python3 memory-bridge/loom_anchor.py verify-local

# Live independent remote audit: reads TOPH and compares against accepted receipts.
# No Git writes, no vote, no automatic acceptance.
python3 memory-bridge/loom_anchor.py audit-remote

# Offline synthetic fork/truncation/deduplication tests.
python3 -m unittest discover -s memory-bridge -p 'test_gate16_prefix.py' -v
```

Public read-only page: https://davidwise01.github.io/persist-cortex/loom/

## Natural limitations

- This bounds **public Git historical integrity and receipt consistency**. A Git SHA or `.dlw` watermark is not an Ed25519 signature or proof that a witness's WHAT/HOW/WHY is factually true.
- Independence depends on preservation of the Hallway repository/history and its authorization boundary. A sufficiently privileged actor could modify both repositories; stronger timestamp notarization requires an additional independently held anchor.
- An initial receipt requires the authorized receiving workflow to **actually run successfully**. A committed script alone is not evidence that reception occurred.
- A network error must be reported as **unverified**, not as proof that no receipts exist.
- The two source ledgers are public; no private local memory is uploaded.
- The separate Corpus Spine v2 link and source code should also be monitored, but this Gate 16 prefix check directly compares the numbered Loom event bytes across repository boundaries. It does not independently notarize the contents of every upstream public Git blob.
