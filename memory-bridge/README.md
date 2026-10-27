# ROOT0 Hallway / Temporal Diode receiver

This directory is a **public, append-only, one-way memory receipt inbox** for the
ROOT0 Corpus Spine (Gate 09). It is NOT another source-of-truth memory database.

Canonical sources:
- [TOPH CORTEX — signed-in actor-bound delivery ledger](https://github.com/DavidWise01/toph-cortex/blob/main/memory/corpus-spine/delivery-events.jsonl)
- [TOPH CORTEX — temporal witness ledger](https://github.com/DavidWise01/toph-cortex/blob/main/memory/corpus-spine/temporal-events.jsonl)
- [Gate 09 dashboard](https://davidwise01.github.io/persist-cortex/identity-bridge/)
- [Gate 08 independent witness diode](https://davidwise01.github.io/persist-cortex/temporal/)

A receiver acknowledgement file must be **created in this repository's Git history**.
It must NEVER edit a prior acknowledgement. The read-only TOPH verifier accepts one
only after checking the exact Git blob SHA and the contents.

## Contract

File: `memory-bridge/receipts/<offer_hash>.json` (hex SHA-256 in filename).

```json
{
  "schema": "root0.delivery-ack/1",
  "offer_hash": "<exact TOPH OFFER event SHA-256>",
  "temporal_hash": "<exact referenced temporal witness SHA-256>",
  "destination_repo": "DavidWise01/0root",
  "received": true
}
```

The [manual receiver workflow](https://github.com/DavidWise01/0root/actions/workflows/temporal-receiver-ack.yml)
checks the GitHub-hosted OFFER and its temporal reference, requires the GitHub
repository-owner actor, then writes exactly one ACK JSON file and makes a non-force
Git commit. It does not send commands back upstream.

To finish a delivery, a registered temporal witness starts TOPH's authenticated
`delivery-receipt-append.yml` with the OFFER number and this ACK file's Git SHA.

No votes. No quorum. Future reservation is not execution. An ACK proves only
that the target repository hosts the matching receipt file, not that three
witnesses agree or that an agent executed any proposed action.

**Never include private snapshots or secrets in this public receipt.**
