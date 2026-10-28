#!/usr/bin/env python3
"""Gate17 independent 0root Stochieon kernel seal receiver.

Independent pinned source manifest Git-blob check, full SHA/.dlw journal replay,
complete scope check, existing local Loom receipt check, one-way create-only Git
history. HTTPS Date is unsigned; no invented trusted timestamp or quorum.
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
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
TRUST=ROOT/"memory-bridge"/"stochieon"/"trust-v1.json"
RECEIPTS=ROOT/"memory-bridge"/"stochieon"/"receipts"
LOOM=ROOT/"memory-bridge"/"loom"
RAW="https://raw.githubusercontent.com/DavidWise01/toph-cortex/main/memory/stochieon/"
SHA=re.compile(r"^[a-f0-9]{64}$")
DOMAIN="ROOT0-STOCHIEON-GATE17-v1\n"

def canon(x)->bytes:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def digest(x)->str:
    return hashlib.sha256(canon(x)).hexdigest()

def dtparse(x):
    if not isinstance(x,str) or not x.endswith("Z"):raise ValueError("Invalid UTC time")
    return dt.datetime.fromisoformat(x.replace("Z","+00:00"))

def pinned()->dict:
    obj=json.loads(TRUST.read_text(encoding="utf-8"))
    if obj.get("schema")!="root0.stochieon.trust/17" or obj.get("receiver")!="DavidWise01/0root" or obj.get("watermark")!=".dlw" or obj.get("constant")!="cubit" or obj.get("quorum") is not None:
        raise ValueError("Independent Stochieon trust pin malformed")
    return obj

def fetch(path:str)->bytes:
    url=RAW+path
    request=urllib.request.Request(url,headers={"User-Agent":"ROOT0-Stochieon-Hallway/17"})
    with urllib.request.urlopen(request,timeout=20) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000:raise ValueError("Public kernel source exceeds bounded receiver size")
    return raw

def source(trust:dict)->tuple[dict,list[dict]]:
    b=fetch("manifest-v1.json")
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!=trust["source_manifest"]["git_blob_sha"]:
        raise ValueError("STOCHIEON MANIFEST DIVERGENCE: independently pinned Git blob changed")
    m=json.loads(b)
    if m.get("schema")!="root0.stochieon.kernel/17" or m.get("name")!="stochieon" or m.get("contract",{}).get("constant")!="cubit":
        raise ValueError("Source kernel scope invalid")
    body=fetch("events-v1.jsonl")
    if body and not body.endswith(b"\n"):raise ValueError("Source kernel journal truncated")
    rows=[json.loads(x) for x in body.decode("utf-8").splitlines() if x]
    verify(rows,m,trust)
    return m,rows

def verify(rows:list[dict],m:dict,trust:dict)->str:
    if m.get("schema")!="root0.stochieon.kernel/17":raise ValueError("Wrong kernel manifest")
    if m.get("contract",{}).get("constant")!="cubit" or m.get("contract",{}).get("watermark")!=".dlw" or m.get("contract",{}).get("quorum") is not None:
        raise ValueError("Changed kernel constant or witness policy")
    nodes={n["id"]:n for n in m["endpoints"]}
    if len(nodes)!=len(m["endpoints"]):raise ValueError("Duplicate named kernel elements")
    fp=digest(m);prev="GENESIS";old=[];last={}
    for i,e in enumerate(rows,1):
        if not isinstance(e,dict) or e.get("version")!=17 or type(e.get("seq")) is not int or e["seq"]!=i or e.get("prev")!=prev or e.get("manifest_sha256")!=fp or e.get("witness") not in ("A","B","C"):
            raise ValueError(f"STOCHIEON EVENT #{i} malformed or chain changed")
        dtparse(e["recorded_at"])
        if not SHA.fullmatch(e["loom_tip"]) or not SHA.fullmatch(e["corpus_tip"]):raise ValueError("Source anchor missing")
        if e["kind"]=="OBSERVE":
            node=nodes.get(e["node_id"])
            ob=e.get("observation")
            if not node or not isinstance(ob,dict) or e.get("coverage") is not None or e.get("seal_root") is not None or e.get("hallway_receipt") is not None:
                raise ValueError("Source observation incomplete")
            if ob.get("time_quality")!="UNSIGNED_HTTP_DATE_NOT_TRUSTED_TSA" or ob.get("result") not in ("MATCH","MISMATCH","UNAVAILABLE","TOO_LARGE"):
                raise ValueError("Time evidence falsely elevated")
            if dtparse(ob["received_utc"])<dtparse(ob["sent_utc"]):
                raise ValueError("Negative observed network interval")
            if ob["result"]=="MATCH":
                if not SHA.fullmatch(ob.get("content_sha256") or ""):raise ValueError("No actually observed content hash")
                if node["kind"]=="git_file" and ob.get("git_blob_sha")!=node["expected_git_blob"]:
                    raise ValueError("Public Git pin mismatch")
            last[e["node_id"]]=e
        elif e["kind"]=="SEAL":
            required=sorted(n for n,v in nodes.items() if v["required"])
            expected=[]
            for n in required:
                record=last.get(n)
                if not record or record["observation"]["result"]!="MATCH":
                    raise ValueError("SEALED UNOBSERVED KERNEL ELEMENT "+n)
                if (dtparse(e["recorded_at"])-dtparse(record["recorded_at"])).total_seconds()>86400:
                    raise ValueError("Kernel measurement stale at seal")
                expected.append({"node_id":n,"observation_seq":record["seq"],
                                 "observation_hash":record["hash"]})
            root=digest({"scope":"stochieon-v17","coverage":expected,
                        "manifest":fp,"loom_tip":e["loom_tip"],
                        "corpus_tip":e["corpus_tip"]})
            if e.get("coverage")!=expected or e.get("seal_root")!=root:
                raise ValueError("Incomplete independently checked kernel seal")
            receipt=e.get("hallway_receipt")
            link=trust["required_loom_anchor"]
            if not isinstance(receipt,dict) or receipt.get("receiver")!="DavidWise01/0root" or receipt.get("source_seq")!=link["seq"] or receipt.get("source_hash")!=link["hash"] or not SHA.fullmatch(receipt.get("receipt_sha256","")):
                raise ValueError("Source falsely claims independent Loom receipt")
        else:raise ValueError("Unsupported kernel event kind")
        body={k:v for k,v in e.items() if k not in ("hash","watermark")}
        mark=".dlw:"+hashlib.sha256(DOMAIN.encode()+canon(body)).hexdigest()
        if e.get("watermark")!=mark or e.get("hash")!=digest({**body,"watermark":mark}):
            raise ValueError("STOCHIEON SHA/.dlw mismatch")
        prev=e["hash"];old.append(e)
    return prev

def local()->list[dict]:
    out=[]
    if not RECEIPTS.exists():return out
    for f in sorted(RECEIPTS.glob("*.json")):
        item=json.loads(f.read_text(encoding="utf-8"))
        e=item.get("seal")
        if item.get("schema")!="root0.stochieon-receipt/17" or item.get("receiver")!="DavidWise01/0root" or not isinstance(e,dict) or item.get("manifest_pin")!=pinned()["source_manifest"]["git_blob_sha"] or f.name!=e.get("hash","")+".json":
            raise ValueError("Invalid immutable kernel receipt file")
        content={k:v for k,v in item.items() if k!="receipt_watermark"}
        expected=".dlw:"+hashlib.sha256(b"ROOT0-STOCHIEON-RECEIVER-v1\n"+canon(content)).hexdigest()
        if item.get("receipt_watermark")!=expected:
            raise ValueError("Altered independent kernel receipt watermark")
        out.append(item)
    return out

def check_prefix(rows:list[dict],receipts:list[dict])->dict:
    seen=set()
    for r in receipts:
        e=r["seal"];seq=e["seq"]
        if seq in seen:raise ValueError("Duplicate independent Stochieon seal receipt")
        seen.add(seq)
        if seq>len(rows):raise ValueError("STOCHIEON SOURCE ROLLBACK: anchored seal missing")
        if rows[seq-1]!=e:raise ValueError("STOCHIEON SOURCE DIVERGENCE: old seal changed")
    return {"status":"PASS","receiver":"DavidWise01/0root","source_events":len(rows),
            "independent_seals":len(receipts),"quorum":None,"time_quality":"UNSIGNED_NOT_TSA"}

def accept(seq:int,expected_hash:str)->Path:
    env=os.environ
    if not (env.get("GITHUB_ACTIONS")=="true" and env.get("GITHUB_REPOSITORY")=="DavidWise01/0root"
            and env.get("GITHUB_REF")=="refs/heads/master" and env.get("GITHUB_EVENT_NAME")=="workflow_dispatch"
            and env.get("GITHUB_ACTOR_ID")=="148925959"
            and env.get("GITHUB_WORKFLOW_REF","").endswith("/.github/workflows/stochieon-accept.yml@refs/heads/master")):
        raise ValueError("Authenticated independent Hallway workflow required")
    trust=pinned();m,rows=source(trust);saved=local()
    check_prefix(rows,saved)
    if type(seq) is not int or seq<1 or seq>len(rows) or not SHA.fullmatch(expected_hash) or rows[seq-1]["hash"]!=expected_hash or rows[seq-1]["kind"]!="SEAL":
        raise ValueError("Only an existing exact verified Gate17 SEAL can be independently accepted")
    if any(x["seal"]["hash"]==expected_hash for x in saved):raise ValueError("Already accepted")
    src=rows[seq-1];link=trust["required_loom_anchor"]
    f=LOOM/(link["hash"]+".json")
    if not f.is_file():raise ValueError("No actual independently accepted Loom #1 receipt")
    b=f.read_bytes();ref=json.loads(b)
    if ref.get("schema")!="root0.loom-anchor/14" or ref.get("event",{}).get("hash")!=link["hash"] or hashlib.sha256(b).hexdigest()!=src["hallway_receipt"]["receipt_sha256"]:
        raise ValueError("Kernel SEAL's Hallway receipt bytes differ from independently held history")
    RECEIPTS.mkdir(parents=True,exist_ok=True)
    body={"schema":"root0.stochieon-receipt/17","receiver":"DavidWise01/0root",
          "accepted_at":dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z"),
          "manifest_pin":trust["source_manifest"]["git_blob_sha"],
          "seal":src,"trusted_tsa_timestamp":False}
    body["receipt_watermark"]=".dlw:"+hashlib.sha256(b"ROOT0-STOCHIEON-RECEIVER-v1\n"+canon(body)).hexdigest()
    target=RECEIPTS/(expected_hash+".json")
    with target.open("x",encoding="utf-8",newline="\n") as output:
        json.dump(body,output,sort_keys=True,ensure_ascii=False,indent=2)
        output.write("\n")
    return target

def main()->int:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("verify-local")
    sub.add_parser("audit-remote")
    a=sub.add_parser("accept")
    a.add_argument("--seq",type=int,required=True)
    a.add_argument("--hash",required=True)
    args=p.parse_args()
    try:
        if args.cmd=="verify-local":
            print(json.dumps({"status":"PASS","independent_receipts":len(local()),
                              "trusted_tsa":False},indent=2))
        elif args.cmd=="audit-remote":
            print(json.dumps(check_prefix(source(pinned())[1],local()),indent=2))
        else:print("STOCHIEON INDEPENDENT RECEIPT:",accept(args.seq,args.hash))
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError,urllib.error.URLError) as error:
        print("STOCHIEON HALTED: "+str(error),file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
