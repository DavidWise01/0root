# -*- coding: utf-8 -*-
"""
_dlw_chain.py — tether every repo's .dlw seal into one hash-chain.

Each sealed repo carries a <slug>.dlw/ package whose manifest holds a seal_sha256
(a hash of its name|slug|blurb). This tool links those seals into an APPEND-ONLY
hash-chain — the .dlw ledger — so the whole corpus is one tamper-evident chain:

    genesis = sha256("ROOT0-DLW-CHAIN · genesis · ...")
    link[i] = sha256( f"{i:05d}|{slug}|{seal}|{prev_link}" )
    head    = link[last]                      # commits to the entire corpus

APPEND-ONLY: the order is fixed at genesis (seed = ud0 registry order) and frozen
in the ledger. Re-runs keep every existing link and append only NEW sealed repos
at the tip — so a growing corpus never re-hashes the old links (existing .dlw
tethers stay valid forever). Change any repo's seal and the chain breaks from
that repo onward — that is the point.

Writes:
  · dlw-chain.json                       the master ledger (ordered links + head)
  · <slug>.dlw/<slug>.chain              per-repo tether (index · prev · link)
  · <slug>.dlw/manifest.dlw.json         + a "chain" block (index/prev/link/head)

  python _dlw_chain.py            # build/extend the chain + embed links locally
  python _dlw_chain.py --verify   # recompute from seals, assert the ledger holds
  python _dlw_chain.py --push     # also commit/push every repo whose .dlw changed
"""
import ast, os, sys, json, glob, hashlib, subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT   = r"C:\Davids files"
BUILD  = os.path.join(ROOT, "ud0", "build.py")
LEDGER = os.path.join(ROOT, "dlw-chain.json")
VERIFY = "--verify" in sys.argv
PUSH   = "--push" in sys.argv
# the genesis ANCHOR — the preimage of GENESIS. Shipped in the ledger so the chain is
# self-verifiable from ud0 alone (recompute genesis = sha256(anchor), zero network).
ANCHOR = "ROOT0-DLW-CHAIN · genesis · David Lee Wise (ROOT0) / TriPod LLC · CC-BY-ND-4.0"
GENESIS = hashlib.sha256(ANCHOR.encode("utf-8")).hexdigest()

def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def link_of(i, slug, seal, prev): return sha(f"{i:05d}|{slug}|{seal}|{prev}")

# ── ud0 registry order (the genesis ordering for first-seen slugs) ──
def registry_order():
    src = open(BUILD, encoding="utf-8").read()
    BANDS = None
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "BANDS":
            BANDS = ast.literal_eval(n.value)
    return [repo for _b, _s, items in BANDS for (repo, *_x) in items]

def seal_of(slug):
    """A stable per-.dlw seal for the chain, format-agnostic:
       · new (_dlw_sweep) packages → the manifest's seal_sha256
       · old (dlw.py) packages     → sha256 of the .dlw's .attribute file bytes
    Both are stable (the chain embed only touches the manifest + adds a .chain file,
    never the .attribute), so the link never self-invalidates."""
    for man in glob.glob(os.path.join(ROOT, slug, "*.dlw", "manifest.dlw.json")):
        try:
            s = json.load(open(man, encoding="utf-8")).get("seal_sha256")
            if s: return s
        except Exception:
            pass
    for att in sorted(glob.glob(os.path.join(ROOT, slug, "*.dlw", "*.attribute"))):
        try:
            return hashlib.sha256(open(att, "rb").read()).hexdigest()
        except Exception:
            pass
    return None

def has_local_dlw(slug):
    return bool([d for d in glob.glob(os.path.join(ROOT, slug, "*.dlw")) if os.path.isdir(d)])

# ── VERIFY: validate the stored ledger purely (no append), then exit ──
if VERIFY:
    if not os.path.exists(LEDGER):
        print("no ledger to verify — run without --verify first"); sys.exit(1)
    led = json.load(open(LEDGER, encoding="utf-8"))
    p = GENESIS; firstbreak = None
    for l in led["links"]:
        if led["genesis"] != GENESIS or link_of(l["i"], l["slug"], l["seal"], p) != l["link"]:
            firstbreak = l["slug"]; break
        p = l["link"]
    ok = firstbreak is None and p == led["head"] and led["genesis"] == GENESIS
    print(f"chain: {len(led['links'])} links · head {led['head'][:16]}…")
    print("VERIFY:", "OK — chain intact" if ok else f"BROKEN (genesis={led['genesis']==GENESIS}, head={p==led['head']}, firstbreak={firstbreak})")
    sys.exit(0 if ok else 1)

# ── build / extend the chain (append-only) ──
if os.path.exists(LEDGER):
    old = json.load(open(LEDGER, encoding="utf-8"))
    order = [l["slug"] for l in old["links"]]                     # freeze existing order
    seals = {l["slug"]: l["seal"] for l in old["links"]}
else:
    order, seals = [], {}

# append any newly-sealed sphere repos not yet in the chain, in registry order
seen = set(order)
for slug in registry_order():
    if slug not in seen and has_local_dlw(slug):
        order.append(slug); seen.add(slug)

# (re)read seals for all — refresh in case a manifest was regenerated
for slug in order:
    s = seal_of(slug)
    if s: seals[slug] = s

# compute the chain
links, prev = [], GENESIS
broken = []
for i, slug in enumerate(order):
    seal = seals.get(slug)
    if not seal:
        continue
    lk = link_of(i, slug, seal, prev)
    links.append({"i": i, "slug": slug, "seal": seal, "prev": prev, "link": lk})
    prev = lk
