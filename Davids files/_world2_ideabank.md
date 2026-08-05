# World II · THE FOLD — ESOTERIC SPHERE IDEA BANK
Sourced 2026-07-31 by 5 domain-keeper agents. Each idea carries a CONCRETE in-browser-verifiable
math claim (the honesty gate). Build in the 5-window house style; verify the claim live before sealing.
Mark an idea `[BUILT]` when done. Prefer the obscure over the textbook. Some overlap across veins — pick distinct.

> ⚠ STALE (2026-08-01): most veins A–E are ALREADY BUILT. Before building ANY idea, grep the
> generator: `python -c "import re;print('the-SLUG' in set(re.findall(r'\"slug\":\"([^\"]+)\"',open('_world2_spheres.py',encoding='utf-8').read())))"`
> Batch 38 built the genuinely-absent: THE BUSY BEAVER, THE MARGOLUS MIRROR, THE REED-SOLOMON,
> THE MINSKY MACHINE, THE CRC. Refill the bank with NEW esoterica when picking gets hard.


Already built (do NOT rebuild): elementary CA, Turing machine, RPN stack, full-adder, BFS, Hamming(7,4),
chaos game/Sierpinski, DFA÷3, LFSR, Gray code, Sieve, Huffman, Euclid GCD, DFT, Newton fractal, bitonic sort,
Tower of Hanoi, gradient descent, backprop, memoization, SHA-256, Merkle tree, attention head, 3-2-1 compressor.

═══════════════════════════════════════════════════════════════════════
## VEIN A — EXOTIC NUMBER SYSTEMS, BASES & ARITHMETIC HARDWARE
1. THE IMAGINARY BASE — Knuth quater-imaginary (base 2i, digits 0-3). CLAIM: every a+bi (a,b∈−8..8) round-trips uniquely.
2. THE TWINDRAGON [BUILT] — base (−1+i), bits {0,1}. CLAIM: unique finite rep for a,b∈−8..8; depth-n fractions = 2^n (twindragon tile).
3. THE GOLDEN RADIX — base-φ, exact ℤ[φ] arithmetic. CLAIM: every int 0..100 has unique no-"11" form collapsing to n.
4. THE CARRYLESS FIELD — Nimber arithmetic (XOR add, recursive mult) = GF(16). CLAIM: field axioms + inverses exhaustive on {0..15}.
5. THE IRRATIONAL ODOMETER — Ostrowski numeration from CF of α. CLAIM: digits obey CF bounds, decode exactly; φ-case = Zeckendorf.
6. THE SUBSET ODOMETER [BUILT] — combinadics bijection 0..C(n,k)−1 ↔ k-subsets. CLAIM: rank∘unrank = id exhaustively for n=10,k=5.
7. THE SPARSEST SIGNATURE [BUILT] — Non-Adjacent Form (signed binary {−1,0,1}). CLAIM: unique NAF −128..127, no adjacent nonzeros, min weight.
8. THE MIRROR FIBONACCI [BUILT] — negaFibonacci coding (reaches negatives, no sign bit). CLAIM: unique no-"11" rep for −50..50.
9. THE PERMUTATION CLOCK [BUILT] — factorial number system + Lehmer code. CLAIM: rank∘unrank bijection over all 720 perms of 6.
10. THE LAZY COUNTER [BUILT] — skew binary (digits 0,1,2, one 2). CLAIM: unique canonical 0..2000; +1 touches ≤2 digits (O(1) carry).
11. THE FIBONACCI PARTITION — Zeckendorf. CLAIM: greedy decomp 1..200 non-consecutive, sums exact, unique.
12. THE RATIONAL TREE — Stern–Brocot. CLAIM: depth-12 all fractions lowest-terms, no repeats, each a mediant.
13. THE THREE-WAY DIGIT [BUILT] — balanced ternary {−,0,+}. CLAIM: unique −40..40, negate=digit-flip; balance-scale weighing puzzle.
14. THE REMAINDER LOOM [BUILT] — Residue Number System {3,5,7}, CRT. CLAIM: unique triples 0..104, CRT exact, componentwise +/× match mod 105.
15. THE ROTATING SHIFT — CORDIC (shift+add trig). CLAIM: 20 iters give sin/cos within 1e-6 of Math over a sweep.

