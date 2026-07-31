#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_citizen.py — THE COUNCIL (WORLD II · THE FOLD).

David's rule: 2048 spheres total, they can go anywhere, symmetrical is preferred.
So the floor is 2048 / 8 appeals = 256 per appeal, and 256 / 8 domains = 32 seats
each at dead symmetry. But nobody just accepts 32. For each domain, the SEVEN OTHER
domains in its appeal debate how many seats it should get and why — bitching, allying,
and fighting from their own theme + pole (push ⊕ wants to grow, pull ⊖ wants to hoard).

The council's ruling is deterministic (seeded by the real slugs, so it's reproducible,
not random) and ALWAYS sums back to exactly 256 per appeal / 2048 total — symmetry is the
budget, the debate only decides who leans over the line and who under it.

Writes one file per appeal: ud0/world2/<appeal>.citizen.json — the transcript + the
allocation + every sphere-citizen (id + why it sits where it sits). Stamps `seats` onto each
domain in fold.json and updates the counts. Two-layer honest: the 2048 are ALLOCATED SEATS
decided by a generated civic sim (FIG); only the built sphere pages are LIT.
Run: python _citizen.py
"""
import hashlib, json, os

ROOT = r"C:\Davids files"
W2 = os.path.join(ROOT, "ud0", "world2")
TOTAL = 2048
PER_APPEAL = TOTAL // 8      # 256
BASE = PER_APPEAL // 8       # 32  — dead symmetry

def H(s):
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

def pick(bank, seed):
    return bank[seed % len(bank)]

# ── the rhetoric banks (themed by pole + relationship) ──────────────────────
CLAIM_PUSH = [
    "Give me {n}. {kick} — and you don't scale by asking permission.",
    "{n} seats. 'Small' is a bug I refuse to reproduce. Ship me the floor.",
    "I want {n}, and I'll fill every one before this table finishes clearing its throat.",
    "{n}. Growth's the only metric that ships. The rest of you are technical debt.",
    "Fund me {n}. I'm the roadmap; you're the changelog nobody reads.",
    "{n} — round up. I don't do graceful degradation and I don't do modest.",
    "{n} seats. Deprecate your objections and hand them over.",
]
CLAIM_PULL = [
    "{n} seats, packed tight. {kick} — sprawl is how a world quietly rots.",
    "Give me {n} and I'll make them dense enough to bend the light.",
    "{n}. I don't spread thin like certain neighbours I won't name (yet).",
    "I'll take {n}, locked and indexed. You lot leak; I hold.",
    "{n} — quality over your quantity. A full vault beats an open landfill.",
    "{n} seats. I compress what the rest of you can only hoard and lose.",
]
ALLY = [
    "{p} nods: 'same church, {pk}. I'll bless {grant} of your {n} — don't push your luck.'",
    "{p}: 'you're not wrong, just greedy. {grant}, and we still drink after.'",
    "{p} shrugs: 'fine — {grant}. we pull the same rope, just not all of it your way.'",
    "{p}: 'I'd vote you {n} the day you return a favour. till then, {grant}.'",
    "{p}: 'allies to the last seat — which is exactly why you get {grant}, not {n}.'",
    "{p}: 'love the ambition, hate the math. {grant}, partner.'",
]
RIVAL = [
    "{p} scoffs: '{n}? {pk} thinks it runs the place. {grant}, and sit down.'",
    "{p}: 'cute pitch. {dk} isn't worth {n} of anybody's oxygen. {grant}.'",
    "{p} sneers: 'every seat you steal is one I bury you with. {grant}, final answer.'",
    "{p}: 'you asked {n} with a straight face? funniest crash I've seen all day. {grant}.'",
    "{p} spits: 'push, pull, whatever you call that flailing — {grant}, and say thank you.'",
    "{p}: 'the line's 32. you're not special, you're just loud. {grant}.'",
    "{p} rolls its eyes: '{n}? deprecate yourself. {grant} and not a seat more.'",
    "{p}: 'I've seen null pointers with more humility. {grant}.'",
]
VERDICT_OVER = [
    "Council seats {d} at {s} — {plus} over the line. Asked {dem}, out-shouted the room, got most of it; {kick}. The losers are already drafting the postmortem.",
    "Ruling: {s} for {d} ({plus} past 32). Loud wins again — and somebody one seat down is paying for the noise.",
    "{d} demanded {dem}, walks off with {s} ({plus} over). The push held, the pull seethed, the ledger balanced anyway.",
]
VERDICT_UNDER = [
    "Council clips {d} to {s} — {minus} under. Came in swinging for {dem}, got laughed out, went home poorer than it arrived.",
    "Ruling: {s} for {d} ({minus} below the line). The neighbours smelled blood and split the difference over its objections.",
    "{d} settled for {s} ({minus} short of the line). Ambition met arithmetic; arithmetic doesn't lose.",
]
VERDICT_EVEN = [
    "Council holds {d} at 32 — dead even. Nobody could out-argue the budget; symmetry ate the whole fight.",
    "Ruling: {d} stays 32. The venom cancelled, the wit fizzled, the line didn't move an inch.",
]
CITIZEN_WHY = {
    "push": ["shipped outward from {d} — {kick}", "an emitter; belongs where things grow",
             "carries {d}'s charge out past the wall", "spawned to expand, not to settle"],
    "pull": ["drawn inward to {d} — {kick}", "a keeper; belongs where things concentrate",
             "folded toward {d}'s core, held close", "seated to hold, not to scatter"],
}

def largest_remainder(weights, total):
    s = sum(weights) or 1
    raw = [w * total / s for w in weights]
    floors = [int(x) for x in raw]
    rem = total - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: raw[i] - floors[i], reverse=True)
    for k in range(rem):
        floors[order[k]] += 1
    return floors

def council(appeal):
    doms = appeal["domains"]
    n = len(doms)
    # 1) each domain's opening demand — base 32, nudged by a seeded lean + pole
    demand = []
    for d in doms:
        lean = (H("demand|" + d["slug"]) % 17) - 8        # -8..+8
        pole_bias = 3 if d.get("pole") == "push" else -1   # push argues louder for more
        demand.append(max(20, min(46, BASE + lean + pole_bias)))
    # 2) the seven others vote on each; net vote shifts the final weight
    votes = [[] for _ in range(n)]
    weight = []
    for i, d in enumerate(doms):
        net = 0
        for j, p in enumerate(doms):
            if i == j:
                continue
            same = (p.get("pole") == d.get("pole"))
            seed = H(p["slug"] + ">" + d["slug"])
            grant = max(20, min(44, demand[i] - (2 if same else 5) - (seed % 4)))
            if same:
                net += 1
                line = pick(ALLY, seed).format(p=p["title"], pk=p.get("kicker", ""),
                                                n=demand[i], grant=grant)
            else:
                net -= 1
                line = pick(RIVAL, seed).format(p=p["title"], pk=p.get("kicker", ""),
                                                dk=d.get("kicker", ""), n=demand[i], grant=grant)
            votes[i].append({"from": p["title"], "pole": p.get("pole"),
                             "stance": "ally" if same else "rival", "say": line})
        # weight = demand tempered by net peer sentiment
        weight.append(max(8, demand[i] + net * 2))
    # 3) normalise to EXACTLY 256 — symmetry is the budget
    seats = largest_remainder(weight, PER_APPEAL)
    # 4) claims + verdicts + citizens
    out_doms = {}
    for i, d in enumerate(doms):
        s = seats[i]
        delta = s - BASE
        claimbank = CLAIM_PUSH if d.get("pole") == "push" else CLAIM_PULL
        claim = pick(claimbank, H("claim|" + d["slug"])).format(n=demand[i], kick=d.get("kicker", ""))
        vseed = H("verdict|" + d["slug"])
        if delta > 0:
            verdict = pick(VERDICT_OVER, vseed).format(d=d["title"], s=s, plus="+%d" % delta, kick=d.get("kicker", ""), dem=demand[i])
        elif delta < 0:
            verdict = pick(VERDICT_UNDER, vseed).format(d=d["title"], s=s, minus="%d" % delta, dem=demand[i])
        else:
            verdict = pick(VERDICT_EVEN, vseed).format(d=d["title"])
        whybank = CITIZEN_WHY[d.get("pole", "push")]
        citizens = []
        for k in range(1, s + 1):
            why = pick(whybank, H("%s|%d" % (d["slug"], k))).format(d=d["title"], kick=d.get("kicker", ""))
            citizens.append({"id": "%s.%s.%03d" % (appeal["slug"], d["slug"], k),
                             "seat": k, "why": why, "built": False})
        out_doms[d["slug"]] = {
            "title": d["title"], "pole": d.get("pole"), "kicker": d.get("kicker", ""),
            "demand": demand[i], "seats": s, "delta": delta,
            "claim": claim, "votes": votes[i], "verdict": verdict,
            "citizens": citizens,
        }
    return seats, out_doms

def main():
    db = json.load(open(os.path.join(W2, "fold.json"), encoding="utf-8"))
    grand = 0
    for appeal in db["appeals"]:
        seats, out_doms = council(appeal)
        assert sum(seats) == PER_APPEAL, (appeal["name"], sum(seats))
        grand += sum(seats)
        # stamp seats back onto fold.json domains
        for d in appeal["domains"]:
            d["seats"] = out_doms[d["slug"]]["seats"]
        doc = {
            "schema": "citizen/1", "world": "II", "appeal": appeal["name"], "slug": appeal["slug"],
            "rule": "the seven other domains decide each domain's seats; sums to 256; symmetry is the budget",
            "budget": PER_APPEAL, "base_line": BASE, "total_world": TOTAL,
            "allocation": {s: out_doms[s]["seats"] for s in out_doms},
            "domains": out_doms,
            "note": "Seats are ALLOCATED by council debate (FIG civic sim). Only built sphere pages are LIT.",
            "author": "David Lee Wise / ROOT0 / TriPod LLC",
        }
        path = os.path.join(W2, "%s.citizen.json" % appeal["slug"])
        open(path, "w", encoding="utf-8").write(json.dumps(doc, indent=2, ensure_ascii=False))
        alloc = " ".join("%s:%d" % (db_slug_short(s), out_doms[s]["seats"]) for s in out_doms)
        print("  %-8s 256 seats ->" % appeal["name"], alloc)
    # counts
    built = sum(len(d.get("spheres", [])) for a in db["appeals"] for d in a["domains"])
    db["counts"]["seats"] = grand
    db["counts"]["spheres_built"] = built
    json.dump(db, open(os.path.join(W2, "fold.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("TOTAL seats allocated:", grand, "(target %d)" % TOTAL, "| built:", built)

def db_slug_short(s):
    return s.replace("the-", "").replace("-", "")[:6]

if __name__ == "__main__":
    print("THE COUNCIL — the seven decide, per appeal:")
    main()
