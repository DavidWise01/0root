#!/usr/bin/env python3
"""0root Hallway: independent, create-only historical anchors for Gate 14 loom.

Validates full remote Git thread chain, .dlw marks, witness predecessor lanes,
past/present/future constraints and exact cubit copy/distill semantics before
saving a separately immutable receipt. No backward write or quorum.
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
import urllib.error
import urllib.request

import cubit_constant

ROOT=Path(__file__).resolve().parents[1]
INBOX=ROOT/"memory-bridge"/"loom"
URL="https://raw.githubusercontent.com/DavidWise01/toph-cortex/main/memory/corpus-spine/loom-events.jsonl"
DOMAIN="ROOT0-THREADED-LOOM-v1\n"
HEX=re.compile(r"^[a-f0-9]{64}$")
THREAD=re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PHASES=("PAST_OBSERVES","PRESENT_DESERVES","FUTURE_RESERVES")
KINDS=("OPEN","WEAVE","LINK","COPY","DISTILL","CHECKPOINT","CLOSE")
FIELDS={"version","seq","kind","recorded_at","event_on","thread","witness",
        "phase","what","how","why","text","refs","source","corpus_tip",
        "thread_prev","witness_prev","mode","prev","watermark","hash"}

def canon(x:dict)->bytes:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def digest(x:dict)->str:
    return hashlib.sha256(canon(x)).hexdigest()

def mark(body:dict)->str:
    return ".dlw:"+hashlib.sha256(DOMAIN.encode("ascii")+canon(body)).hexdigest()

def verify(rows:list[dict])->str:
    if not isinstance(rows,list):raise ValueError("Loom journal must be array")
    prev="GENESIS";threads={};lanes={}
    for idx,e in enumerate(rows,1):
        if not isinstance(e,dict) or set(e)!=FIELDS or e["version"]!=14 or type(e["seq"]) is not int or e["seq"]!=idx or e["prev"]!=prev:
            raise ValueError(f"Loom {idx}: malformed sequence")
        if e["kind"] not in KINDS or e["phase"] not in PHASES or e["witness"] not in ("A","B","C") or not isinstance(e["thread"],str) or not THREAD.fullmatch(e["thread"]):
            raise ValueError(f"Loom {idx}: unknown kind, witness, phase or thread")
        if not isinstance(e["recorded_at"],str) or not e["recorded_at"].endswith("Z"):
            raise ValueError(f"Loom {idx}: UTC Z record time required")
        t=dt.datetime.fromisoformat(e["recorded_at"].replace("Z","+00:00")).date()
        d=dt.date.fromisoformat(e["event_on"])
        position=PHASES.index(e["phase"])
        if (position==0 and d>t) or (position==1 and d!=t) or (position==2 and d<=t):
            raise ValueError(f"Loom {idx}: temporal date mismatch")
        if not isinstance(e["corpus_tip"],str) or not HEX.fullmatch(e["corpus_tip"]):
            raise ValueError(f"Loom {idx}: missing canonical corpus anchor")
        source=e["source"]
        if source is not None:
            if not isinstance(source,dict) or set(source)!={"repo","path","blob_sha","visibility"} or not re.fullmatch(r"DavidWise01/[A-Za-z0-9._-]+",source["repo"]) or not re.fullmatch(r"[a-f0-9]{40}",source["blob_sha"]) or source["visibility"]!="public":
                raise ValueError(f"Loom {idx}: invalid public Git source metadata")
        for key in ("what","how","why"):
            if not isinstance(e[key],str) or not 1<=len(e[key])<=1600:raise ValueError(f"Loom {idx}: missing explanation")
        if not isinstance(e["text"],str) or len(e["text"])>6000:raise ValueError(f"Loom {idx}: text too large")
        refs=e["refs"]
        if not isinstance(refs,list) or len(refs)>16 or any(type(x) is not int or x<1 or x>=idx for x in refs) or refs!=sorted(set(refs)):
            raise ValueError(f"Loom {idx}: invalid causal refs")
        thread=e["thread"];prior=threads.get(thread);lane=(thread,e["witness"]);previous=lanes.get(lane)
        if e["kind"]=="OPEN":
            if prior is not None or refs or e["thread_prev"] is not None or e["witness_prev"] is not None or position!=0:
                raise ValueError(f"Loom {idx}: illegal thread opening")
        else:
            if prior is None or e["thread_prev"]!=prior["seq"] or e["witness_prev"]!=(previous["seq"] if previous else None):
                raise ValueError(f"Loom {idx}: thread/witness predecessor mismatch")
            if previous and previous["kind"]=="CLOSE":raise ValueError(f"Loom {idx}: closed witness lane")
            if previous:
                k=PHASES.index(previous["phase"])
                if position<k or position>k+1:raise ValueError(f"Loom {idx}: temporal phase jump")
            elif position!=0:raise ValueError(f"Loom {idx}: missing PAST opening observation")
        if e["kind"] in ("COPY","DISTILL"):
            if e["mode"]!=e["kind"].lower() or not refs:raise ValueError(f"Loom {idx}: transform origin missing")
            original="\n".join(rows[n-1]["text"] for n in refs)
            cubit_constant.verify(original,e["text"],e["mode"])
        elif e["mode"] is not None:raise ValueError(f"Loom {idx}: stray transformation mode")
        if e["kind"]=="LINK" and (not refs or not any(rows[n-1]["thread"]!=thread for n in refs)):
            raise ValueError(f"Loom {idx}: LINK not cross-thread")
        if e["kind"]=="CLOSE" and previous is None:raise ValueError(f"Loom {idx}: closing unstarted witness")
        core={k:v for k,v in e.items() if k not in ("watermark","hash")}
        if e["watermark"]!=mark(core):raise ValueError(f"Loom {idx}: changed .dlw watermark")
        if e["hash"]!=digest({**core,"watermark":e["watermark"]}) or not HEX.fullmatch(e["hash"]):
            raise ValueError(f"Loom {idx}: incorrect SHA chain")
        threads[thread]=e;lanes[lane]=e;prev=e["hash"]
    return prev

def history()->list[dict]:
    request=urllib.request.Request(URL,headers={"User-Agent":"ROOT0-Hallway-loom/1"})
    with urllib.request.urlopen(request,timeout=20) as rsp:data=rsp.read(4_000_001)
    if len(data)>4_000_000 or (data and not data.endswith(b"\n")):
        raise ValueError("Remote loom oversized or incomplete")
    rows=[json.loads(line) for line in data.decode("utf-8").splitlines() if line]
    verify(rows)
    return rows

def local()->list[dict]:
    out=[]
    if not INBOX.is_dir():return out
    for file in sorted(INBOX.glob("*.json")):
        record=json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(record,dict) or set(record)!={"schema","receiver","accepted_at","event"} or record["schema"]!="root0.loom-anchor/14" or record["receiver"]!="DavidWise01/0root":
            raise ValueError("Invalid Hallway loom receipt")
        e=record["event"]
        if not isinstance(e,dict) or file.name!=e.get("hash","")+".json" or not HEX.fullmatch(e["hash"]):
            raise ValueError("Loom anchor filename mismatch")
        body={k:v for k,v in e.items() if k not in ("hash","watermark")}
        if mark(body)!=e.get("watermark") or digest({**body,"watermark":e["watermark"]})!=e["hash"]:
            raise ValueError("Hallway source event altered")
        out.append(record)
    return out

def receive(seq:int,sha:str)->Path:
    allowed=(os.environ.get("GITHUB_ACTIONS")=="true" and
             os.environ.get("GITHUB_REPOSITORY")=="DavidWise01/0root" and
             os.environ.get("GITHUB_REF")=="refs/heads/master" and
             os.environ.get("GITHUB_EVENT_NAME")=="workflow_dispatch" and
             os.environ.get("GITHUB_ACTOR_ID")=="148925959" and
             os.environ.get("GITHUB_WORKFLOW_REF","").endswith("/.github/workflows/loom-anchor.yml@refs/heads/master"))
    if not allowed:raise ValueError("Authenticated Hallway workflow required")
    if type(seq) is not int or seq<1 or not HEX.fullmatch(sha):raise ValueError("Invalid target seq/hash")
    remote=history()
    if seq>len(remote) or remote[seq-1]["hash"]!=sha:raise ValueError("Remote loom event absent or changed")
    if any(x["event"]["hash"]==sha for x in local()):raise ValueError("Already anchored")
    INBOX.mkdir(parents=True,exist_ok=True)
    target=INBOX/(sha+".json")
    item={"schema":"root0.loom-anchor/14","receiver":"DavidWise01/0root",
          "accepted_at":dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z"),
          "event":remote[seq-1]}
    with target.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(item,f,sort_keys=True,ensure_ascii=False,indent=2);f.write("\n")
    return target

def main(argv=None)->int:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("verify-local")
    a=sub.add_parser("receive");a.add_argument("--seq",type=int,required=True);a.add_argument("--hash",required=True)
    args=p.parse_args(argv)
    try:
        if args.cmd=="verify-local":print(f"PASS / independently anchored loom events={len(local())}")
        else:print("APPENDED HISTORICAL LOOM ANCHOR:",receive(args.seq,args.hash))
        return 0
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError,urllib.error.URLError) as exc:
        print("HALTED: "+str(exc),file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