═══════════════════════════════════════════════════════════════════════
## VEIN B — AUTOMATA, TILINGS & MODELS OF COMPUTATION
1. THE CYCLIC TAG [BUILT] — cyclic tag system (Cook's Rule-110 universality engine). CLAIM: re-derives documented word sequence step-by-step.
2. THE BUSY BEAVER — n-state halting champions. CLAIM: BB(3) halts 21 steps/6 ones, BB(2) 6 steps/4 ones, re-simulated from blank.
3. THE WANG DOMINOES [BUILT] — edge-colored tiles. CLAIM: backtracking fills N×N respecting colors; recolor one edge → 0 solutions (exhaustive).
4. THE POST DOMINOES [BUILT] — Post Correspondence Problem. CLAIM: known solution concatenates equal top/bottom; unsolvable one → no match ≤bound.
5. THE MARGOLUS MIRROR — reversible block CA (Critters). CLAIM: forward T then inverse T = exact start; particle count conserved.
6. THE SKI FOREST [BUILT] — combinatory logic S,K,I. CLAIM: S K K x → x for sampled x; S(K S)K → B (composition), by rewriting to normal form.
7. THE BETA REDUCER [BUILT] — untyped λ-calculus, Church numerals. CLAIM: MULT 2 3 β-reduces to Church 6; SUCC(SUCC ZERO)=2, structural compare.
8. THE WIREWORLD FOUNDRY — 4-state CA logic. CLAIM: built XOR/AND gate matches truth table by running the CA and timing output.
9. THE COLLATZ TAG [BUILT] — Collatz as 2-tag system (De Mol). CLAIM: tag output matches direct 3x+1 hailstone for sampled n.
10. THE MINSKY COUNTERS — 2-counter machine (INC/DEC-branch). CLAIM: stored program computes m×n, halts with product, vs direct mult.
11. THE PENROSE INFLATION — kites/darts substitution. CLAIM: tile-count ratio → φ (substitution-matrix eigenvalue), converging live.
12. THE OVERLAP-FREE WORD — Thue–Morse (0→01,1→10). CLAIM: first N symbols contain no cube (exhaustive scan); matches popcount parity.
13. THE TURMITE ZOO [BUILT] — Langton's ant & kin. CLAIM: ant builds the 104-step highway from blank grid (exact recurring period+displacement).
14. THE RULE 110 GLIDERS — particle view of Rule 110. CLAIM: ether space-period 14/time-period 7; glider constant velocity; collision outcome.
15. THE L-SYSTEM GARDEN — Lindenmayer A→AB,B→A. CLAIM: generation lengths = Fibonacci; bracketed turtle path branches per rules.

═══════════════════════════════════════════════════════════════════════
## VEIN C — CODING THEORY, CRYPTOGRAPHY & COMPRESSION
1. THE SHORTEST WITNESS — Berlekamp–Massey (shortest LFSR for a sequence). CLAIM: recovered LFSR regenerates input; recovers known deg-n gen from 2n terms.
2. THE NUMERAL [BUILT] — rANS (asymmetric numeral systems). CLAIM: encode→decode round-trips bytes; bits/symbol within a fraction of Shannon entropy.
3. THE COUNTER OF MULTITUDES — HyperLogLog. CLAIM: distinct-count estimate within ~1.04/√m of exact Set over N uniques.
4. THE GOLDEN CODE — Zeckendorf/Fibonacci self-delimiting code (ends "11"). CLAIM: greedy no-adjacent + sums to n; stream splits uniquely at "11".
5. THE HOMOMORPH [BUILT] — Paillier (toy). CLAIM: Dec(Enc(a)·Enc(b))=a+b and Dec(Enc(a)^k)=k·a over random a,b,k.
6. THE WHISPER NETWORK [BUILT] — LDPC bit-flipping decoder. CLAIM: corrupt valid codeword ≤k errors → iterative flipping restores (H·c=0).
7. THE SQUARE ROOT IN THE RING — Tonelli–Shanks modular sqrt. CLAIM: returned r satisfies r²≡n (mod p); non-residues flagged via Legendre.
8. THE OUROBOROS STRING — de Bruijn sequence. CLAIM: cyclic length b^k contains all b^k k-grams exactly once (enumerate windows).
9. THE EXACT TRANSFORM — Number Theoretic Transform. CLAIM: NTT·pointwise·INTT = schoolbook convolution bit-for-bit (prime field, no rounding).
10. THE THUMBPRINT [BUILT] — MinHash. CLAIM: fraction of matching min-hashes ≈ true Jaccard, converging with k.
11. THE NEST [BUILT] — Cuckoo filter. CLAIM: no false negatives; measured FP-rate near theoretical for fingerprint size; supports deletes.
12. THE FIXED BLOCK [BUILT] — Tunstall coding (variable-to-fixed, Huffman's dual). CLAIM: round-trips; equal codeword length; greedy fattest-leaf split.
13. THE FIELD INVERSE [BUILT] — Rijndael GF(2⁸) inversion / AES S-box. CLAIM: b⊗b⁻¹=1 for all nonzero b; S-box∘S-box⁻¹=id over 256 bytes.
14. THE MOST LIKELY PATH [BUILT] — Viterbi decoder. CLAIM: encode→inject ≤correctable errors→Viterbi recovers original bits over trials.
15. THE PROBABLE PRIME — Miller–Rabin. CLAIM: composites fail ≥3/4 bases (miss ≤4^−t); primes always pass, vs trial-division oracle.

═══════════════════════════════════════════════════════════════════════
## VEIN D — ESOTERIC DATA STRUCTURES & GRAPH / STRING / DP ALGORITHMS
1. THE ORACLE OF ECHOES — suffix automaton (DAWG). CLAIM: Σ(len−len[link]) = brute-force distinct-substring count; membership matches naive.
2. THE THIMBLE ARMY — HyperLogLog. CLAIM: within ~2% rel error at 2^14 registers vs exact Set.size. (dup of C3 — pick one)
3. THE FAILURE WEB — Aho-Corasick. CLAIM: one-pass (pattern,end) matches == per-pattern indexOf over 40 words / 5000 chars.
4. THE HALVING TREE [BUILT] — van Emde Boas. CLAIM: succ/pred match sorted-array binary search over 10k ops; op-count ~ log log u.
5. THE MIRROR SEEKER — Manacher. CLAIM: palindrome radii match O(n²) expand-around-center in one O(n) sweep (500 chars).
6. THE ALTERNATING PATH — Hopcroft–Karp. CLAIM: matching size = slow baseline AND = min vertex cover (Kőnig), live.
7. THE LAYERED FLOOD — Dinic max-flow. CLAIM: max flow = min cut every run on random networks.
8. THE COIN-FLIP HEAP — Treap. CLAIM: in-order always sorted, heap-property on priorities, membership vs Set; height ~2log₂n.
9. THE SPARSE ORACLE — Sparse Table RMQ. CLAIM: 5000 range-min via two power-of-two blocks match brute force; O(1)/query.
10. THE FORGIVING SIEVE [BUILT] — Count-Min Sketch. CLAIM: estimate ≥ true and ≤ true+εN over 100k stream vs exact map.
11. THE LOW-LINK MINER — Tarjan SCC. CLAIM: SCC partition == Kosaraju two-pass, up to relabeling.
12. THE PROPHET'S JUMP — Skip list. CLAIM: ops match sorted ref over 3000; avg hops within const·log₂n.
13. THE WELDER — Union-Find (path compression + rank). CLAIM: connectivity == brute BFS over 500 unions; avg follows ~flat (α(n)).
14. THE LAZY LORD — Segment tree + lazy propagation. CLAIM: 4000 range-add/range-sum match naive array (no lost/double updates).
15. THE FENWICK LADDER — Binary Indexed Tree (i&−i). CLAIM: prefix/range sums match cumulative array over 5000 ops; ~log₂n touches.

═══════════════════════════════════════════════════════════════════════
## VEIN E — SIGNAL / GRAPHICS / NUMERIC & UNCONVENTIONAL COMPUTING
1. THE ONE-BIT RIVER [BUILT] — delta-sigma modulator. CLAIM: modulate 0.5·sin at OSR=64, reconstruct <0.01 RMS; noise shaping >20dB hi vs lo.
2. THE DIGIT WITHOUT ITS PREDECESSORS — BBP formula. CLAIM: returns Nth hex digit of π (N=1→2, N=10, N=1000) vs reference, no prior digits.
3. THE STRING THAT REMEMBERS — Karplus–Strong. CLAIM: fundamental = fs/(N+0.5) within <1 Hz (autocorr); energy decays monotonically.
4. THE SINGLE EAR — Goertzel. CLAIM: single-bin magnitude = |X[k]| from full DFT to <1e-9; DTMF keypad detection.
5. THE INTEGRATOR THAT NEVER DRIFTS — leapfrog/Verlet vs RK4. CLAIM: leapfrog |ΔE| bounded over 1e5 steps; RK4 secular drift.
6. THE ORTHOGONAL SIGN-FLIP [BUILT] — Walsh–Hadamard transform. CLAIM: applied twice = N·identity (integer-exact); basis rows orthogonal (dots=0).
7. THE LEDGER THAT LOSES NOTHING [BUILT] — Kahan summation. CLAIM: sum 1e6×0.1: naive float32 drifts, Kahan within ~1 ULP of exact.
8. THE CURVE THAT FILLS [BUILT] THE PLANE — Hilbert curve. CLAIM: index↔(x,y) bijection over N×N; consecutive indices Manhattan-adjacent (=1).
9. THE ELECTRON MAZE — Wireworld (dup of B8 — pick one). CLAIM: gate truth tables + period-verified clock.
10. THE EMPTY CIRCLE LAW [BUILT] — Bowyer–Watson Delaunay. CLAIM: every triangle's circumcircle empty; maximizes min angle vs random triangulation.
11. THE MEAN OF TWO MEANS — Gauss–Legendre AGM for π. CLAIM: π to >1e-14 in ~4 iters; correct-digit count roughly doubles each pass.
12. THE POLITE SCATTER [BUILT] — Bridson Poisson-disk. CLAIM: all pairs ≥ r apart (no violations); blue-noise ring spectrum vs clumpy random.
13. THE LOADED-DICE TABLE — Walker's alias method. CLAIM: 1e6 draws reproduce target probs <0.5%/outcome; O(1) per draw.
14. THE FEATHERED EDGE [BUILT] — Xiaolin Wu antialiased line. CLAIM: two blended pixels per column sum to full intensity (energy conserved <1e-6).
15. THE SPOTS THAT BREED — Gray–Scott reaction–diffusion (Turing patterns). CLAIM: mitosis regime → blob count grows; params move across phase map.

═══════════════════════════════════════════════════════════════════════
NOTE: dedup — HyperLogLog (C3/D2), Wireworld (B8/E9), Zeckendorf (A11/C4) appear twice; build once.
~70 distinct concepts here = ~3.5 batches of 20. Re-run the keeper agents to refill when the bank runs low.

═══════════════════════════════════════════════════════════════════════
## VEIN F — REFILL (added 2026-08-04, batch 206). Veins A–E are EXHAUSTED.
Batch 206 checked 53 candidates across veins A–E plus fresh esoterica; ALL of A–E were taken,
as were 48 of the 53. The corpus is dense at 1165 — always run the three-way check
(generator slug + fold.json + ud0/world2 file listing) before drafting anything.

BUILT in batch 206: THE MONSKY, THE SHARKOVSKII, THE LOB, THE PRESBURGER, THE JORDAN CURVE.

BUILT in batch 209: all five below — THE ELLSBERG, THE NEWCOMB, THE GENTZEN, THE HERBRAND, THE KREIN-MILMAN.
VEIN F IS NOW EXHAUSTED TOO. Refill again before the next roll; the corpus is at 1180 and dense.

Was free as of 2026-08-04 (all now built):
1. THE ELLSBERG — ambiguity aversion; the two-urn choice pair is inconsistent with ANY
   probability assignment. CLAIM: exhaustively show no single P over the 90-ball urn makes both
   modal choices rational (linear feasibility, checkable by enumeration).
2. THE NEWCOMB — one-boxing vs two-boxing. CLAIM: build both decision tables and show causal
   and evidential decision theory give provably OPPOSITE recommendations on the same payoff matrix.
3. THE GENTZEN — sequent calculus cut-elimination. CLAIM: run the reduction on a proof WITH cuts,
   verify the output is cut-free, proves the same sequent, and has the subformula property.
4. THE HERBRAND — reduce a first-order validity to propositional. CLAIM: for a fixed formula,
   the Herbrand expansion at depth k becomes propositionally unsatisfiable at a specific k,
   verified by an actual SAT check.
5. THE KREIN-MILMAN — a compact convex set is the hull of its extreme points. CLAIM: for random
   polytopes, recompute the hull from extreme points alone and confirm it reproduces the set exactly.

NOTE ON SKOLEM SEQUENCES: free by slug, but deliberately SKIPPED — too close to the already-built
Langford pairing (same family). Near-duplicates are a real trap; batch 205 skipped `the-dither`
for the same reason (batch 42 already ships Floyd–Steinberg dithering).

## VEIN G — REFILL (added 2026-08-05, batch 229). Veins A–F are EXHAUSTED.
Batch 229 checked 40 candidates. **18 of the first 20 were already built** — the corpus is at
1280 and extremely dense. Always run the three-way check (generator slug + fold.json +
ud0/world2 file listing) before drafting anything, and check the STEM too.

TAKEN as of 2026-08-05 (do not re-draft): the-bbp, the-perrin, the-kolakoski, the-stern-brocot,
the-golomb-ruler, the-look-and-say, the-superpermutation, the-zeckendorf, the-farey,
the-carmichael, the-sylvester, the-recaman, the-wieferich, the-thue-morse, the-de-bruijn,
the-gray-code, the-cantor-pairing, the-hofstadter, the-eertree, the-alias-method,
the-dancing-links, the-sidon-set, the-van-der-corput, the-fractional-cascading, the-treap,
the-euler-tour.

BUILT in batch 229: THE ZERO-ONE PRINCIPLE, THE MARSAGLIA PLANES, THE LYNDON WORD,
THE DAVENPORT-SCHINZEL, THE HASHLIFE.

STILL FREE as of 2026-08-05 (verified by the three-way check — RE-CHECK before drafting):
1. THE COSTAS ARRAY — a permutation matrix whose displacement vectors are all distinct.
   CLAIM: exhaustively count Costas arrays for n ≤ 7 (1, 2, 4, 12, 40, 116, 200) and confirm
   every one has n(n−1)/2 pairwise-distinct difference vectors.
2. THE ULAM — the Ulam sequence 1, 2, 3, 4, 6, 8, 11, … each term the smallest integer that is
   a sum of two distinct earlier terms in exactly one way. CLAIM: generate to N and confirm the
   uniqueness condition holds term by term; the near-periodicity of the residues mod 21.6 is
   an OPEN observation and must be stamped AMBER if mentioned.
3. THE SPECTRAL TEST — Knuth's LCG quality measure. NOTE: near-duplicate of the-marsaglia-planes
   (batch 229). Only build if framed on the ν_t computation itself, not on the plane-counting.
4. THE BATCHER — odd-even mergesort as its own sphere. NOTE: near-duplicate of
   the-zero-one-principle (batch 229), which already builds and draws the Batcher network.
   Probably skip.
5. THE ZIGGURAT — Marsaglia & Tsang's rejection sampler for the normal distribution.
   CLAIM: build the 128-layer table, confirm every layer has equal area to machine precision,
   and measure the acceptance rate against the predicted 98.8%.
6. THE FINGER TREE — Hinze & Paterson's 2-3 finger tree. CLAIM: amortised O(1) access at both
   ends and O(log min(i, n−i)) at index i — measure node touches against that bound.
7. THE SCAPEGOAT — Galperin & Rivest's rebalance-by-rebuild tree. CLAIM: with α = 0.57, the
   measured amortised rebuild cost per insert stays bounded while worst-case depth stays under
   log_{1/α}(n).
8. THE MIDDLE SQUARE — von Neumann 1946, and its collapse. CLAIM: over all 10,000 four-digit
   seeds, count how many reach zero and the exact cycle-length distribution — exhaustive.
9. THE EXACT COVER — Knuth's Algorithm X without the dancing-links implementation.
   NOTE: the-dancing-links is TAKEN; only build if framed on the cover problem itself.
10. THE HASH LIFE TIME-DOUBLING — the half batch 229 deliberately did NOT implement. CLAIM: a
    node of size 2^k advances 2^(k−2) generations in one memoised lookup; measure the actual
    speedup against naive Life on a Gosper glider gun. This is a genuine open follow-up.

NOTE ON NEAR-DUPLICATES: batch 229 skipped the-spectral-test and the-batcher for exactly this
reason, as batch 205 skipped the-dither and batch 206 skipped Skolem sequences. A free slug is
not the same as a free idea.
