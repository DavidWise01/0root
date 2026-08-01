#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_dlw_fold.py — THE .dlw.fold SEAL TOOL (WORLD II · THE FOLD).

World I (MIRROR) seals into an append-only linear CHAIN (dlw-chain.json). World II
FOLDS: every inhabitant's birth-seal folds pairwise up a Merkle tree to a single
ROOT_0 hash — "4096 folded to 0". Each `.dlw.fold` sidecar carries its own MERKLE
PROOF back to ROOT_0, so one file verifies itself (Cameron's line: one file carries
its own proof). Re-runnable: the fold root is the CURRENT commitment to all of World
II and updates as the world grows, until World II is itself sealed.

Reads ud0/world2/fold.json (the World II DB). Writes:
  - ud0/world2/fold-chain.json      (the ledger: anchor, genesis, leaves, ROOT_0)
  - ud0/world2/<slug>.dlw.fold      (per-inhabitant seal + self-verifying proof)
  - updates fold.json with fold_root + per-item seals.
Read-only otherwise. Run: python _dlw_fold.py
"""
import hashlib, json, os, re, datetime

ROOT = r"C:\Davids files"
W2 = os.path.join(ROOT, "ud0", "world2")
FOLD_ANCHOR = "0ROOT.AI//THE-FOLD//4096->0//David Lee Wise (ROOT0)//with AVAN"

def h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "x"

def seal_of(name, slug, blurb):
    """the birth-certificate seal — same formula as World I's .dlw (name|slug|blurb)."""
    return h(f"{name}|{slug}|{blurb}")

def merkle_levels(leaves):
    """bottom-up levels; odd node duplicates itself. levels[0]=leaves, levels[-1]=[root]."""
    if not leaves:
        return [[h(FOLD_ANCHOR)]]
    levels = [leaves[:]]
    cur = leaves[:]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(h(a + b))
        levels.append(nxt)
        cur = nxt
    return levels

def proof_for(index, levels):
    proof, idx = [], index
    for lvl in levels[:-1]:
        sib = idx ^ 1
        sh = lvl[sib] if sib < len(lvl) else lvl[idx]   # duplicated-last
        proof.append({"h": sh, "side": "R" if idx % 2 == 0 else "L"})
        idx //= 2
    return proof

def verify(seal, proof, root):
    x = seal
    for p in proof:
        x = h(x + p["h"]) if p["side"] == "R" else h(p["h"] + x)
    return x == root

# ── gather the current World II inhabitants from fold.json ──
db = json.load(open(os.path.join(W2, "fold.json"), encoding="utf-8"))
items = []   # (kind, name, slug, blurb)
for s in db.get("spheres", []):
    items.append(("sphere", s["title"], slugify(s["slug"].replace("../", "")), s.get("blurb", "")))
for k in db.get("keepers", []):
    items.append(("keeper", k["name"], slugify(k["name"]), k.get("role", "")))

leaves = [seal_of(name, slug, blurb) for (_kind, name, slug, blurb) in items]
levels = merkle_levels(leaves)
root = levels[-1][0]            # ROOT_0 — the fold
genesis = h(FOLD_ANCHOR)
today = datetime.date.today().isoformat()

# ── per-inhabitant .dlw.fold sidecars (self-verifying) ──
ledger_leaves = []
for i, ((kind, name, slug, blurb), seal) in enumerate(zip(items, leaves)):
    proof = proof_for(i, levels)
    assert verify(seal, proof, root), f"proof failed for {slug}"
    fold = {
        "schema": "dlw.fold/1", "world": "II", "kind": kind,
        "name": name, "slug": slug, "seal": seal, "index": i,
        "algo": "sha256(name|slug|blurb) + sha256 merkle-fold",
        "anchor": FOLD_ANCHOR, "genesis": genesis,
        "proof": proof, "folded_to": "ROOT_0", "root": root,
        "verify": "fold seal up the proof (R: h(x+sib), L: h(sib+x)) -> root",
        "sealed": today, "author": "David Lee Wise / ROOT0 / TriPod LLC",
    }
    open(os.path.join(W2, f"{slug}.dlw.fold"), "w", encoding="utf-8").write(
        json.dumps(fold, indent=2, ensure_ascii=False))
    ledger_leaves.append({"index": i, "kind": kind, "name": name, "slug": slug, "seal": seal})

# ── the ledger ──
ledger = {
    "schema": "fold-chain/1", "world": "II", "name": "THE FOLD",
    "algo": "sha256(name|slug|blurb) folded pairwise (merkle) to a single root",
    "anchor": FOLD_ANCHOR, "genesis": genesis,
    "folded_to": "ROOT_0", "root": root, "count": len(leaves), "sealed": today,
    "note": "Every World II inhabitant folds to ROOT_0. Live: the root updates as the world grows, until World II is sealed. Each <slug>.dlw.fold carries its own proof to this root.",
    "leaves": ledger_leaves,
    "author": "David Lee Wise / ROOT0 / TriPod LLC",
}
open(os.path.join(W2, "fold-chain.json"), "w", encoding="utf-8").write(
    json.dumps(ledger, indent=2, ensure_ascii=False))

# ── stamp the DB so the hub can show the fold root ──
db["fold_root"] = root
db["genesis"] = genesis
seal_by_slug = {L["slug"]: L["seal"] for L in ledger_leaves}
for s in db.get("spheres", []):
    s["seal"] = seal_by_slug.get(slugify(s["slug"].replace("../", "")))
for k in db.get("keepers", []):
    k["seal"] = seal_by_slug.get(slugify(k["name"]))
json.dump(db, open(os.path.join(W2, "fold.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"SEALED .dlw.fold — {len(leaves)} inhabitants folded to ROOT_0")
for L in ledger_leaves:
    print(f"  [{L['index']}] {L['kind']:7} {L['slug']:26} {L['seal'][:16]}…")
print(f"ROOT_0 = {root}")
print(f"genesis = {genesis[:16]}…  ·  every proof self-verified ✓")
print(f"wrote fold-chain.json + {len(leaves)} <slug>.dlw.fold + stamped fold.json")
