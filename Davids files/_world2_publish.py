# -*- coding: utf-8 -*-
"""One command to build, verify, seal and publish a World II batch.

    python _world2_publish.py --new the-convoy-effect,the-work-stealing,... \\
                              --message-file msg.txt

    python _world2_publish.py --new <slugs> --dry-run     # everything but the pushes

The steps were previously eleven manual commands, and the manual ones were where
things went wrong: llms.txt advertising a count the files did not contain, the
agent-0root mirror committed but not pushed (0root.ai went 50 spheres stale that
way), the corpus frozen at the last crawl. Each of those is now either automated
or gated.

THE GATE THAT MATTERS: --new slugs are re-derived live against the BUILT pages
before anything is committed. If a single published LIT number is not reproduced
by the instrument that ships, this aborts and nothing is pushed. A selftest
passing in a scratch file is not evidence about the artifact; only the artifact
is. Never weaken this to make a count.

Order:
    1  build          _world2_spheres.py
    2  VERIFY         _world2_verify.js on --new           <-- aborts on failure
    3  teach          _i13_teach.py
    4  seal           _dlw_fold.py
    5  corpus         _corpus_merge.py  (also regenerates llms.txt counts)
    6  stage          copy corpus + llms.txt into agent-0root/static
    7  push ud0       add world2 + commit + push
    8  mirror         robocopy /MIR ud0/world2 -> agent-0root/static/world2
    9  push mirror    add static + commit + PUSH (not just commit)
   10  commit C:      the generator and claim file
   11  POST-CHECK     both hosts same sphere count and fold_root, corpus parses,
                      corpus World II count == fold count, llms.txt agrees
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UD0 = os.path.join(HERE, "ud0")
W2 = os.path.join(UD0, "world2")
AGENT = os.path.join(HERE, "agent-0root")
STATIC = os.path.join(AGENT, "static")
BUNDLE = os.path.join(HERE, "iphone", "full corpus")

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def say(step, msg):
    print("[%s] %s" % (step, msg), flush=True)


def die(msg):
    print("\nABORTED: %s" % msg, flush=True)
    raise SystemExit(1)


def run(cmd, cwd=None, step="", allow=(0,)):
    r = subprocess.run(cmd, cwd=cwd or HERE, env=ENV,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode not in allow:
        sys.stdout.write(r.stdout or "")
        sys.stderr.write(r.stderr or "")
        die("%s failed (exit %d): %s" % (step, r.returncode, " ".join(cmd[:3])))
    return r


def tail(text, n=1):
    lines = [l for l in (text or "").splitlines() if l.strip()]
    return lines[-n] if lines else ""


def read_fold():
    with open(os.path.join(W2, "fold.json"), encoding="utf-8") as f:
        d = json.load(f)
    return d["counts"]["spheres"], d["fold_root"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", default="",
                    help="comma-separated slugs added this batch; verified live")
    ap.add_argument("--message-file", help="commit message file")
    ap.add_argument("--message", help="commit message (use --message-file for long ones)")
    ap.add_argument("--dry-run", action="store_true",
                    help="build, verify, seal and merge, but do not commit or push")
    ap.add_argument("--skip-verify", action="store_true",
                    help=argparse.SUPPRESS)   # deliberately undocumented; see below
    a = ap.parse_args()

    new = [s.strip() for s in a.new.split(",") if s.strip()]
    if a.skip_verify:
        # Not a normal option. If you are reaching for it, the honest move is to
        # fix the sphere, not to publish an unverified claim.
        say("!!", "VERIFICATION SKIPPED BY FLAG -- this batch is being published "
                  "without re-deriving its published numbers")

    # 1 build
    say("1/11", "building spheres")
    r = run([sys.executable, "_world2_spheres.py"], step="build")
    say("1/11", tail(r.stdout))

    # 2 verify -- the gate
    if new and not a.skip_verify:
        say("2/11", "re-deriving %d new spheres against the BUILT pages" % len(new))
        r = subprocess.run(["node", "_world2_verify.js"] + new, cwd=HERE, env=ENV,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        sys.stdout.write(r.stdout or "")
        if r.returncode != 0:
            sys.stderr.write(r.stderr or "")
            die("live verification failed -- nothing was committed or pushed. "
                "Fix the sphere; do not publish the number.")
    elif not new:
        say("2/11", "no --new slugs given; skipping live re-derivation")

    # 3 teach, 4 seal, 5 corpus
    say("3/11", "teaching I-13")
    run([sys.executable, "_i13_teach.py"], step="i13")
    say("4/11", "sealing the fold")
    r = run([sys.executable, "_dlw_fold.py"], step="seal")
    say("4/11", tail(r.stdout))
    say("5/11", "regenerating the corpus + llms.txt from local sources")
    r = run([sys.executable, "_corpus_merge.py"], step="corpus")
    for l in (r.stdout or "").splitlines():
        if l.strip():
            say("5/11", l.strip())

    count, root = read_fold()

    # 6 stage the corpus onto the serving host
    say("6/11", "staging corpus + llms.txt into agent-0root/static")
    for name in ("corpus.jsonl", "corpus-world2.json", "llms.txt"):
        src = os.path.join(W2, name) if name != "llms.txt" else os.path.join(BUNDLE, name)
        if not os.path.isfile(src):
            die("expected %s to exist after the corpus step" % src)
        shutil.copyfile(src, os.path.join(STATIC, name))

    if a.dry_run:
        say("--", "dry run: built, verified, sealed and merged. Nothing pushed.")
        say("--", "spheres %d  fold_root %s" % (count, root[:16]))
        return 0

    msg = None
    if a.message_file:
        msg = ["-F", a.message_file]
    elif a.message:
        msg = ["-m", a.message]
    else:
        die("need --message-file or --message to commit")

    # 7 ud0
    say("7/11", "committing + pushing ud0")
    run(["git", "add", "world2"], cwd=UD0, step="ud0 add")
    run(["git", "commit", "-q"] + msg, cwd=UD0, step="ud0 commit")
    run(["git", "push", "-q", "origin", "HEAD"], cwd=UD0, step="ud0 push")

    # 8 mirror
    say("8/11", "mirroring world2 -> agent-0root/static/world2")
    r = subprocess.run(["robocopy", W2, os.path.join(STATIC, "world2"),
                        "/MIR", "/NFL", "/NDL", "/NJH", "/NJS", "/NP"],
                       capture_output=True, text=True)
    if r.returncode >= 8:
        die("robocopy failed rc=%d" % r.returncode)

    # 9 mirror push -- COMMIT IS NOT ENOUGH, 0root.ai serves from origin
    say("9/11", "committing + PUSHING the mirror")
    run(["git", "fetch", "-q", "origin"], cwd=AGENT, step="mirror fetch")
    run(["git", "add", "static"], cwd=AGENT, step="mirror add")
    run(["git", "commit", "-q"] + msg, cwd=AGENT, step="mirror commit")
    run(["git", "push", "-q", "origin", "HEAD"], cwd=AGENT, step="mirror push")
    r = run(["git", "status", "-sb"], cwd=AGENT, step="mirror status")
    if "ahead" in (r.stdout or ""):
        die("mirror still ahead of origin after push -- 0root.ai would go stale")

    # 10 the generator side. NEVER `git add -A` under C:\ -- named paths only.
    say("10/11", "committing the generator")
    paths = ["_world2_spheres.py", "_corpus_merge.py", "_world2_verify.js",
             "_world2_publish.py",
             os.path.join("iphone", "full corpus", "corpus.jsonl"),
             os.path.join("iphone", "full corpus", "corpus-world2.json"),
             os.path.join("iphone", "full corpus", "llms.txt")]
    run(["git", "add"] + [p for p in paths if os.path.exists(os.path.join(HERE, p))],
        cwd=HERE, step="C: add")
    run(["git", "commit", "-q"] + msg, cwd=HERE, step="C: commit", allow=(0, 1))

    # 11 post-check
    say("11/11", "post-check")
    problems = []
    counts = {}
    for label, d in (("ud0", W2), ("mirror", os.path.join(STATIC, "world2"))):
        with open(os.path.join(d, "fold.json"), encoding="utf-8") as f:
            fd = json.load(f)
        counts[label] = (fd["counts"]["spheres"], fd["fold_root"])
    if counts["ud0"] != counts["mirror"]:
        problems.append("hosts disagree: %s" % counts)

    jl = os.path.join(STATIC, "corpus.jsonl")
    with open(jl, "rb") as f:
        raw = f.read()
    if b"\r\n" in raw:
        problems.append("corpus.jsonl contains CRLF")
    lines = raw.decode("utf-8").split("\n")[:-1]
    try:
        man = json.loads(lines[0])
    except Exception as e:
        problems.append("manifest line does not parse: %s" % e)
        man = {}
    w2n = sum(1 for l in lines[1:] if json.loads(l)["w"] == 2)
    if w2n != count:
        problems.append("corpus World II %d != fold %d" % (w2n, count))
    if man.get("world2_fold_root") != root:
        problems.append("manifest fold_root does not match the seal")
    llms = open(os.path.join(STATIC, "llms.txt"), encoding="utf-8").read()
    if format(count, ",") not in llms:
        problems.append("llms.txt does not state the current World II count")

    for label in counts:
        say("11/11", "%-7s spheres %d  fold_root %s"
            % (label, counts[label][0], counts[label][1][:16]))
    say("11/11", "corpus %d lines, World II %d, manifest root %s"
        % (len(lines), w2n, str(man.get("world2_fold_root"))[:16]))

    if problems:
        for p in problems:
            print("  PROBLEM: %s" % p)
        die("post-check found %d problem(s) -- the push already happened, "
            "so fix and re-run" % len(problems))

    print("\nPUBLISHED  %d spheres  fold_root %s  corpus %d records"
          % (count, root[:16], len(lines) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
