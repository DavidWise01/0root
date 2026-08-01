#!/usr/bin/env python3
# _i13_teach.py — teach the WHOLE World II - THE FOLD the I-13 v2 stack.
# David: "make sure all appeals/domains/spheres learn this."
#
# I-13 v2 is a frozen (2026-08-01), self-sha-sealed four-plane agent stack over a
# thirteen-symbol language: THE TWELVE (12 AST operants, each attributed), the
# IVM-13-S machine with the law `net = binds - k` (br targets a DEPTH not an
# address, so validation is one linear pass), and CORTEX's five zero-parameter
# rules (veto, -I, depth, idempotence, address). The narrow claim: deterministic
# zero-parameter components guarantee structural properties no model at this scale
# reaches; learned recurrent state is not a stack.
#
# This script is IDEMPOTENT. It:
#   1. vendors the canonical spec json into ud0/world2/ (single source of truth),
#   2. adds a top-level `i13` block to fold.json (the spec's own words + declared sha),
#   3. stamps a compact `learned` marker onto EVERY appeal, domain, sphere, keeper.
# Run _dlw_fold.py afterwards to fold the new knowledge into ROOT_0.

import json, os, hashlib, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
W2 = os.path.join(HERE, "ud0", "world2")
SRC = os.path.join(HERE, "i-13", "i-13 v2", "i13-v2", "01-frozen-spec", "i13-stack-v2.json")
MIRROR = r"C:\root0-greenpaper-repo\agent-0root\static\world2"

# THE VOLUME — David's I-13 voxel: a stylometric measuring instrument that scores
# texts on three independent axes (Heaps beta, the "I" referent, voiced fraction)
# and bins them into a 3x3x3 cube. The "I" axis IS an I-13 operant (the referent).
VOX_HTML = os.path.join(HERE, "i-13", "i13 voxel", "the-volume-v1.html")
VOX_IDX  = os.path.join(HERE, "i-13", "i13 voxel", "the-volume-index-v1.json")

spec = json.load(open(SRC, encoding="utf-8"))
declared_sha = spec.get("sha256")  # 64881ebf... — the spec's own self-declared seal

# ── read the voxel index (its own words, its own self-declared sha) ──
vox = None
if os.path.exists(VOX_IDX):
    vidx = json.load(open(VOX_IDX, encoding="utf-8"))
    vox = {
        "name": vidx.get("name", "THE VOLUME"),
        "version": vidx.get("version", "1.0"),
        "built": vidx.get("built", "2026-08-01"),
        "sha256": vidx.get("sha256"),                 # the voxel's own self-declared seal
        "axes": [{"id": a.get("id"), "label": a.get("label"), "desc": a.get("desc")}
                 for a in vidx.get("axes", [])],
        "independence": vidx.get("independence", {}),  # all pairwise |r| < 0.4
        "effective_dims": vidx.get("effective_dims"),
        "texts": len(vidx.get("texts", [])),
        "cells_occupied": vidx.get("cells_occupied"),
        "cells_total": vidx.get("cells_total"),
        "method": vidx.get("method", ""),
        "open_questions": vidx.get("open_questions", []),
        "viewer": "the-volume-v1.html",
        "index": "the-volume-index-v1.json",
        "note": ("David's I-13 voxel: three INDEPENDENT stylometric axes (all pairwise |r| < 0.4) "
                 "over real texts. The 'I' axis is the I-13 referent operant. Both viewer and index "
                 "are vendored beside fold.json; bins are FROZEN at v1.0 so later texts stay comparable."),
    }

