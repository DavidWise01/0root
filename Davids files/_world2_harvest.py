#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_world2_harvest.py — sweep Downloads for silicon-coding artifacts and vendor them into THE FOLD.

Discovers top-level *.html in Downloads, keeps only the ones whose title/name reads as
SILICON CODING (a tight keyword router — physics / World-I / legal / media are excluded),
dedupes " (N)" copies and anything already in fold.json, requires self-contained (0 external
refs), routes each to a World II domain, frames it (Code-Monkeys nav+seal via _world2_vendor.frame)
and wires it into fold.json.

  python _world2_harvest.py            # DRY: print the plan, touch nothing
  python _world2_harvest.py --go       # actually vendor + wire
"""
import json, os, re, sys
from _world2_vendor import frame

DL = r"C:\Users\Dave\Downloads"
W2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ud0", "world2")
GO = "--go" in sys.argv

# hard excludes — World-I physics/chem/attention, legal, media, data blobs
EXCLUDE = re.compile(r"""field|quark|gluon|lepton|boson|higgs|hawking|fermion|graviton|gravity|
 capacitor|inductor|\bdiode|breadboard|memristor|aromatic|orbital|spinor|casimir|isospin|
 metallic|covalent|nacl|\bbond\b|electron|proton|neutron|photon|exciton|hydrogen|deuterium|
 attention|jacobi|curvature|\blens|basin|hourglass|holograph|hamiltonian_|casimir|
 claim-|mcro|evidence|judgment|notice|order|invoice|receipt|auto owners|
 pulsar|entangled|spin.?ladder|torus.?district|lc.?tank|paper-0|encapsulated|concept.?cloud|
 encapsul|isospin|hepteract|hexeract|em_torus|linked_torus|nested_qft|nested_decoher|
 \.pdf|\.zip|\.png|\.jpg|\.jpeg|\.wav|\.epub|\.pt$|\.json$|\.txt$|\.py$|\.js$|\.go$|\.skill""",
 re.I | re.X)

# first match wins -> (appeal, domain_slug, accent, icon)
ROUTES = [
 (r"compiler|bytecode|assembl|opcode|mini.?comp|machine.?code", "SPAWN", "the-toolchain", "#7cfc00", "spawn"),
 (r"\bvm\b|virtual.?machine|register.?machine|stack.?machine|instruction.?set|\bisa\b", "SPAWN", "the-toolchain", "#39fc6b", "cheat"),
 (r"language|alphabet|grammar|lexer|parser|syntax|monoline|learn.?speak|\bcorpus\b|notation|glyph", "SPAWN", "the-toolchain", "#00f5ff", "glitch"),
 (r"\bbpe\b|token|vocab|byte.?pair|embedd?er", "GRIND", "the-epoch", "#ffd23f", "grind"),
 (r"ternary|\btrit|base.?3|radix|fractal.?tern", "CHEAT", "the-shortcut", "#7cfc00", "cheat"),
 (r"enigma|cipher|steganog|encrypt|crypto|side.?channel|air.?gap|airgap|numbers.?station|one.?time", "BOSS", "the-firewall", "#ff5a3c", "boss"),
 (r"merkle|\bhash\b|sha-?256|ed25519|\bseal\b|provenance|chain.?of.?custody", "LOOT", "the-mint", "#ffd23f", "loot"),
 (r"langton|cellular|automat|rule.?110|game.?of.?life|edge.?of.?chaos|\bca[_ -]", "GLITCH", "undefined-behavior", "#42ffb0", "grind"),
 (r"error.?correct|coding.?theory|hamming|qubit.?code|repetition.?code|five.?channel|five.?qubit", "BOSS", "the-gauntlet", "#ff5a3c", "boss"),
 (r"65536|network[_-]?4096|net65536|network_", "GRIND", "the-mainframe", "#9d00ff", "glitch"),
 (r"turing|imitation.?game|\blogical|boolean|logic.?gate|state.?machine|finite.?state|circuit", "CHEAT", "the-konami-code", "#ffd23f", "cheat"),
 (r"compress|huffman|entropy.?cod|\bpulse\b|3-?2-?1", "CO-OP", "the-sync", "#00f5ff", "coop"),
]

def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"

def title_of(html):
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

def route(text):
    for rx, ap, dom, acc, ico in ROUTES:
        if re.search(rx, text, re.I):
            return ap, dom, acc, ico
    return None

def main():
    db = json.load(open(os.path.join(W2, "fold.json"), encoding="utf-8"))
    have = {s["slug"] for s in db["spheres"]}
    dom_by_slug = {d["slug"]: d for a in db["appeals"] for d in a.get("domains", [])}
    ap_of = {d["slug"]: a["name"] for a in db["appeals"] for d in a.get("domains", [])}
    files = sorted(f for f in os.listdir(DL) if f.lower().endswith(".html"))
    plan, skipped = [], {"dup": 0, "exclude": 0, "noroute": 0, "external": 0, "have": 0}
    seen_base = set()
    for f in files:
        base = f[:-5]
        if re.search(r"\(\d+\)$", base):                 # " (1)" copies
            skipped["dup"] += 1; continue
        slug = slugify(base)
        if slug in have or slug in seen_base:
            skipped["have"] += 1; continue
        if EXCLUDE.search(f):
            skipped["exclude"] += 1; continue
        path = os.path.join(DL, f)
        try:
            html = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        title = title_of(html)
        r = route(title + " " + f)
        if not r:
            skipped["noroute"] += 1; continue
        if len(re.findall(r'(?:src|href)="https?://|fetch\(|googleapis|cdn\.', html)) > 0:
            skipped["external"] += 1; continue
        ap, dom, acc, ico = r
        seen_base.add(slug)
        plan.append({"file": f, "slug": slug, "title": title or base, "appeal": ap,
                     "domain": dom, "accent": acc, "icon": ico})
    print(f"CANDIDATES: {len(plan)}   skipped: {skipped}")
    from collections import Counter
    bydom = Counter(p["domain"] for p in plan)
    print("by domain:", dict(bydom))
    for p in plan[:80]:
        print(f"  {p['appeal']:8}/{p['domain']:20} {p['slug'][:34]:34} :: {p['title'][:44]}")
    if len(plan) > 80:
        print(f"  … and {len(plan)-80} more")
    if not GO:
        print("\nDRY RUN — re-run with --go to vendor these.")
        return
    # vendor for real
    top = {s["slug"]: s for s in db["spheres"]}
    done = 0
    for p in plan:
        html = open(os.path.join(DL, p["file"]), encoding="utf-8", errors="replace").read()
        dom = dom_by_slug.get(p["domain"])
        dtitle = dom["title"] if dom else p["domain"]
        ctx = {"ACCENT": p["accent"], "APPEAL": p["appeal"], "DOMAIN": dtitle}
        open(os.path.join(W2, p["slug"] + ".html"), "w", encoding="utf-8").write(frame(html, ctx))
        title = p["title"][:40]
        kicker = "vendored from David's corpus — a silicon-coding instrument"
        blurb = f"David's own artifact — {p['title']} — vendored into THE FOLD (self-contained, Code-Monkeys framed)."
        rec = {"slug": p["slug"], "title": title, "kicker": kicker, "accent": p["accent"], "blurb": blurb}
        if p["slug"] in top: top[p["slug"]].update(rec)
        else: db["spheres"].append(rec)
        if dom is not None:
            dom.setdefault("spheres", [])
            nest = {"slug": p["slug"], "title": title, "accent": p["accent"], "icon": p["icon"], "kicker": kicker}
            ex = next((x for x in dom["spheres"] if x.get("slug") == p["slug"]), None)
            if ex: ex.update(nest)
            else: dom["spheres"].append(nest)
        done += 1
    db["counts"]["spheres"] = len(db["spheres"])
    db["counts"]["spheres_built"] = sum(len(d.get("spheres", [])) for a in db["appeals"] for d in a["domains"])
    json.dump(db, open(os.path.join(W2, "fold.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nVENDORED {done} spheres. total: {db['counts']['spheres']} sealed / {db['counts']['spheres_built']} seated")

if __name__ == "__main__":
    main()
