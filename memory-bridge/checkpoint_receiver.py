#!/usr/bin/env python3
"""Hallway independent signed-checkpoint receiver: PIN -> VERIFY -> APPEND.

Verifies TOPH source checkpoint and source-prefix roots with the independently
stored 0root trust pin; writes a new receipt in 0root only. Never modifies TOPH.
"""
from __future__ import annotations
import argparse
import base64
import binascii
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT=Path(__file__).resolve().parents[1]
TRUST=ROOT/"memory-bridge"/"trust"/"checkpoint-key-pins.json"
INBOX=ROOT/"memory-bridge"/"checkpoints"
BASE="https://raw.githubusercontent.com/DavidWise01/toph-cortex/main/memory/corpus-spine/"
STREAMS={"CORPUS":"events-v2.jsonl","TEMPORAL":"temporal-events.jsonl",
         "DELIVERY":"delivery-events.jsonl","ATTESTATION":"witness-attestations.jsonl"}
DOMAIN="ROOT0-CHECKPOINT-v1"
HEX=re.compile(r"^[0-9a-f]{64}$")
FIELDS={"version","seq","kind","recorded_at","witness","github_actor","github_actor_id",
        "key_id","state","prev","payload_sha256","signature_b64","hash"}

def canonical(x)->bytes:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def sha(x)->str:
    return hashlib.sha256(canonical(x)).hexdigest()

def decode64(s:str,n:int)->bytes:
    if not isinstance(s,str):raise ValueError("Expected base64")
    try:data=base64.b64decode(s,validate=True)
    except (ValueError,binascii.Error) as e:raise ValueError("Malformed base64") from e
    if len(data)!=n or base64.b64encode(data).decode()!=s:
        raise ValueError("Wrong-length/non-canonical base64")
    return data

def pins(path:Path=TRUST)->dict:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema")!="root0.checkpoint-trust-pins/1" or obj.get("receiver")!="DavidWise01/0root" or not isinstance(obj.get("pins"),list):
        raise ValueError("Invalid independent Hallway trust policy")
    out={}
    actor_ids=set()
    for item in obj["pins"]:
        if not isinstance(item,dict) or set(item)!={"witness","github_actor_id","key_id","public_key_b64"}:
            raise ValueError("Invalid pin format")
        if item["witness"] not in ("A","B","C") or not str(item["github_actor_id"]).isdigit():
            raise ValueError("Invalid pinned witness")
        raw=decode64(item["public_key_b64"],32)
        fingerprint=hashlib.sha256(raw).hexdigest()
        if fingerprint!=item["key_id"] or fingerprint in out:
            raise ValueError("Duplicate or incorrectly pinned key")
        # A single GitHub account cannot stand in for multiple witnesses.
        ident=(item["witness"],str(item["github_actor_id"]))
        if any(uid==ident[1] and lane!=ident[0] for lane,uid in actor_ids):
            raise ValueError("Same GitHub actor pinned to multiple witness lanes")
        actor_ids.add(ident)
        out[fingerprint]=item
    return out

def message(e:dict)->bytes:
    obj={"domain":DOMAIN,"witness":e["witness"],"key_id":e["key_id"],
         "recorded_at":e["recorded_at"],"checkpoint_seq":e["seq"],
         "previous_checkpoint":e["prev"],"state":e["state"]}
    return canonical(obj)

def verify_record(e:dict,trust:dict)->None:
    if not isinstance(e,dict) or set(e)!=FIELDS or e["version"]!=1 or e["kind"]!="CHECKPOINT" or type(e["seq"]) is not int or e["seq"]<1:
        raise ValueError("Malformed signed checkpoint event")
    if not isinstance(e["hash"],str) or not HEX.fullmatch(e["hash"]) or sha({k:v for k,v in e.items() if k!="hash"})!=e["hash"]:
        raise ValueError("Checkpoint event SHA-256 mismatch")
    entry=trust.get(e["key_id"])
    if not entry or e["witness"]!=entry["witness"] or e["github_actor_id"]!=str(entry["github_actor_id"]):
        raise ValueError("No independently pinned witness public key")
    try:dt.date.fromisoformat(e["recorded_at"])
    except (TypeError,ValueError) as exc:raise ValueError("Invalid record date") from exc
    payload=message(e)
    if hashlib.sha256(payload).hexdigest()!=e["payload_sha256"]:
        raise ValueError("Signed checkpoint envelope mismatch")
    try:Ed25519PublicKey.from_public_bytes(decode64(entry["public_key_b64"],32)).verify(
            decode64(e["signature_b64"],64),payload)
    except InvalidSignature as exc:raise ValueError("Ed25519 signature invalid") from exc

def verify_source_log(rows:list[dict])->None:
    if not isinstance(rows,list):raise ValueError("Source ledger not an array")
    prev="GENESIS"
    for i,e in enumerate(rows,1):
        if not isinstance(e,dict) or e.get("seq")!=i or e.get("prev")!=prev:
            raise ValueError("Invalid source ledger ordering")
        if not isinstance(e.get("hash"),str) or not HEX.fullmatch(e["hash"]) or sha({k:v for k,v in e.items() if k!="hash"})!=e["hash"]:
            raise ValueError("Invalid source SHA chain")
        prev=e["hash"]

def valid_state(e:dict,streams:dict)->bool:
    state=e["state"]
    if not isinstance(state,dict) or set(state)!=set(STREAMS):return False
    for name in STREAMS:
        record=state[name]
        if not isinstance(record,dict) or set(record)!={"count","tip"}:return False
        count=record["count"];rows=streams[name]
        if type(count) is not int or count<0 or count>len(rows):return False
        if record["tip"]!=(rows[count-1]["hash"] if count else "GENESIS"):return False
    return True

