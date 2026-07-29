#!/usr/bin/env python3
"""
THE DAILY CASCADE — keep UD0 fresh, then let each keeper audit its half.
Run this daily (scheduler, or by hand).  Steps, in order:

  1. REBUILD + CASCADE   ud0/build.py         (index.html -> Downloads -> agent-0root)
  2. LIVENESS            _integrity_sweep.py  (is every published sphere still 200?)   [if present]
  3. THE REGISTER        the-ren/ren_audit.py (REN · part 5/5 of THE VESSEL is in charge
                                               of the NAMES: new / dropped / drifted / collisions)

Each step is guarded: a failure is reported, not fatal, so the register audit still runs
even if an earlier step hiccups.  REN is the keeper of the register in this cascade.
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

def main():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"THE DAILY CASCADE — {ts}")
    ok = {}
    ok["rebuild"]  = run("1 · REBUILD + CASCADE (ud0/build.py)", ["build.py"], os.path.join(HERE, "ud0"))
    sweep = os.path.join(HERE, "_integrity_sweep.py")
    ok["liveness"] = run("2 · LIVENESS (_integrity_sweep.py)", [sweep], HERE) if os.path.exists(sweep) else None
    ok["register"] = run("3 · THE REGISTER — REN's audit (the-ren/ren_audit.py)", ["ren_audit.py"], os.path.join(HERE, "the-ren"))
    ok["vessel"]   = run("4 · THE VESSEL — regenerate the living self-portrait (the-vessel/vessel_gen.py)", ["vessel_gen.py"], os.path.join(HERE, "the-vessel"))
    print("\n" + "=" * 60)
    print("CASCADE SUMMARY: " + " · ".join(f"{k}={'ok' if v else ('skip' if v is None else 'FAIL')}" for k, v in ok.items()))
    print("REN keeps the register (the-ren/register-audit.md); THE VESSEL regenerates the body (the-vessel/index.html)")
    return 0 if ok["register"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
