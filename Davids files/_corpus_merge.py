# -*- coding: utf-8 -*-
"""Build the whole corpus as ONE continuous stream, from sources that cannot drift.

    python _corpus_merge.py

World II is regenerated from LOCAL files every run -- fold.json for the fields,
the built page for the text, the generator's entry table for the seating. It
used to be read from a crawl export, which meant corpus.jsonl froze at whatever
count the last crawl saw: it said 1,525 while the fold was already at 1,535.
Nothing that has to be re-crawled by hand can stay synchronised, so this reads
the same files the publish step writes.

The local extractor was checked against the crawl before it replaced it: 1,524
of 1,524 spheres present in both came out byte-identical. (The first attempt
stripped HTML comments with `<!--.*?-->`, which over-matched and ate real
content on 6 pages -- the version here does not strip them, and that is what
made the reproduction exact.) The export had one sphere, `the-4096`, that no
longer exists on disk, in fold.json, or on the mirror; regenerating locally
drops it, correctly.

World I stays sourced from corpus-world1.json. It is SEALED at 2,048 and its
pages live in separate GitHub repos, not here -- a sealed world cannot drift, so
a fixed export is the right source for it rather than a stale one.

Output, in ud0/world2 and the iphone bundle:

    corpus.jsonl        both worlds, newline-delimited, line 1 a manifest
    corpus-world2.json  the World II half, refreshed, same schema as the crawl

Continuous in the sense that matters: a reader takes one line at a time, new
spheres append without a rewrite, and line N is sphere N.
"""

import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLD = os.path.join(HERE, "ud0", "world2", "fold.json")
PAGES = os.path.join(HERE, "ud0", "world2")
GEN = os.path.join(HERE, "_world2_spheres.py")
W1 = os.path.join(HERE, "iphone", "full corpus", "corpus-world1.json")

OUT_DIRS = [
    os.path.join(HERE, "iphone", "full corpus"),
    os.path.join(HERE, "ud0", "world2"),
]

W2_URL = "https://0root.ai/world2/%s.html"


def die(msg):
    sys.stderr.write("FATAL: %s\n" % msg)
    raise SystemExit(1)


def extract(path):
    """Visible text of a built sphere page.

    Deliberately does NOT strip HTML comments -- see the module docstring; the
    obvious `<!--.*?-->` rule over-matches and silently truncates real content.
    """
    src = open(path, encoding="utf-8").read()
    s = re.sub(r"<script[^>]*>.*?</script>", " ", src, flags=re.S | re.I)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def seating():
    """slug -> (domain_slug, domain_title, appeal_slug, appeal_name).

    Neither fold.json nor the page carries the seating; it exists only in the
    generator's entry table.
    """
    src = open(GEN, encoding="utf-8").read()
    seat = {}
    pat = re.compile(
        r'\{"slug":"([a-z0-9-]+)".*?'
        r'"appeal_name":"([^"]*)","appeal_slug":"([^"]*)",\s*'
        r'"domain_title":"([^"]*)","domain_slug":"([^"]*)"',
        re.S)
    for m in pat.finditer(src):
        slug, ap_name, ap_slug, dm_title, dm_slug = m.groups()
        seat.setdefault(slug, (dm_slug, dm_title, ap_slug, ap_name))
    return seat


def world2_records():
    if not os.path.isfile(FOLD):
        die("no fold.json at %s -- run _world2_spheres.py first" % FOLD)
    fold = json.load(open(FOLD, encoding="utf-8"))
    seat = seating()
    recs, nopage, unseated = [], [], 0
    for s in fold["spheres"]:
        slug = s["slug"]
        page = os.path.join(PAGES, slug + ".html")
        if not os.path.isfile(page):
            nopage.append(slug)
            continue
        text = extract(page)
        url = W2_URL % slug
        dm_slug, dm_title, ap_slug, ap_name = seat.get(slug, (None, None, None, None))
        if dm_slug is None:
            unseated += 1
        recs.append({
            "id": hashlib.sha1(url.encode("utf-8")).hexdigest()[:16],
            "slug": slug, "title": s.get("title"), "kicker": s.get("kicker"),
            "gloss": s.get("blurb"), "seal": s.get("seal"),
            "learned": s.get("learned"), "accent": s.get("accent"),
            "url": url, "chars": len(text), "text": text,
            "_domain": dm_slug, "_domain_title": dm_title,
            "_appeal": ap_slug, "_appeal_name": ap_name,
        })
    return recs, nopage, unseated, fold


