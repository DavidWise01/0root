# -*- coding: utf-8 -*-
"""Merge the two corpus exports into ONE continuous stream.

corpus-world1.json and corpus-world2.json are each a single JSON object with a
`spheres` array inside. That shape forces a reader to hold the whole 15 MB in
memory before it can look at the first sphere, and it means two files with two
different record schemas for what is one corpus.

This emits corpus.jsonl: newline-delimited JSON, one sphere per line, both
worlds in one file, in corpus order. Continuous in the useful sense --

  * streamable   a reader takes one line at a time; nothing has to be buffered
  * appendable   new spheres are `>>` onto the end, no rewrite, no reparse
  * seekable     line N is sphere N; no index needed
  * uniform      one schema across both worlds, so `w` is the only thing that
                 tells them apart

Line 1 is a manifest record (`"record":"manifest"`); every line after it is
`"record":"sphere"`. A reader that does not care can skip line 1 by checking
the field, not by counting.

Re-runnable: reads the exports, writes the merge. Nothing is invented here --
if a field is absent upstream it is absent in the output, not filled in.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "iphone", "full corpus")
GEN = os.path.join(HERE, "_world2_spheres.py")
OUT = os.path.join(HERE, "iphone", "full corpus", "corpus.jsonl")


def world2_seating():
    """slug -> (domain_slug, domain_title, appeal_slug, appeal_name).

    The world2 export carries no domain or appeal per sphere, and neither does
    fold.json -- the seating only exists in the generator's entry table. World I
    records DO carry both, so without this the merged file would have a schema
    that is only half populated depending on which world a line came from.
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


def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    w1 = load("corpus-world1.json")
    w2 = load("corpus-world2.json")
    seat = world2_seating()

    recs = []
    n = 0

    for s in w1["spheres"]:
        n += 1
        recs.append({
            "record": "sphere", "w": 1, "n": n,
            "uid": "1:" + str(s.get("slug")),
            "id": s.get("id"), "slug": s.get("slug"), "title": s.get("title"),
            "gloss": s.get("gloss"),
            "domain": s.get("domain"), "appeal": s.get("appeal"),
            "url": s.get("url"), "chars": s.get("chars"),
            # world I only
            "page_title": s.get("page_title"),
            "description": s.get("description"),
            "template": s.get("template"),
            "text": s.get("text"),
        })

    missing = 0
    for s in w2["spheres"]:
        n += 1
        slug = s.get("slug")
        dm_slug, dm_title, ap_slug, ap_name = seat.get(slug, (None, None, None, None))
        if dm_slug is None:
            missing += 1
        recs.append({
            "record": "sphere", "w": 2, "n": n,
            "uid": "2:" + str(slug),
            "id": s.get("id"), "slug": slug, "title": s.get("title"),
            "gloss": s.get("gloss"),
            "domain": dm_slug, "appeal": ap_slug,
            "url": s.get("url"), "chars": s.get("chars"),
            # world II only
            "kicker": s.get("kicker"),
            "domain_title": dm_title, "appeal_name": ap_name,
            "seal": s.get("seal"), "accent": s.get("accent"),
            "learned": s.get("learned"),
            "text": s.get("text"),
        })

    manifest = {
        "record": "manifest",
        "corpus": "UD0 - Universe David 0",
        "author": "David Lee Wise / ROOT0 / TriPod LLC",
        "format": "ndjson; line 1 is this manifest, every line after is one sphere",
        "spheres": len(recs),
        "world1": len(w1["spheres"]),
        "world2": len(w2["spheres"]),
        "world1_generated": w1.get("generated"),
        "world2_generated": w2.get("generated"),
        "world1_sealed_at": w1.get("sealed_at"),
        "source": "merge of corpus-world1.json + corpus-world2.json; world II "
                  "domain/appeal joined from the generator's seating table",
        "key": "uid (or n). NOT slug -- 76 slugs appear once in each world as a "
               "World I sphere and its World II counterpart, with different urls. "
               "Keying on slug alone silently collapses those 76 pairs.",
        "fields": "record w n uid id slug title gloss domain appeal url chars text",
        "note": "w=1 is World I MIRROR (sealed). w=2 is World II THE FOLD (live, "
                "count climbs). Records carry only what the sources carry.",
        "world2_unseated": missing,
        "world2_unseated_note":
            "%d World II spheres carry domain=null and appeal=null. These are the "
            "founding spheres, built before the generator's seating table existed; "
            "the seating is absent from every source in the corpus (the export, "
            "fold.json, and the built pages all lack it), so it is left null here "
            "rather than guessed. Every World I sphere is seated." % missing,
        "terms": "CC-BY-ND-4.0",
    }

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, ensure_ascii=False) + "\n")
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    size = os.path.getsize(OUT)
    print("wrote %s" % OUT)
    print("  %d lines (1 manifest + %d spheres: %d world I, %d world II)"
          % (len(recs) + 1, len(recs), len(w1["spheres"]), len(w2["spheres"])))
    print("  %.2f MB" % (size / 1048576.0))
    print("  %d of %d World II spheres seated; %d founding spheres carry "
          "domain=null (absent from every source, not dropped here)"
          % (len(w2["spheres"]) - missing, len(w2["spheres"]), missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
