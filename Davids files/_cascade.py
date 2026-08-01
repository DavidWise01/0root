# -*- coding: utf-8 -*-
"""
_cascade.py — the ROOT0 attribution cascade. Run after adding ANY new repo/sphere.

Two idempotent steps, in order:
  1. _dlw_sweep.py   — every ud0-sphere repo gets README + .attribution + <slug>.dlw
  2. _dlw_chain.py   — every .dlw seal is tethered into the append-only hash-chain
                       (new repos append at the tip; existing links never change)

  python _cascade.py            # dry: generate/extend locally, report
  python _cascade.py --push     # also commit + push every changed repo

This is the "auto in the cascade" guarantee: a new repo is sealed AND chained by
one command, no repo left untethered. Safe to re-run.
"""
import os, sys, subprocess

ROOT = r"C:\Davids files"
PUSH = "--push" in sys.argv
PY = sys.executable

def run(script):
    args = [PY, os.path.join(ROOT, script)] + (["--push"] if PUSH else [])
    print(f"\n===== {script} {'--push' if PUSH else '(dry)'} =====", flush=True)
    return subprocess.run(args, cwd=ROOT).returncode

rc1 = run("_dlw_sweep.py")     # seal
rc2 = run("_dlw_chain.py")     # tether
rc3 = run("_i13_consensus.py") # universal consensus of every .agent that learned I-13
print(f"\ncascade done · seal rc={rc1} · chain rc={rc2} · i13-consensus rc={rc3}")
if not PUSH:
    print("dry run — re-run with --push to commit + push.")
print("verify the chain any time:  python _dlw_chain.py --verify")
print("read the agents' consensus:  .agents/I13-CONSENSUS.md")