def validate_checkpoint_chain(rows:list[dict],trust:dict,streams:dict)->None:
    if not isinstance(rows,list):raise ValueError("Checkpoint chain is not an array")
    prev="GENESIS";latest={}
    for i,e in enumerate(rows,1):
        if e.get("seq")!=i or e.get("prev")!=prev:
            raise ValueError("Broken checkpoint predecessor/sequence")
        verify_record(e,trust)
        if not valid_state(e,streams):raise ValueError("Unverifiable source-prefix state for checkpoint")
        last=latest.get(e["witness"])
        if last and any(e["state"][name]["count"]<last["state"][name]["count"] for name in STREAMS):
            raise ValueError("Checkpoint witness rollback")
        prev=e["hash"];latest[e["witness"]]=e

def remote(name:str)->list[dict]:
    url=BASE+name
    req=urllib.request.Request(url,headers={"User-Agent":"ROOT0-checkpoint-anchor/1"})
    with urllib.request.urlopen(req,timeout=20) as rsp:content=rsp.read()
    if len(content)>8_000_000:raise ValueError("Remote journal exceeds safe read limit")
    if content and not content.endswith(b"\n"):raise ValueError("Incomplete remote JSONL")
    return [json.loads(line) for line in content.decode("utf-8").splitlines() if line]

def anchored(path:Path=INBOX,trust:dict|None=None)->list[dict]:
    pinned=pins() if trust is None else trust
    received=[];seen=set()
    for item in sorted(path.glob("*.json")) if path.is_dir() else []:
        a=json.loads(item.read_text(encoding="utf-8"))
        if not isinstance(a,dict) or set(a)!={"schema","receiver","accepted_at","checkpoint"} or a["schema"]!="root0.checkpoint-anchor/1" or a["receiver"]!="DavidWise01/0root":
            raise ValueError("Invalid pinned checkpoint anchor file")
        e=a["checkpoint"]
        verify_record(e,pinned)
        if item.name!=e["hash"]+".json" or item.name in seen:
            raise ValueError("Anchor filename does not match signed checkpoint")
        seen.add(item.name);received.append(e)
    # Local anchors may arrive out of order across lanes; no quorum implied.
    return received

def receive(seq:int,expected_hash:str)->Path:
    if not pins():raise ValueError("No independent 0root keys pinned; receipt denied")
    auth=(os.environ.get("GITHUB_ACTIONS")=="true" and
          os.environ.get("GITHUB_REPOSITORY")=="DavidWise01/0root" and
          os.environ.get("GITHUB_REF")=="refs/heads/master" and
          os.environ.get("GITHUB_EVENT_NAME")=="workflow_dispatch" and
          os.environ.get("GITHUB_ACTOR_ID")=="148925959" and
          os.environ.get("GITHUB_WORKFLOW_REF","").endswith("/.github/workflows/checkpoint-anchor.yml@refs/heads/master"))
    if not auth:raise ValueError("Owner-authenticated Hallway workflow context required")
    if type(seq) is not int or seq<1 or not HEX.fullmatch(expected_hash):
        raise ValueError("Invalid signed checkpoint selection")
    trust=pins()
    streams={name:remote(path) for name,path in STREAMS.items()}
    for rows in streams.values():verify_source_log(rows)
    checkpoints=remote("checkpoints.jsonl")
    validate_checkpoint_chain(checkpoints,trust,streams)
    if seq>len(checkpoints):raise ValueError("Checkpoint sequence not present")
    checkpoint=checkpoints[seq-1]
    if checkpoint["hash"]!=expected_hash:raise ValueError("Offered checkpoint hash mismatch")
    import key_decisions
    if checkpoint["key_id"] in key_decisions.replay(key_decisions.read(key_decisions.LEDGER,trust),trust):
        raise ValueError("Hallway independent key BLOCK forbids new checkpoint acceptance")

    existing=anchored(trust=trust)
    if any(old["hash"]==expected_hash for old in existing):
        raise ValueError("Checkpoint already anchored")
    same_lane=[old for old in existing if old["witness"]==checkpoint["witness"]]
    if same_lane:
        recent=max(old["seq"] for old in same_lane)
        if checkpoint["seq"]<=recent:raise ValueError("Receiver anti-rollback: older or repeated sequence")
        last=max(same_lane,key=lambda x:x["seq"])
        if any(checkpoint["state"][k]["count"]<last["state"][k]["count"] for k in STREAMS):
            raise ValueError("Receiver anti-rollback: source snapshot regressed")
    target=INBOX/(expected_hash+".json")
    target.parent.mkdir(parents=True,exist_ok=True)
    body={"schema":"root0.checkpoint-anchor/1","receiver":"DavidWise01/0root",
          "accepted_at":dt.datetime.now(dt.timezone.utc).date().isoformat(),
          "checkpoint":checkpoint}
    with target.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(body,out,ensure_ascii=False,sort_keys=True,indent=2)
        out.write("\n")
    return target

def main()->int:
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="cmd",required=True)
    sub.add_parser("verify-local")
    cmd=sub.add_parser("receive")
    cmd.add_argument("--seq",type=int,required=True)
    cmd.add_argument("--hash",required=True)
    args=parser.parse_args()
    try:
        if args.cmd=="verify-local":
            import key_decisions
            trust=pins();blocked=key_decisions.replay(key_decisions.read(key_decisions.LEDGER,trust),trust)
            items=anchored(trust=trust)
            print(f"PASS / anchored={len(items)} / trusted public keys={len(trust)} / irreversibly blocked={len(blocked)}")
        else:print("CREATED VERIFIED ANCHOR:",receive(args.seq,args.hash))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print("HALTED: "+str(e),file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
