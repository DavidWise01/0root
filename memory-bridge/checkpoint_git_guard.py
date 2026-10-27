#!/usr/bin/env python3
"""Hallway Git-parent guard: preserve independently anchored files and pinned keys.
Runs on push with fetch-depth=2. Does not protect against force-push bypass.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PIN="memory-bridge/trust/checkpoint-key-pins.json"
PREFIX="memory-bridge/checkpoints/"
DECISIONS="memory-bridge/trust/key-decisions.jsonl"

def git(*args)->bytes:
    p=subprocess.run(["git",*args],cwd=ROOT,capture_output=True)
    if p.returncode!=0:raise ValueError("Missing Git history needed for append audit")
    return p.stdout

def previous(path:str)->bytes:
    return git("show","HEAD^:"+path)

def check()->None:
    raw=previous(PIN)
    old=json.loads(raw);now=json.loads((ROOT/PIN).read_bytes())
    original=old.get("pins");current=now.get("pins")
    if old.get("schema")!=now.get("schema") or not isinstance(original,list) or not isinstance(current,list):
        raise ValueError("Untrusted or changed pinned trust registry")
    if len(current)<len(original) or current[:len(original)]!=original:
        raise ValueError("Existing independent witness keys removed or rewritten")
    paths=git("ls-tree","-r","--name-only","HEAD^","--",PREFIX).decode().splitlines()
    for path in paths:
        if not path.startswith(PREFIX) or not path.endswith(".json"):continue
        file=ROOT/path
        if not file.is_file() or file.read_bytes()!=previous(path):
            raise ValueError("Previously anchored checkpoint deleted or rewritten: "+path)
    print(f"APPEND PASS / prior Hallway anchors={len(paths)} / retained trust pins={len(original)}")

if __name__=="__main__":
    try:check()
    except (ValueError,OSError,json.JSONDecodeError) as e:
        print("HALTED: "+str(e),file=sys.stderr);raise SystemExit(1)
