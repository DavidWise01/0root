#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_world2_vendor.py — VENDOR David's existing self-contained artifacts into WORLD II · THE FOLD.

Some of David's Downloads pages are already complete silicon-coding instruments (the same
family as i13-language / i13-factory). Rather than rebuild them, we bring the real thing in:
inject the Code-Monkeys top-nav + scanline + seal footer, then wire the sphere into fold.json
(top-level spheres[] for the .dlw.fold seal + its domain's nested spheres[] for the hub).
Only touches self-contained files (verified 0 external refs). Re-runnable.

Run: python _world2_vendor.py    then:  python _dlw_fold.py   (reseal)
"""
import json, os, re

DL = r"C:\Users\Dave\Downloads"
W2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ud0", "world2")

CM_CSS = """
.cm-scan{position:fixed;inset:0;z-index:40;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0,transparent 2px,rgba(0,0,0,.16) 3px)}
.cm-top{position:fixed;top:0;left:0;right:0;z-index:99999;display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 14px;background:rgba(4,7,4,.92);border-bottom:3px solid #255c2c;font-family:ui-monospace,monospace;font-weight:700;font-size:11px;letter-spacing:.5px;color:#39fc6b;backdrop-filter:blur(3px)}
.cm-top a{color:#39fc6b;text-decoration:none}.cm-top a:hover{color:#ffd23f}.cm-top .sl{color:%(ACCENT)s}
.cm-seal{font-family:ui-monospace,monospace;font-size:11px;color:#4c7a54;text-align:center;padding:16px;border-top:2px solid #255c2c;margin-top:30px;position:relative;z-index:20}
"""
CM_NAV = ('<div class="cm-scan"></div><div class="cm-top">'
          '<a href="./">&#9664; THE FOLD</a>'
          '<span>0ROOT.AI // WORLD II &middot; %(APPEAL)s &middot; %(DOMAIN)s</span>'
          '<span class="sl">&#9670; .dlw.fold</span></div><div style="height:42px"></div>')
CM_SEAL = ('<div class="cm-seal">&#9670; sealed .dlw.fold &rarr; ROOT_0 &middot; a sphere of %(DOMAIN)s '
           '&middot; vendored from David&rsquo;s corpus &middot; David Lee Wise (ROOT0), with AVAN</div>')

def frame(html, ctx):
    # inject CM CSS before the first </style>
    html = re.sub(r'</style>', (CM_CSS % ctx) + '</style>', html, count=1)
    # inject the nav right after the first <body ...>
    html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + (CM_NAV % ctx), html, count=1)
    # inject the seal before the LAST </body>
    i = html.rfind('</body>')
    if i != -1:
        html = html[:i] + (CM_SEAL % ctx) + html[i:]
    return html

VENDOR = [
 {"src":"machine-corpus-13.html","slug":"machine-corpus-13","title":"THE MACHINE CORPUS",
  "appeal_name":"SPAWN","domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#39fc6b","icon":"cheat",
  "kicker":"I and the twelve — the thirteen the machine speaks",
  "blurb":"David's I-13 corpus itself: one letter I plus twelve forms = the thirteen the machine speaks. The source study behind the whole silicon world."},
 {"src":"mini_compiler.html","slug":"mini-compiler","title":"THE MINI-COMPILER",
  "appeal_name":"SPAWN","domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#7cfc00","icon":"spawn",
  "kicker":"your words → the machine's jumps",
  "blurb":"a real mini-compiler — turns plain words into the machine's bytes and jumps. The compile step of I-13, made touchable."},
 {"src":"bpe.html","slug":"bpe","title":"BPE — THE VOCABULARY",
  "appeal_name":"GRIND","domain_title":"THE EPOCH","domain_slug":"the-epoch","accent":"#ffd23f","icon":"grind",
  "kicker":"merge the commonest pair, again and again",
  "blurb":"byte-pair encoding, learned live: repeatedly merge the most frequent adjacent pair to grow a vocabulary. The tokeniser that feeds a language like I-13."},
 {"src":"coding-theory-ternary.html","slug":"coding-theory-ternary","title":"TERNARY CODING",
  "appeal_name":"CHEAT","domain_title":"THE SHORTCUT","domain_slug":"the-shortcut","accent":"#7cfc00","icon":"cheat",
  "kicker":"base-3, the radix nearest optimal",
  "blurb":"coding theory in trits — base-3 is the integer radix closest to the theoretical optimum (e). The clever number system the Factory forgot."},
 # --- second pass: physics-named but genuinely CODE (VMs / kernels / gates / registers), self-contained ---
 {"src":"exciton-vm.html","slug":"exciton-vm","title":"THE EXCITON VM","appeal_name":"SPAWN",
  "domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#39fc6b","icon":"cheat",
  "kicker":"a real virtual machine + bytecode","blurb":"David's Exciton VM — a real bytecode virtual machine, vendored into THE FOLD."},
 {"src":"hydrogen-vm.html","slug":"hydrogen-vm","title":"THE HYDROGEN VM","appeal_name":"SPAWN",
  "domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#7cfc00","icon":"spawn",
  "kicker":"the simplest machine that computes","blurb":"David's Hydrogen VM — a virtual machine stripped to its simplest, vendored into THE FOLD."},
 {"src":"kernel-27.html","slug":"kernel-27","title":"KERNEL 27","appeal_name":"SPAWN",
  "domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#00f5ff","icon":"glitch",
  "kicker":"the 27-cell kernel · 3³","blurb":"David's 27-cell kernel (3³), the ternary compute core, vendored into THE FOLD."},
 {"src":"register.html","slug":"register","title":"THE REGISTER","appeal_name":"SPAWN",
  "domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#ffd23f","icon":"loot",
  "kicker":"a machine register, up close","blurb":"David's register instrument — the CPU register, up close, vendored into THE FOLD."},
 {"src":"ouroboros-engine.html","slug":"ouroboros-engine","title":"THE OUROBOROS ENGINE","appeal_name":"SPAWN",
  "domain_title":"THE TOOLCHAIN","domain_slug":"the-toolchain","accent":"#ff2d95","icon":"glitch",
  "kicker":"the compiler that eats its own tail","blurb":"David's Ouroboros engine — the self-consuming compile loop, vendored into THE FOLD."},
 {"src":"choice_engine.html","slug":"choice-engine","title":"THE CHOICE ENGINE","appeal_name":"SPAWN",
  "domain_title":"THE SANDBOX","domain_slug":"the-sandbox","accent":"#9d00ff","icon":"coop",
  "kicker":"a decision engine, made of code","blurb":"David's choice engine — a runnable decision machine, vendored into THE FOLD."},
 {"src":"twelve-gate-core.html","slug":"twelve-gate-core","title":"THE TWELVE-GATE CORE","appeal_name":"CHEAT",
  "domain_title":"THE KONAMI CODE","domain_slug":"the-konami-code","accent":"#ffd23f","icon":"cheat",
  "kicker":"twelve logic gates, one core","blurb":"David's twelve-gate core — logic gates composed into a compute core, vendored into THE FOLD."},
 {"src":"paper-08-logic-gate.html","slug":"paper-08-logic-gate","title":"THE LOGIC GATE","appeal_name":"CHEAT",
  "domain_title":"THE KONAMI CODE","domain_slug":"the-konami-code","accent":"#00f5ff","icon":"glitch",
  "kicker":"the gate all computing is built from","blurb":"David's logic-gate paper — the primitive every processor is built from, vendored into THE FOLD."},
 {"src":"octorat_chaos_silo.html","slug":"octorat-chaos-silo","title":"THE OCTORAT · CHAOS","appeal_name":"CHEAT",
  "domain_title":"THE SHORTCUT","domain_slug":"the-shortcut","accent":"#7cfc00","icon":"cheat",
  "kicker":"the ternary walker in chaos","blurb":"David's ternary octorat under chaos — the base-3 walker, vendored into THE FOLD."},
 {"src":"octorat_probability_engine.html","slug":"octorat-probability-engine","title":"THE OCTORAT · PROBABILITY","appeal_name":"CHEAT",
  "domain_title":"THE SHORTCUT","domain_slug":"the-shortcut","accent":"#ffd23f","icon":"cheat",
  "kicker":"the octorat's probability engine","blurb":"David's octorat probability engine — ternary odds made mechanical, vendored into THE FOLD."},
]

def main():
    db = json.load(open(os.path.join(W2, "fold.json"), encoding="utf-8"))
    top = {s["slug"]: s for s in db["spheres"]}
    dom_by_slug = {d["slug"]: d for a in db["appeals"] for d in a.get("domains", [])}
    for v in VENDOR:
        src = os.path.join(DL, v["src"])
        if not os.path.exists(src):
            print(f"  [!] missing: {v['src']}"); continue
        html = open(src, encoding="utf-8", errors="replace").read()
        ctx = {"ACCENT": v["accent"], "APPEAL": v["appeal_name"], "DOMAIN": v["domain_title"]}
        open(os.path.join(W2, v["slug"] + ".html"), "w", encoding="utf-8").write(frame(html, ctx))
        rec = {"slug": v["slug"], "title": v["title"], "kicker": v["kicker"],
               "accent": v["accent"], "blurb": v["blurb"]}
        if v["slug"] in top: top[v["slug"]].update(rec)
        else: db["spheres"].append(rec)
        d = dom_by_slug.get(v["domain_slug"])
        if d is not None:
            d.setdefault("spheres", [])
            nest = {"slug": v["slug"], "title": v["title"], "accent": v["accent"],
                    "icon": v["icon"], "kicker": v["kicker"]}
            ex = next((x for x in d["spheres"] if x.get("slug") == v["slug"]), None)
            if ex: ex.update(nest)
            else: d["spheres"].append(nest)
        print(f"  vendored {v['title']:22} -> {v['appeal_name']} / {v['domain_title']}  ({v['slug']}.html)")
    db["counts"]["spheres"] = len(db["spheres"])
    db["counts"]["spheres_built"] = sum(len(d.get("spheres", [])) for a in db["appeals"] for d in a["domains"])
    json.dump(db, open(os.path.join(W2, "fold.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"spheres now: {db['counts']['spheres']} sealed / {db['counts']['spheres_built']} seated")

if __name__ == "__main__":
    print("VENDORING DOWNLOADS -> WORLD II:")
    main()