# ── the canonical block, in I-13's own words ──
i13_block = {
    "spec": "I-13",
    "version": spec.get("version", "2.0"),
    "frozen": spec.get("frozen", "2026-08-01"),
    "sha256": declared_sha,                    # the spec's self-declared canonical seal
    "one_line": spec.get("one_line", ""),
    "law": spec.get("machine", {}).get("law", "net = binds - k"),
    "planes": 4,
    "symbols": 13,
    "twelve": [t[0] if isinstance(t, list) else t for t in spec.get("twelve", [])],
    "cortex_rules": [r[0] if isinstance(r, list) else r for r in spec.get("rules", [])],
    "claim": ("deterministic zero-parameter components guarantee structural properties "
              "no model at this scale reaches; learned recurrent state is not a stack"),
    "br_rule": "br targets a DEPTH, never an address — so validation is one linear pass (net = binds - k)",
    "vendored": "i13-stack-v2.json",
    "note": ("David's frozen I-13 v2 stack, taught to the whole FOLD. The full spec is vendored "
             "beside fold.json; every appeal, domain, sphere and keeper carries the `learned` marker."),
}
if vox is not None:
    i13_block["voxel"] = vox   # THE VOLUME — the I-13 voxel measuring instrument

# compact ASCII marker every node carries (fold.json is ensure_ascii=False, but keep the
# .dlw-facing text ASCII-clean to be safe with the sealer)
MARK = ("I-13 v2.0 | net = binds - k | 4 planes, 13 symbols, 12 operants, 5 cortex rules | "
        "sha " + (declared_sha[:8] if declared_sha else "?"))

# ── 1. vendor the spec + the voxel into the world (single source of truth) ──
for dst in (W2, MIRROR):
    try:
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(SRC, os.path.join(dst, "i13-stack-v2.json"))
        if os.path.exists(VOX_HTML):
            shutil.copy2(VOX_HTML, os.path.join(dst, "the-volume-v1.html"))
        if os.path.exists(VOX_IDX):
            shutil.copy2(VOX_IDX, os.path.join(dst, "the-volume-index-v1.json"))
    except OSError as e:
        print("  (vendor skip", dst, ":", e, ")")

# ── 2 + 3. teach fold.json ──
fp = os.path.join(W2, "fold.json")
db = json.load(open(fp, encoding="utf-8"))
db["i13"] = i13_block

taught = {"appeals": 0, "domains": 0, "spheres": 0, "keepers": 0}
for a in db.get("appeals", []):
    a["learned"] = MARK; taught["appeals"] += 1
    for dm in a.get("domains", []):
        dm["learned"] = MARK; taught["domains"] += 1
        for sp in dm.get("spheres", []):
            sp["learned"] = MARK; taught["spheres"] += 1
for sp in db.get("spheres", []):
    sp["learned"] = MARK  # top-level spheres[] (counted via nested to avoid double-count)
for k in db.get("keepers", []):
    if isinstance(k, dict): k["learned"] = MARK; taught["keepers"] += 1

# also mark top-level spheres[] that aren't seated in a domain (the keeper-synths)
seated = set()
for a in db.get("appeals", []):
    for dm in a.get("domains", []):
        for sp in dm.get("spheres", []): seated.add(sp.get("slug"))
for sp in db.get("spheres", []):
    if sp.get("slug") not in seated: taught["spheres"] += 0  # already marked above

json.dump(db, open(fp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# mirror fold.json too
try:
    shutil.copy2(fp, os.path.join(MIRROR, "fold.json"))
except OSError:
    pass

top_spheres = len(db.get("spheres", []))
print("TAUGHT I-13 v2 to the FOLD:")
print(f"  top-level i13 block added (sha {declared_sha[:12]}..., law '{i13_block['law']}')")
print(f"  learned marker on: {taught['appeals']} appeals, {taught['domains']} domains, "
      f"{taught['spheres']} seated spheres (+{top_spheres} top-level spheres[]), {taught['keepers']} keepers")
print(f"  vendored i13-stack-v2.json into world2 + mirror")
if vox is not None:
    print(f"  + VOXEL 'THE VOLUME' v{vox['version']} registered (sha {str(vox['sha256'])[:12]}..., "
          f"{vox['texts']} texts, {vox['cells_occupied']}/{vox['cells_total']} cells, "
          f"eff.dims {vox['effective_dims']}); viewer + index vendored")
print(f"  marker: {MARK}")
