#!/usr/bin/env python3
"""0root independent append-only receipt of ROOT0 watermarked public referents.

Records exactly one independently fetched source event. No sender write access,
no website private keys, no quorum, no inference of physical time dilation.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
INBOX=ROOT/"memory-bridge"/"referents"
SOURCE="https://raw.githubusercontent.com/DavidWise01/toph-cortex/main/memory/corpus-spine/referent-events.jsonl"
DOMAIN="ROOT0-WATERMARK-v1\n"
HEX=re.compile(r"^[0-9a-f]{64}$")
KINDS=("REGISTER","SAMPLE","CORRECT")
KEYS={"version","seq","kind","recorded_at","witness","github_actor_id","referent_id",
    "referent_uri","basis","what","how","why","claimed_author","content_sha256",
    "source_seq","sample","prev","watermark","hash"}

def canonical(x:dict)->bytes:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def hashed(x:dict)->str:
    return hashlib.sha256(canonical(x)).hexdigest()

def watermark(e:dict)->str:
    core={k:v for k,v in e.items() if k not in ("hash","watermark")}
    return hashlib.sha256(DOMAIN.encode("ascii")+canonical(core)).hexdigest()

def verify_row(e:dict)->None:
    if not isinstance(e,dict) or set(e)!=KEYS or e["version"]!=1 or type(e["seq"]) is not int or e["seq"]<1 or e["kind"] not in KINDS:
        raise ValueError("Invalid referent source event schema")
    if e["witness"] not in ("A","B","C") or not isinstance(e["github_actor_id"],str) or not e["github_actor_id"].isdigit():
        raise ValueError("Invalid source witness")
    if not isinstance(e["referent_uri"],str) or not e["referent_uri"].startswith("https://"):
        raise ValueError("Bad URI")
    if hashlib.sha256(e["referent_uri"].encode("utf-8")).hexdigest()!=e["referent_id"]:
        raise ValueError("Referent content locator mismatch")
    if not HEX.fullmatch(e["hash"]) or not HEX.fullmatch(e["watermark"]) or watermark(e)!=e["watermark"]:
        raise ValueError("Source watermark invalid")
    if hashed({k:v for k,v in e.items() if k!="hash"})!=e["hash"]:
        raise ValueError("Source event hash invalid")

def read_remote()->list[dict]:
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"ROOT0-independent-referent-receiver/1"})
    with urllib.request.urlopen(req,timeout=20) as resp:data=resp.read(4_000_001)
    if len(data)>4_000_000 or data and not data.endswith(b"\n"):
        raise ValueError("Source ledger oversized or incomplete")
    rows=[json.loads(x) for x in data.decode("utf-8").splitlines() if x]
    previous="GENESIS";registered={}
    for i,e in enumerate(rows,1):
        verify_row(e)
        if e["seq"]!=i or e["prev"]!=previous:raise ValueError("Source ledger not hash chained")
        if e["kind"]=="REGISTER":
            if e["referent_id"] in registered or e["source_seq"] is not None or e["sample"] is not None:
                raise ValueError("Malformed referent origin")
            registered[e["referent_id"]]=i
        elif e["source_seq"]!=registered.get(e["referent_id"]):
            raise ValueError("Referenced origin not in source chain")
        previous=e["hash"]
    return rows

def local()->list[dict]:
    found=[];seen=set()
    if not INBOX.exists():return []
    for path in sorted(INBOX.glob("*.json")):
        rec=json.loads(path.read_text(encoding="utf-8"))
        if rec.get("schema")!="root0.referent-anchor/1" or rec.get("receiver")!="DavidWise01/0root":
            raise ValueError("Untrusted independent receipt")
        event=rec.get("event");verify_row(event)
        if path.name!=event["hash"]+".json" or path.name in seen:
            raise ValueError("Receipt filename mismatch or duplicate")
        seen.add(path.name);found.append(rec)
    return found

def receive(seq:int,expected:str)->Path:
    if not (os.environ.get("GITHUB_ACTIONS")=="true" and os.environ.get("GITHUB_REPOSITORY")=="DavidWise01/0root" and
            os.environ.get("GITHUB_EVENT_NAME")=="workflow_dispatch" and os.environ.get("GITHUB_REF")=="refs/heads/master" and
            os.environ.get("GITHUB_ACTOR_ID")=="148925959" and
            os.environ.get("GITHUB_WORKFLOW_REF","").endswith("/.github/workflows/referent-anchor.yml@refs/heads/master")):
        raise ValueError("Owner-authenticated Hallway workflow required")
    if type(seq) is not int or seq<1 or not HEX.fullmatch(expected):
        raise ValueError("Invalid source sequence or expected hash")
    rows=read_remote()
    if seq>len(rows) or rows[seq-1]["hash"]!=expected:raise ValueError("Source event absent or changed")
    if any(x["event"]["hash"]==expected for x in local()):
        raise ValueError("Previously anchored referent cannot be appended again")
    INBOX.mkdir(parents=True,exist_ok=True)
    path=INBOX/(expected+".json")
    item={"schema":"root0.referent-anchor/1","receiver":"DavidWise01/0root",
          "accepted_at":dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z"),
          "event":rows[seq-1]}
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(item,f,sort_keys=True,indent=2,ensure_ascii=False)
        f.write("\n")
    return path

def main(argv=None)->int:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("verify-local")
    a=sub.add_parser("receive");a.add_argument("--seq",type=int,required=True);a.add_argument("--hash",required=True)
    args=p.parse_args(argv)
    try:
        if args.cmd=="verify-local":
            print(f"PASS / independent source anchors={len(local())}")
        else:print("APPENDED INDEPENDENT RECEIPT:",receive(args.seq,args.hash))
        return 0
    except (ValueError,OSError,KeyError,json.JSONDecodeError,urllib.error.URLError) as e:
        print("HALTED: "+str(e),file=sys.stderr);return 1

if __name__=="__main__":
    raise SystemExit(main())
