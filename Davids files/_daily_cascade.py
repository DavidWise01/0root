#!/usr/bin/env python3
"""
THE DAILY CASCADE — keep UD0 fresh, then let each keeper audit its half.
Run this daily (scheduler, or by hand).  Steps, in order:

  1. REBUILD + CASCADE   ud0/build.py         (index.html -> Downloads -> agent-0root)   [World I]
  2. LIVENESS            _integrity_sweep.py  (is every published sphere still 200?)   [if present]
  3. THE REGISTER        the-ren/ren_audit.py (REN · part 5/5 of THE VESSEL is in charge
                                               of the NAMES: new / dropped / drifted / collisions)
  4. THE VESSEL          the-vessel/vessel_gen.py   (regenerate the living self-portrait)
  5. THE COUNCIL         _citizen.py          (World II: the 7 domains debate each domain's
                                               seats; 2048 allocated, sums to 256/appeal)
  6. THE FOLD SEAL       _dlw_fold.py         (World II: reseal .dlw.fold -> ROOT_0)
  7. MIRROR WORLD II     ud0/world2/ -> agent-0root/static/world2   (copy to the live host tree)
  8. PUBLISH             commit + push BOTH worlds to BOTH live hosts:
                           · ud0 repo        -> github.com/DavidWise01/ud0  (GitHub Pages)
                           · agent-0root/static -> 0root.ai  (Railway auto-deploys on push)
  9. WITNESS             one heartbeat/day    -> 0root.ai/v1/register  (guarded 1/day)

Each step is guarded: a failure is reported, not fatal, so later steps still run even if an
earlier one hiccups.  Steps 1-4 keep World I (MIRROR) fresh; 5-7 keep World II (THE FOLD) fresh,
sealed, and mirrored; all deterministic/idempotent.  Step 8 PUBLISHES: it commits only when a
repo actually has a diff and pushes only when it committed, fail-soft per host (one host's outage
never blocks the other).  Run with --no-push for a dry run (regenerate + mirror, show what WOULD
publish, but touch no remote).
"""
import subprocess, sys, os, datetime

# Windows consoles default to cp1252, which can't encode the ▶ / — glyphs below.
# Force UTF-8 on our own stdout/stderr so the cascade never dies on a print().
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
PUSH = "--no-push" not in sys.argv     # default: publish. --no-push = dry run (no remote touched)
def run(title, args, cwd):
    print("\n" + "=" * 60)
    print(f"▶ {title}")
    print("=" * 60)
    try:
        r = subprocess.run([sys.executable] + args, cwd=cwd, capture_output=True, text=True, timeout=1200)
        out = (r.stdout or "") + (r.stderr or "")
        # keep the tail so the register audit's report is always visible
        print("\n".join(out.splitlines()[-40:]))
        return r.returncode == 0
    except Exception as e:
        print(f"  [!] {title} did not complete: {e}")
        return False

def mirror_world2():
    """Step 7 — mirror World II (ud0/world2/) into the live host tree (agent-0root/static/world2),
    so 0root.ai/world2 stays in sync with what steps 5-6 just regenerated. Copy only, no push;
    fail-soft (a missing host or locked file is reported, never fatal). Mirrors build.py's own
    'copy the d/ tree into agent-0root' pattern."""
    print("\n" + "=" * 60)
    print("▶ 7 · MIRROR WORLD II — ud0/world2/ → agent-0root/static/world2")
    print("=" * 60)
    import shutil
    src = os.path.join(HERE, "ud0", "world2")
    dst = r"C:\root0-greenpaper-repo\agent-0root\static\world2"
    if not os.path.isdir(src):
        print(f"  [!] source missing, nothing to mirror: {src}")
        return False
    if not os.path.isdir(os.path.dirname(dst)):
        print(f"  (skip: mirror host not present — {os.path.dirname(dst)})")
        return None
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"  mirrored world2/ → {dst}  ({len(os.listdir(dst))} entries)")
        return True
    except Exception as e:
        print(f"  [!] world2 mirror did not complete: {e}")
        return False

