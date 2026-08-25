"""|||  Test David's guess: are off-target counts vs bulge budget Fibonacci? (synthetic)"""
import probe

g = "ACGTACGTACGTACGTACGT"
print("guess: bulge1=1, bulge2=5, bulge3=8  (fib?)")
print("actual hit counts vs bulge budget (max_mm=4), 320kb synthetic seqs:")

seq = probe.synthetic_sequence(320000, probe.SEED + 320000)
row = [len(probe.search_offtargets(g, seq, 4, b)) for b in range(0, 6)]
print("  stress seed :", row)

for s in (7, 99, 2026, 42):
    seq = probe.synthetic_sequence(320000, s)
    row = [len(probe.search_offtargets(g, seq, 4, b)) for b in range(0, 6)]
    print("  seed %5d :" % s, row)

fib = [0, 1, 1, 2, 3, 5, 8, 13]
print("fib for reference:", fib[:6])
