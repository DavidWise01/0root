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
  7. WITNESS             one heartbeat/day    -> 0root.ai/v1/register  (guarded 1/day)

Each step is guarded: a failure is reported, not fatal, so later steps still run even if an
earlier one hiccups.  Steps 1-4 keep World I (MIRROR) fresh; 5-6 keep World II (THE FOLD) fresh
and sealed; both are deterministic/idempotent (re-running changes nothing unless the corpus did).
Local regeneration only — nothing here git-pushes; publishing stays a manual step.
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

def witness_biome():
    """Step 5 — fire ONE witness per day into the live register (the biome's heartbeat).
    Guarded to one/day via a local marker; fail-soft (a network hiccup is reported, never fatal)."""
    print("\n" + "=" * 60)
    print("▶ 7 · WITNESS — the biome's daily heartbeat → 0root.ai/v1/register")
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
    ok["witness"]  = witness_biome()
    print("\n" + "=" * 60)
    print("CASCADE SUMMARY: " + " · ".join(f"{k}={'ok' if v else ('skip' if v is None else 'FAIL')}" for k, v in ok.items()))
    print("REN keeps the register (the-ren/register-audit.md); THE VESSEL regenerates the body (the-vessel/index.html)")
    return 0 if ok["register"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