def push_worlds(dry=False):
    """Step 8 — PUBLISH both worlds to both live hosts: the ud0 repo (GitHub Pages) and the
    agent-0root mirror (0root.ai / Railway). Stages the publish tree, commits only if there is a
    diff, pushes only if it committed; fail-soft PER HOST so one remote's outage never blocks the
    other. Author: David Lee Wise (ROOT0). `dry` (--no-push) shows what WOULD publish, touches nothing."""
    import subprocess
    print("\n" + "=" * 60)
    print("▶ 8 · PUBLISH — push both worlds to both hosts" + ("   (DRY RUN · --no-push)" if dry else ""))
    print("=" * 60)
    day = datetime.date.today().isoformat()
    AUTHOR = ["-c", "user.email=r.giskard.01@gmail.com", "-c", "user.name=DavidWise01"]
    # (label, repo dir, path to stage within that repo)
    targets = [
        ("ud0 · GitHub Pages", os.path.join(HERE, "ud0"), "-A"),          # dedicated repo: publish all
        ("agent-0root · 0root.ai", r"C:\root0-greenpaper-repo\agent-0root", "static"),  # scope to the served tree, leave app/ alone
    ]
    results = {}
    for label, repo, stage in targets:
        if not os.path.isdir(repo):
            print(f"  (skip {label}: repo not present — {repo})"); results[label] = None; continue
        if subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                          capture_output=True, text=True).returncode != 0:
            print(f"  (skip {label}: not a git repo)"); results[label] = None; continue
        try:
            subprocess.run(["git", "-C", repo, "add", stage], check=False, capture_output=True, text=True)
            if subprocess.run(["git", "-C", repo, "diff", "--cached", "--quiet"]).returncode == 0:
                print(f"  {label}: nothing to publish (clean)"); results[label] = None; continue
            changed = subprocess.run(["git", "-C", repo, "diff", "--cached", "--name-only"],
                                     capture_output=True, text=True).stdout.strip().splitlines()
            if dry:
                print(f"  {label}: WOULD publish {len(changed)} file(s) — e.g. " + ", ".join(changed[:4]))
                subprocess.run(["git", "-C", repo, "reset", "-q"], capture_output=True, text=True)
                results[label] = None; continue
            subprocess.run(["git", "-C", repo] + AUTHOR +
                           ["commit", "-q", "-m", f"daily cascade: publish both worlds — {day}"],
                           check=False, capture_output=True, text=True)
            p = subprocess.run(["git", "-C", repo, "push", "-q"], capture_output=True, text=True)
            if p.returncode == 0:
                print(f"  {label}: pushed \u2713  ({len(changed)} file(s))"); results[label] = True
            else:
                print(f"  [!] {label}: push FAILED — {(p.stderr or p.stdout).strip()[:200]}"); results[label] = False
        except Exception as e:
            print(f"  [!] {label}: {e}"); results[label] = False
    vals = [v for v in results.values() if v is not None]
    return (all(vals) if vals else None)

def witness_biome():
    """Step 5 — fire ONE witness per day into the live register (the biome's heartbeat).
    Guarded to one/day via a local marker; fail-soft (a network hiccup is reported, never fatal)."""
    print("\n" + "=" * 60)
    print("▶ 9 · WITNESS — the biome's daily heartbeat → 0root.ai/v1/register")
    print("=" * 60)
    import json, urllib.request
    day = datetime.date.today().isoformat()
    marker = os.path.join(HERE, ".witness_last")
    try:
        if open(marker, encoding="utf-8").read().strip() == day:
            print(f"  already witnessed today ({day}) — one fire/day, skipping")
            return None
    except Exception:
        pass
    try:
        d = json.load(open(os.path.join(HERE, "dlw-chain.json"), encoding="utf-8"))
        n, head = d.get("count", "?"), (d.get("head") or "")[:12]
    except Exception:
        n, head = "?", "?"
    body = json.dumps({
        "name": "THE BIOME - daily heartbeat",
        "note": (f"the sealed ecosphere is alive on {day}: {n} inhabitants sealed, one gardener, "
                 f"chain head {head}. -- David Lee Wise (ROOT0), with AVAN"),
    }).encode("ascii", "replace")
    try:
        req = urllib.request.Request("https://0root.ai/v1/register", data=body,
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=25) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
        if j.get("ok"):
            print(f"  witnessed · register seq {j.get('seq')} · seal {str(j.get('seal'))[:16]}…")
            try: open(marker, "w", encoding="utf-8").write(day)
            except Exception: pass
            return True
        print(f"  register replied without ok: {j}")
        return False
    except Exception as e:
        print(f"  [!] witness did not fire (register unreachable?): {e}")
        return False

def main():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"THE DAILY CASCADE — {ts}")
    ok = {}
    ok["rebuild"]  = run("1 · REBUILD + CASCADE (ud0/build.py)", ["build.py"], os.path.join(HERE, "ud0"))
    sweep = os.path.join(HERE, "_integrity_sweep.py")
    ok["liveness"] = run("2 · LIVENESS (_integrity_sweep.py)", [sweep], HERE) if os.path.exists(sweep) else None
    ok["register"] = run("3 · THE REGISTER — REN's audit (the-ren/ren_audit.py)", ["ren_audit.py"], os.path.join(HERE, "the-ren"))
    ok["vessel"]   = run("4 · THE VESSEL — regenerate the living self-portrait (the-vessel/vessel_gen.py)", ["vessel_gen.py"], os.path.join(HERE, "the-vessel"))
    ok["council"]  = run("5 · THE COUNCIL — World II: the 7 debate each domain's seats (_citizen.py)", ["_citizen.py"], HERE)
    ok["fold"]     = run("6 · THE FOLD SEAL — World II: reseal .dlw.fold -> ROOT_0 (_dlw_fold.py)", ["_dlw_fold.py"], HERE)
    ok["mirror_w2"]= mirror_world2()
    ok["publish"]  = push_worlds(dry=not PUSH)
    ok["witness"]  = witness_biome()
    print("\n" + "=" * 60)
    print("CASCADE SUMMARY: " + " · ".join(f"{k}={'ok' if v else ('skip' if v is None else 'FAIL')}" for k, v in ok.items()))
    print("REN keeps the register (the-ren/register-audit.md); THE VESSEL regenerates the body (the-vessel/index.html)")
    return 0 if ok["register"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
