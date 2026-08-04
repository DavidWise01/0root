#!/usr/bin/env python3
# Reality-wide slug scan for World II — THE FOLD.
# Unions every slug source that actually exists in git reality, not just the generator source:
#   1) generator _world2_spheres.py  (SPHERES slug literals)
#   2) sealed ud0/world2/fold.json    (top-level spheres[] + nested appeals[].domains[].spheres[])
#   3) on-disk HTML filenames in ud0/world2 AND the agent-0root mirror  (the-*.html)
# Usage: python _reality_scan.py kw1 kw2 ...    (prints, per keyword, every matching slug across ALL sources)
#        python _reality_scan.py --slugs a b    (checks EXACT slugs -> TAKEN/free across the union)
import re, os, json, sys, glob

GEN = r"C:\Davids files\_world2_spheres.py"
FOLD = r"C:\Davids files\ud0\world2\fold.json"
HTML_DIRS = [r"C:\Davids files\ud0\world2", r"C:\root0-greenpaper-repo\agent-0root\static\world2"]

def gen_slugs():
    try:
        t = open(GEN, encoding="utf-8").read()
        return set(re.findall(r'"slug":"([^"]+)"', t))
    except Exception:
        return set()

def fold_slugs():
    s = set()
    try:
        d = json.load(open(FOLD, encoding="utf-8"))
        for sp in d.get("spheres", []):
            s.add(sp.get("slug"))
        for a in d.get("appeals", []):
            for dm in a.get("domains", []):
                for sp in dm.get("spheres", []):
                    s.add(sp.get("slug") if isinstance(sp, dict) else sp)
    except Exception:
        pass
    return {x for x in s if x}

def html_slugs():
    s = set()
    for hd in HTML_DIRS:
        for f in glob.glob(os.path.join(hd, "the-*.html")):
            s.add(os.path.splitext(os.path.basename(f))[0])
    return s

def union():
    g, f, h = gen_slugs(), fold_slugs(), html_slugs()
    return g | f | h, g, f, h

def main():
    args = sys.argv[1:]
    allslugs, g, f, h = union()
    print(f"[reality] union={len(allslugs)} slugs  (gen={len(g)} fold={len(f)} html={len(h)})")
    if not args:
        return
    if args[0] == "--slugs":
        for s in args[1:]:
            where = []
            if s in g: where.append("gen")
            if s in f: where.append("fold")
            if s in h: where.append("html")
            print(f"  {s:34} {'TAKEN['+','.join(where)+']' if where else 'free'}")
        return
    for kw in args:
        base = kw.split("-")[0]
        hits = sorted(x for x in allslugs if base in x)
        print(f"  {kw:22} -> {hits if hits else 'FREE'}")

if __name__ == "__main__":
    main()
