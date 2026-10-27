#!/usr/bin/env python3
"""0root independently appended irreversible key BLOCK decisions.

A BLOCK prevents *new* Hallway checkpoint acceptance; historical receipts
are still verified against the retained (not deleted) public key.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys

import checkpoint_receiver as receiver

LEDGER=Path(__file__).resolve().parent/"trust"/"key-decisions.jsonl"
FIELDS={"version","seq","kind","recorded_at","key_id","witness","github_actor_id","reason","prev","hash"}

def replay(rows:list[dict],pins:dict)->set[str]:
    if not isinstance(rows,list):raise ValueError("Receiver decisions not a list")
    prev="GENESIS";blocked=set()
    for n,e in enumerate(rows,1):
        if not isinstance(e,dict) or set(e)!=FIELDS or e["version"]!=1 or type(e["seq"]) is not int or e["seq"]!=n or e["prev"]!=prev or e["kind"]!="BLOCK":
            raise ValueError(f"Independent key decision {n}: invalid schema/sequence")
        pin=pins.get(e["key_id"])
        if not pin or pin["witness"]!=e["witness"] or str(pin["github_actor_id"])!=e["github_actor_id"] or e["key_id"] in blocked:
            raise ValueError(f"Independent key decision {n}: unpinned or already blocked")
        try:dt.date.fromisoformat(e["recorded_at"])
        except (ValueError,TypeError) as exc:raise ValueError("Invalid receiver decision date") from exc
        if not isinstance(e["reason"],str) or not 1<=len(e["reason"])<=500:raise ValueError("Reason required")
        if e["hash"]!=receiver.sha({k:v for k,v in e.items() if k!="hash"}):
            raise ValueError(f"Independent decision {n}: SHA mismatch")
        blocked.add(e["key_id"]);prev=e["hash"]
    return blocked

def read(path:Path,trust:dict)->list[dict]:
    if not path.exists():return []
    s=path.read_text(encoding="utf-8")
    if s and not s.endswith("\n"):raise ValueError("Truncated receiver decisions")
    rows=[json.loads(line) for line in s.splitlines() if line]
    replay(rows,trust);return rows

def main(argv=None)->int:
    parser=argparse.ArgumentParser()
    subs=parser.add_subparsers(dest="cmd",required=True)
    subs.add_parser("verify");subs.add_parser("status")
    a=subs.add_parser("block")
    a.add_argument("--key-id",required=True)
    a.add_argument("--reason",required=True)
    a.add_argument("--expected-tip",required=True)
    args=parser.parse_args(argv)
    try:
        trust=receiver.pins();rows=read(LEDGER,trust)
        prior=replay(rows,trust);tip=rows[-1]["hash"] if rows else "GENESIS"
        if args.cmd=="verify":print("PASS / blocked=%d / tip=%s"%(len(prior),tip))
        elif args.cmd=="status":print(json.dumps({"blocked_keys":sorted(prior),"tip":tip,"quorum":None,"votes":False},indent=2))
        else:
            if args.expected_tip!=tip:raise ValueError("Receiver decision CAS conflict")
            if not (os.environ.get("GITHUB_ACTIONS")=="true" and
                    os.environ.get("GITHUB_REPOSITORY")=="DavidWise01/0root" and
                    os.environ.get("GITHUB_EVENT_NAME")=="workflow_dispatch" and
                    os.environ.get("GITHUB_REF")=="refs/heads/master" and
                    os.environ.get("GITHUB_ACTOR_ID")=="148925959" and
                    os.environ.get("GITHUB_WORKFLOW_REF","").endswith("/.github/workflows/key-block.yml@refs/heads/master")):
                raise ValueError("Owner-authenticated Hallway workflow required")
            pin=trust.get(args.key_id)
            if not pin or args.key_id in prior:raise ValueError("Key absent from trust pins or already blocked")
            body={"version":1,"seq":len(rows)+1,"kind":"BLOCK",
                  "recorded_at":dt.datetime.now(dt.timezone.utc).date().isoformat(),
                  "key_id":args.key_id,"witness":pin["witness"],
                  "github_actor_id":str(pin["github_actor_id"]),
                  "reason":args.reason,"prev":tip}
            e={**body,"hash":receiver.sha(body)}
            replay([*rows,e],trust)
            with LEDGER.open("a",encoding="utf-8",newline="\n") as f:
                f.write(json.dumps(e,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n")
                f.flush();os.fsync(f.fileno())
            print("APPENDED LOCAL irreversible key block "+e["hash"])
        return 0
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
        print("HALTED: "+str(e),file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