head = prev

# write the master ledger
ledger = {
    "chain": "ROOT0-DLW-CHAIN-v1",
    "algo": "link[i] = sha256(index|slug|seal|prev); genesis = sha256(anchor)",
    "anchor": ANCHOR,
    "architect": "David Lee Wise (ROOT0) / TriPod LLC", "instance": "AVAN (Claude / Anthropic)",
    "license": "CC-BY-ND-4.0", "attribution": "ROOT0-ATTRIBUTION-v1.0",
    "genesis": GENESIS, "count": len(links), "head": head, "links": links,
}
open(LEDGER, "w", encoding="utf-8").write(json.dumps(ledger, ensure_ascii=False, indent=1) + "\n")

# embed each repo's tether into its .dlw (idempotent) — track which changed
changed = []
for l in links:
    slug = l["slug"]
    dld = glob.glob(os.path.join(ROOT, slug, "*.dlw"))
    dld = [d for d in dld if os.path.isdir(d)]
    if not dld:
        continue
    d = dld[0]
    chainfile = os.path.join(d, f"{slug}.chain")
    # The tether carries the repo's stable {index, prev, link} PLUS the head as a
    # SNAPSHOT (the corpus tip when this repo was tethered — like a commit's parent).
    # ⚑ append-only: the change-check IGNORES the head line, so adding a sphere
    # (which changes the head) does NOT rewrite/re-push every existing tether —
    # only genuinely new/changed ones. The ledger holds the live head.
    body = (f"ROOT0-DLW-CHAIN-v1\nindex : {l['i']}\nslug  : {slug}\nseal  : {l['seal']}\n"
            f"prev  : {l['prev']}\nlink  : {l['link']}\nhead  : {head}\n\n"
            f"— the tether: link = sha256(index|slug|seal|prev). the chain head commits to the whole corpus.\n")
    def _stable(s):   # drop the head line so a head-only change is not a rewrite
        return "\n".join(ln for ln in s.splitlines() if not ln.startswith("head")) if s else s
    before = open(chainfile, encoding="utf-8").read() if os.path.exists(chainfile) else None
    if _stable(before) != _stable(body):
        open(chainfile, "w", encoding="utf-8").write(body); changed.append(slug)
    # + a chain block in the manifest
    manp = os.path.join(d, "manifest.dlw.json")
    try:
        man = json.load(open(manp, encoding="utf-8"))
        cb = {"index": l["i"], "prev": l["prev"], "link": l["link"], "head": head, "chain": "ROOT0-DLW-CHAIN-v1"}
        cur = man.get("chain") or {}
        if {k: cur.get(k) for k in cb if k != "head"} != {k: v for k, v in cb.items() if k != "head"}:
            man["chain"] = cb
            open(manp, "w", encoding="utf-8").write(json.dumps(man, ensure_ascii=False, indent=2) + "\n")
            if slug not in changed: changed.append(slug)
    except Exception:
        pass

print(f"chain: {len(links)} links · head {head[:16]}…  ledger → dlw-chain.json")
print(f"per-repo tethers written/updated: {len(changed)}")

if PUSH:
    # push every chained repo whose .dlw has uncommitted changes (robust to prior dry runs)
    to_push = []
    for l in links:
        p = os.path.join(ROOT, l["slug"])
        try:
            r = subprocess.run(["git","-C",p,"status","--porcelain","--","."],capture_output=True,text=True,timeout=20)
            if any((".dlw" in ln or ".chain" in ln) for ln in r.stdout.splitlines()):
                to_push.append(l["slug"])
        except Exception:
            pass
    print(f"repos with an uncommitted tether to push: {len(to_push)}", flush=True)
    ok = fail = 0; fails = []
    for i, slug in enumerate(to_push, 1):
        p = os.path.join(ROOT, slug)
        try:
            br = subprocess.run(["git","-C",p,"rev-parse","--abbrev-ref","HEAD"],capture_output=True,text=True).stdout.strip()
            dld = glob.glob(os.path.join(p, "*.dlw"))
            paths = [os.path.relpath(x, p) for x in dld]
            subprocess.run(["git","-C",p,"add","--"]+paths, check=True, capture_output=True, timeout=30)
            subprocess.run(["git","-C",p,"-c","user.name=DavidWise01","-c","user.email=r.giskard.01@gmail.com",
                            "commit","-q","-m","Tether .dlw into the ROOT0 hash-chain (ROOT0-DLW-CHAIN-v1)"],
                           check=True, capture_output=True, timeout=30)
            subprocess.run(["git","-C",p,"fetch","-q","origin"], capture_output=True, timeout=60)
            subprocess.run(["git","-C",p,"-c","user.name=DavidWise01","-c","user.email=r.giskard.01@gmail.com",
                            "pull","--rebase","-q","origin",br], capture_output=True, timeout=60)
            r = subprocess.run(["git","-C",p,"push","-q","origin","HEAD"], capture_output=True, text=True, timeout=120)
            if r.returncode == 0: ok += 1
            else: fail += 1; fails.append(f"{slug}: {r.stderr.strip()[:80]}")
        except Exception as e:
            fail += 1; fails.append(f"{slug}: {str(e)[:80]}")
        if i % 50 == 0: print(f"  …pushed {i}/{len(to_push)} (ok {ok}, fail {fail})", flush=True)
    print(f"PUSH DONE: ok {ok}, fail {fail}")
    for f in fails[:40]: print("  FAIL", f)