def main():
    w2, nopage, unseated, fold = world2_records()
    if not os.path.isfile(W1):
        die("no corpus-world1.json at %s" % W1)
    w1 = json.load(open(W1, encoding="utf-8"))

    lines, n = [], 0
    for s in w1["spheres"]:
        n += 1
        lines.append({
            "record": "sphere", "w": 1, "n": n,
            "uid": "1:" + str(s.get("slug")),
            "id": s.get("id"), "slug": s.get("slug"), "title": s.get("title"),
            "gloss": s.get("gloss"),
            "domain": s.get("domain"), "appeal": s.get("appeal"),
            "url": s.get("url"), "chars": s.get("chars"),
            "page_title": s.get("page_title"),
            "description": s.get("description"),
            "template": s.get("template"),
            "text": s.get("text"),
        })
    for s in w2:
        n += 1
        lines.append({
            "record": "sphere", "w": 2, "n": n,
            "uid": "2:" + s["slug"],
            "id": s["id"], "slug": s["slug"], "title": s["title"],
            "gloss": s["gloss"],
            "domain": s["_domain"], "appeal": s["_appeal"],
            "url": s["url"], "chars": s["chars"],
            "kicker": s["kicker"],
            "domain_title": s["_domain_title"], "appeal_name": s["_appeal_name"],
            "seal": s["seal"], "accent": s["accent"], "learned": s["learned"],
            "text": s["text"],
        })

    manifest = {
        "record": "manifest",
        "corpus": "UD0 - Universe David 0",
        "author": "David Lee Wise / ROOT0 / TriPod LLC",
        "format": "ndjson; line 1 is this manifest, every line after is one sphere",
        "spheres": len(lines),
        "world1": len(w1["spheres"]),
        "world2": len(w2),
        "world1_generated": w1.get("generated"),
        "world1_sealed_at": w1.get("sealed_at"),
        "world2_fold_root": fold.get("fold_root"),
        "world2_source": "regenerated from ud0/world2/fold.json + the built pages "
                         "on every run, so it cannot fall behind the fold",
        "world1_source": "corpus-world1.json; World I is SEALED at 2,048 and its "
                         "pages live in separate repos, so it cannot drift",
        "key": "uid (or n). NOT slug -- some slugs appear once in each world, as a "
               "World I sphere and its World II counterpart at different urls. "
               "Keying on slug alone silently collapses those pairs.",
        "fields": "record w n uid id slug title gloss domain appeal url chars text",
        "note": "w=1 is World I MIRROR (sealed). w=2 is World II THE FOLD (live).",
        "world2_unseated": unseated,
        "world2_unseated_note":
            "%d World II spheres carry domain=null and appeal=null: the founding "
            "spheres, built before the generator's seating table existed. The "
            "seating is absent from fold.json and from the pages too, so it is "
            "left null rather than guessed." % unseated,
        "terms": "CC-BY-ND-4.0",
    }

    jsonl = json.dumps(manifest, ensure_ascii=False) + "\n"
    jsonl += "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines)

    w2export = {
        "world": "world2", "generated": fold.get("sealed") or "",
        "source": "regenerated locally from fold.json + the built sphere pages",
        "schema": {k: "string" for k in
                   ("id slug title kicker gloss seal learned accent url chars text").split()},
        "stats": {
            "documents": len(w2),
            "total_chars": sum(r["chars"] for r in w2),
            "mean_chars": (sum(r["chars"] for r in w2) // max(1, len(w2))),
        },
        "declared": fold.get("counts", {}),
        "spheres": [{k: v for k, v in r.items() if not k.startswith("_")} for r in w2],
    }

    for d in OUT_DIRS:
        if not os.path.isdir(d):
            continue
        with open(os.path.join(d, "corpus.jsonl"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(jsonl)
        with open(os.path.join(d, "corpus-world2.json"), "w",
                  encoding="utf-8", newline="\n") as f:
            json.dump(w2export, f, ensure_ascii=False)

    print("corpus.jsonl  %d lines (1 manifest + %d spheres)" % (len(lines) + 1, len(lines)))
    print("  world I  %d (sealed export)" % len(w1["spheres"]))
    print("  world II %d (regenerated from fold.json + built pages)" % len(w2))
    print("  fold_root %s" % str(fold.get("fold_root"))[:16])
    print("  %d unseated (domain=null)" % unseated)
    if nopage:
        print("  %d in fold.json with NO built page: %s"
              % (len(nopage), ", ".join(nopage[:5])))
    for d in OUT_DIRS:
        if os.path.isdir(d):
            print("  wrote -> %s" % d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
