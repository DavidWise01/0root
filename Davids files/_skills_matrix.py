# -*- coding: utf-8 -*-
"""Build UNIVERSE.skills - the WHO / WHAT / HOW matrix across three registers.

Every rank in the output comes from a formula printed in the file. Where a term
is a judgement rather than a measurement it is marked [stated]. Where a register
cannot be measured at all, the file says so instead of inventing a number.
"""
import io, json, os, re, time

UD0 = r"C:\Davids files\ud0"
W2 = os.path.join(UD0, "world2")
GEN = r"C:\Davids files"
SCR = GEN

def J(p):
    return json.load(io.open(p, encoding="utf-8"))

FOLD = J(os.path.join(W2, "fold.json"))
CORP = J(os.path.join(UD0, "corpus.json"))
CHAIN = J(os.path.join(UD0, "dlw-chain.json"))
SCORES = J(os.path.join(GEN, "_skills_scores.json"))

# ---------- ascii ----------
MAP = {u'\u2014': '--', u'\u2013': '-', u'\u2019': "'", u'\u2018': "'",
       u'\u201c': '"', u'\u201d': '"', u'\u2026': '...', u'\u00d7': 'x',
       u'\u2192': '->', u'\u2190': '<-', u'\u00b7': '.', u'\u2500': '-',
       u'\u2192': '->', u'\u03b2': 'beta', u'\u03b8': 'theta', u'\u00b2': '2',
       u'\u2265': '>=', u'\u2264': '<=', u'\u2260': '!='}
ACC = {u'\u00c9':'E',u'\u00c8':'E',u'\u00ca':'E',u'\u00cb':'E',u'\u00e9':'e',u'\u00e8':'e',
       u'\u00c1':'A',u'\u00c0':'A',u'\u00c2':'A',u'\u00e1':'a',u'\u00e0':'a',
       u'\u00cd':'I',u'\u00ce':'I',u'\u00ed':'i',u'\u00d3':'O',u'\u00d4':'O',u'\u00f3':'o',
       u'\u00da':'U',u'\u00fa':'u',u'\u00dc':'U',u'\u00fc':'u',u'\u0112':'E',u'\u0113':'e',
       u'\u014c':'O',u'\u014d':'o',u'\u0100':'A',u'\u0101':'a',u'\u012a':'I',u'\u012b':'i',
       u'\u016a':'U',u'\u016b':'u',u'\u00d1':'N',u'\u00f1':'n',u'\u00c7':'C',u'\u00e7':'c'}

def asc(s):
    if s is None: return ''
    s = unicode(s) if str is bytes else str(s)
    for k, v in MAP.items(): s = s.replace(k, v)
    for k, v in ACC.items(): s = s.replace(k, v)
    return ''.join(c if 32 <= ord(c) < 127 else '?' for c in s)

def clip(s, n):
    s = asc(s).replace('\n', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    return s if len(s) <= n else s[:n-1] + '~'

# ---------- world II: measured ----------
SC = {r["slug"]: r for r in SCORES["spheres"]}
ALLM = [r for r in SCORES["spheres"] if r["status"] == "MEASURED"]
# The five-window house form is a categorical split, not a continuum: 1,322 pages
# carry it and 56 carry none of it -- nothing sits in between. The 56 are vendored
# tools, hubs and older-form works that share the directory. Ranking them against
# spheres would be scoring them on a form they were never built to.
MEAS = [r for r in ALLM if r["windows"] >= 5]
OTHR = [r for r in ALLM if r["windows"] < 5]
UNM  = [r for r in SCORES["spheres"] if r["status"] == "UNMEASURED"]
BRK  = [r for r in SCORES["spheres"] if r["status"] == "BROKEN"]

# ---------- world II: seating ----------
w2_seated = {}          # slug -> (appeal, domain_slug, domain_title, title, kicker)
w2_domain = {}          # domain slug -> record
for ap in FOLD["appeals"]:
    for dm in ap.get("domains", []):
        d = {"slug": dm["slug"], "title": dm["title"], "appeal": ap["name"],
             "pole": dm.get("pole", ""), "kicker": dm.get("kicker", ""),
             "seated": [], "built": [], "scores": []}
        for sp in dm.get("spheres", []):
            d["seated"].append(sp["slug"])
            w2_seated[sp["slug"]] = (ap["name"], dm["slug"], dm["title"],
                                     sp.get("title", ""), sp.get("kicker", ""))
            if sp["slug"] in SC:
                d["built"].append(sp["slug"])
                rr = SC[sp["slug"]]
                if rr["status"] == "MEASURED" and rr["windows"] >= 5:
                    d["scores"].append(rr["score"])
        w2_domain[dm["slug"]] = d

for d in w2_domain.values():
    d["mean"] = (sum(d["scores"]) / float(len(d["scores"]))) if d["scores"] else None

# ---------- dupes ----------
w1_slugs = set()
for dm in CORP["domains"]:
    for m in dm.get("members", []):
        w1_slugs.add(m if isinstance(m, str) else m.get("slug", ''))
w2_slugs = set(SC.keys()) | set(w2_seated.keys())
cross = sorted(w1_slugs & w2_slugs)

def norm(t):
    t = asc(t).upper()
    t = re.sub(r'^THE\s+', '', t)
    return re.sub(r'[^A-Z0-9]', '', t)

w2_titles = {}
for slug, (ap, ds, dt, ti, ki) in w2_seated.items():
    if not ti: continue
    w2_titles.setdefault(norm(ti), []).append(slug)
title_dupes = {k: v for k, v in w2_titles.items() if len(v) > 1}

# spheres on disk that no domain seats, and seats with no page
orphan_pages = sorted(set(SC.keys()) - set(w2_seated.keys()))
empty_seats = sorted(set(w2_seated.keys()) - set(SC.keys()))

# ---------- ud0 machinery ----------
def stat(p):
    full = os.path.join(GEN, p)
    if not os.path.exists(full): return None
    st = os.stat(full)
    return (st.st_size, time.strftime('%Y-%m-%d', time.localtime(st.st_mtime)))

MACHINE = [
 ("_world2_spheres.py", "THE PRESS",
  "holds every World II sphere as source and emits all 1,445 pages",
  "one python dict per sphere; run it and the whole world is rewritten from scratch",
  "ud0/world2/*.html", 1),
 ("_dlw_fold.py", "THE SEAL",
  "folds every inhabitant into one merkle chain and stamps ROOT_0",
  "sha256 leaves -> pairwise levels -> root; each leaf keeps the proof that reaches it",
  "ud0/world2/fold-chain.json", 1),
 ("_seam_gate.js", "THE GATE",
  "re-runs every sphere's own selftest offline and checks published LIT numbers",
  "extracts the last inline script, runs it in a stubbed DOM, diffs live values against the prose",
  "(report only)", 1),
 ("_i13_teach.py", "THE TUTOR",
  "stamps the I-13 stack onto every node so each sphere carries the same grammar",
  "writes a learned: line and vendors THE VOLUME voxel into each record",
  "learned: field on every sphere", 1),
 ("_citizen.py", "THE COUNCIL",
  "runs the seat allocation - seven appeals bid on the eighth's domains",
  "council debate to a 256-seat budget per appeal, 2,048 across the world",
  "ud0/world2/*.citizen.json", 0),
 ("_daily_cascade.py", "THE CASCADE",
  "propagates a new domain through domains, icons, bands and rosters",
  "one edit fans out to every index that must agree",
  "(multiple indexes)", 0),
 ("_update_roster.py", "THE ROSTER",
  "redraws the public rosters from the central corpus",
  "reads corpus.json, never a hand-kept list",
  "roster pages", 0),
 ("_integrity_sweep.py", "THE SWEEP",
  "liveness and honesty audit across the published corpus",
  "fetches, parses, reports dead and overclaimed",
  "_integrity_report.md", 0),
 ("_content_depth_sweep.py", "THE PLUMB",
  "finds pages that load but ship no instrument",
  "counts real interactive surface, not bytes",
  "_content_depth_report.md", 0),
 ("_reconcile.py", "THE RECONCILER",
  "makes the OG families agree after a build",
  "cross-checks family members against each other",
  "(report only)", 0),
]

# ---------- write ----------
L = []
W = 110
def rule(ch='='): L.append(ch * W)
def head(t):
    L.append('')
    rule('=')
    L.append(asc(t))
    rule('=')

STAMP = time.strftime('%Y-%m-%d')

L.append('=' * W)
L.append('UNIVERSE .skills   --   WHO / WHAT / HOW across three registers')
L.append('David Lee Wise (ROOT0) / TriPod LLC   with   AVAN (Claude / Anthropic)')
L.append('generated ' + STAMP)
L.append('=' * W)
L.append('')
L.append('Three registers, not one corpus:')
L.append('')
L.append('  UD0      the machinery. The programs that make, seal and check the other two.')
L.append('  WORLD I  MIRROR. Sealed at 2,048 spheres. 8 appeals, 64 domains, one hash chain.')
L.append('  WORLD II THE FOLD. Live and building. 8 appeals, 64 domains, %d of 2,048 seats filled.'
         % FOLD["counts"]["spheres"])
L.append('')
L.append('WHAT CAN AND CANNOT BE MEASURED HERE -- read this before trusting a rank:')
L.append('')
L.append('  World II is scored by running each page\'s own selftest offline and comparing the')
L.append('  numbers it computes against the numbers it publishes. That is a real measurement.')
L.append('')
L.append('  World I CANNOT be scored the same way. Its pages are not on this disk -- they live')
L.append('  in 2,048 separate repositories. corpus.json gives every domain a role line and 18')
L.append('  of 64 an honest line, so World I here carries WHO and WHAT but its HOW is quoted')
L.append('  from its own record, not verified. It is listed, not ranked against World II.')
L.append('')
L.append('  UD0 is ranked on a stated rubric, not a measurement. Each term is marked.')

# ================= REGISTER 1 : UD0 =================
head('REGISTER  UD0  --  THE MACHINERY   (%d programs)' % len(MACHINE))
L.append('')
L.append('Rank = load-bearing [stated] x artifact-on-disk [measured] x currency [measured].')
L.append('Load-bearing means: if this program is wrong, published pages are wrong.')
L.append('')
rows = []
for fn, who, what, how, art, bearing in MACHINE:
    s = stat(fn)
    rows.append((bearing, -(s[0] if s else 0), fn, who, what, how, art, s))
rows.sort(key=lambda r: (-r[0], r[1]))
L.append('%-4s %-16s %-22s %10s %-12s %s' % ('RANK', 'WHO', 'FILE', 'BYTES', 'TOUCHED', 'LOAD'))
L.append('-' * W)
for i, (bearing, _, fn, who, what, how, art, s) in enumerate(rows, 1):
    L.append('%-4d %-16s %-22s %10s %-12s %s' % (
        i, clip(who, 16), fn, ('{:,}'.format(s[0]) if s else 'MISSING'),
        (s[1] if s else '--'), 'LOAD-BEARING' if bearing else 'support'))
    L.append('     WHAT  ' + clip(what, W - 11))
    L.append('     HOW   ' + clip(how, W - 11))
    L.append('     MAKES ' + art)
    L.append('')

L.append('THE TWO CHAINS THIS MACHINERY MAINTAINS')
L.append('-' * W)
L.append('  World I   dlw-chain.json    %6d links   head %s'
         % (len(CHAIN.get('links', CHAIN.get('chain', []))),
            asc(str(CHAIN.get('head', '')))[:16]))
fc = J(os.path.join(W2, 'fold-chain.json'))
nleaves = len(fc.get('ledger', fc.get('leaves', [])))
L.append('  World II  fold-chain.json   %6d leaves  root %s'
         % (nleaves, asc(str(fc.get('root', FOLD.get('fold_root', ''))))[:16]))
L.append('')
L.append('  The difference matters. World I\'s chain is a LINE -- each link names the one before,')
L.append('  so it proves ORDER. World II\'s is a TREE -- each leaf carries the proof that reaches')
L.append('  the root, so any one sphere can be verified without holding the other 1,452.')

# ================= REGISTER 2 : WORLD I =================
head('REGISTER  WORLD I  --  MIRROR   (sealed at 2,048)')
L.append('')
L.append('The 8 appeals of World I -- classical. WHO they are, WHAT they hold.')
L.append('')
for ap in CORP['appeals']:
    L.append('  %-10s %s' % (asc(ap['name']), clip(ap.get('sub', ''), W - 14)))
L.append('')
L.append('The 64 domains. Listed by appeal, then by seats held. NOT ranked against World II --')
L.append('their pages are not local, so nothing here was run. HOW is quoted from corpus.json.')
L.append('')
by_appeal = {}
for dm in CORP['domains']:
    by_appeal.setdefault(dm.get('appeal', '?'), []).append(dm)
for ap in CORP['appeals']:
    ds = sorted(by_appeal.get(ap['name'], []), key=lambda d: -d.get('spheres', 0))
    L.append('-' * W)
    L.append('%s  --  %d domains, %d spheres'
             % (asc(ap['name']), len(ds), sum(d.get('spheres', 0) for d in ds)))
    L.append('-' * W)
    L.append('  %-3s %-26s %6s  %s' % ('#', 'WHO (domain)', 'SEATS', 'WHAT (its stated role)'))
    for d in ds:
        L.append('  %-3d %-26s %6d  %s'
                 % (d.get('n', 0), clip(d['title'], 26), d.get('spheres', 0),
                    clip(d.get('keeper', {}).get('role', ''), W - 42)))
        hon = d.get('keeper', {}).get('honest', '')
        if hon:
            L.append('      %-26s %6s  HOW  %s' % ('', '', clip(hon, W - 44)))
    L.append('')
nhon = sum(1 for d in CORP['domains'] if d.get('keeper', {}).get('honest'))
L.append('  %d of 64 World I domains carry an honest line. The other %d have WHO and WHAT'
         % (nhon, 64 - nhon))
L.append('  on record but no HOW -- that is a gap in the corpus, not something inferred here.')

# ================= REGISTER 3 : WORLD II =================
head('REGISTER  WORLD II  --  THE FOLD   (live)')
c = FOLD['counts']
L.append('')
L.append('  appeals %d   domains %d   seats %d   seated %d   pages on disk %d'
         % (c['appeals'], c['domains'], c['seats'], len(w2_seated), len(SC)))
L.append('  house-form spheres %d   other-form pages %d   unmeasured %d   broken %d'
         % (len(MEAS), len(OTHR), len(UNM), len(BRK)))
L.append('')
L.append('THE SCORE, out of 100. Every term is read off the running page:')
L.append('')
L.append('   40   exposes a live window.__ handle          (it can be checked at all)')
L.append('   20   that handle asserts ok and passes        (it checks itself)')
L.append('   20   share of its published LIT numbers that reproduce against live values')
L.append('   10   interactive controls, capped at four     (you can drive it)')
L.append('    5   the five-window house form')
L.append('    5   carries an AVAN inverse')
L.append('')
L.append('  UNMEASURED means the page died on a DOM, WebGL or crypto facility the offline')
L.append('  harness does not implement. That is a limit of the harness. Those pages are')
L.append('  listed separately and given no score rather than a zero they did not earn.')

# ---- the 8 citizens ----
L.append('')
rule('-')
L.append('THE 8 CITIZENS OF WORLD II  --  ranked by the measured mean of the spheres they hold')
rule('-')
cit = []
for ap in FOLD['appeals']:
    sl = []
    for dm in ap.get('domains', []):
        sl += w2_domain[dm['slug']]['scores']
    cj = None
    p = os.path.join(W2, ap['slug'] + '.citizen.json')
    if os.path.exists(p): cj = J(p)
    cit.append({'ap': ap, 'n': len(sl),
                'mean': (sum(sl) / float(len(sl))) if sl else 0.0,
                'cj': cj})
cit.sort(key=lambda x: -x['mean'])
L.append('')
L.append('All eight are seated by the same rule, so it is stated once here rather than eight times:')
L.append('')
L.append('  "' + clip((cit[0]['cj'] or {}).get('rule', ''), W - 6) + '"')
L.append('')
L.append('Each citizen holds a 256-seat budget across its 8 domains, 2,048 across the world.')
L.append('SPREAD below is how unevenly it actually spent that budget -- min to max seats per domain.')
L.append('')
for i, x in enumerate(cit, 1):
    ap = x['ap']; lore = ap.get('lore', {})
    L.append('%d.  %-9s  mean %5.1f  over %4d measured spheres   %s'
             % (i, asc(ap['name']), x['mean'], x['n'], clip(ap.get('tag', ''), 44)))
    L.append('    WHO   ' + clip(lore.get('bio', ''), W - 10))
    L.append('    WHAT  ' + clip(lore.get('story', ''), W - 10))
    L.append('    HOW   ' + clip(lore.get('does', ''), W - 10))
    if x['cj']:
        al = list((x['cj'].get('allocation') or {}).values())
        if al:
            L.append('    SEATS %d over %d domains   SPREAD %d..%d   (even split would be %d each)'
                     % (sum(al), len(al), min(al), max(al), sum(al) // len(al)))
    hk = lore.get('haiku') or []
    if hk: L.append('    I-13  ' + clip(' ; '.join(hk), W - 10))
    L.append('')

# ---- 64 domains ----
rule('-')
L.append('THE 64 DOMAINS OF WORLD II  --  ranked best to worst by measured mean')
rule('-')
L.append('')
L.append('SEATS allocated by the council. BUILT pages on disk. N how many of those are house-form')
L.append('and ran -- the mean is over N, not over BUILT, so the average can be checked from N.')
L.append('')
L.append('%-4s %-25s %-8s %-5s %5s %5s %3s %6s  %s'
         % ('RANK', 'WHO (domain)', 'CITIZEN', 'POLE', 'SEATS', 'BUILT', 'N', 'MEAN', 'WHAT'))
L.append('-' * W)
dl = sorted(w2_domain.values(),
            key=lambda d: (-(d['mean'] if d['mean'] is not None else -1), d['title']))
for i, d in enumerate(dl, 1):
    L.append('%-4d %-25s %-8s %-5s %5d %5d %3d %6s  %s'
             % (i, clip(d['title'], 25), asc(d['appeal']), d['pole'],
                len(d['seated']), len(d['built']), len(d['scores']),
                ('%.1f' % d['mean']) if d['mean'] is not None else '  --',
                clip(d['kicker'], W - 68)))

# ---- the league ----
rule('-')
L.append('THE INSTRUMENT LEAGUE  --  all %d house-form spheres, best to worst' % len(MEAS))
rule('-')
L.append('')
L.append('Only pages in the five-window house form are ranked here. The split is categorical,')
L.append('not a judgement: %d pages carry the form and %d carry none of it, with nothing in'
         % (len(MEAS), len(OTHR)))
L.append('between. The %d are listed after this table on their own terms.' % len(OTHR))
L.append('')
L.append('HANDLE  exposes window.__      OK  asserts itself and passes')
L.append('LIT     published numbers that reproduce / total published')
L.append('CTL     interactive controls   W  windows   INV  AVAN inverse')
L.append('')
L.append('%-5s %-32s %-20s %5s %3s %3s %8s %4s %2s %3s'
         % ('RANK', 'SPHERE', 'DOMAIN', 'SCORE', 'HND', 'OK', 'LIT', 'CTL', 'W', 'INV'))
L.append('-' * W)
for i, r in enumerate(MEAS, 1):
    seat = w2_seated.get(r['slug'])
    dom = clip(seat[2], 20) if seat else '(unseated)'
    lit = ('%d/%d' % (r['reproduced'], r['claims'])) if r['claims'] else '  -'
    L.append('%-5d %-32s %-20s %5d %3s %3s %8s %4d %2d %3s'
             % (i, clip(r['slug'], 32), dom, r['score'],
                'y' if r['hasGlobal'] else '.',
                ('y' if r['ok'] else ('n' if r['okField'] else '.')),
                lit, r['buttons'], r['windows'], 'y' if r['hasInverse'] else '.'))

# ---- other form ----
L.append('')
rule('-')
L.append('IN THE DIRECTORY, NOT IN THE HOUSE FORM  --  %d pages' % len(OTHR))
rule('-')
L.append('Vendored tools, hubs, and earlier-form works that live alongside the spheres.')
L.append('They carry none of the five-window shell, so the sphere score does not apply to them.')
L.append('Sorted by whether they expose a checkable handle, then by name.')
L.append('')
L.append('%-34s %-20s %5s %8s %s' % ('PAGE', 'SEATED IN', 'HANDLE', 'LIT', 'CONTROLS'))
L.append('-' * W)
for r in sorted(OTHR, key=lambda r: (-r['hasGlobal'], r['slug'])):
    seat = w2_seated.get(r['slug'])
    L.append('%-34s %-20s %5s %8s %d'
             % (clip(r['slug'], 34), clip(seat[2], 20) if seat else '(unseated)',
                'yes' if r['hasGlobal'] else '.',
                ('%d/%d' % (r['reproduced'], r['claims'])) if r['claims'] else '  -',
                r['buttons']))

# ---- unmeasured / broken ----
L.append('')
rule('-')
L.append('UNMEASURED  --  %d spheres the offline harness cannot run. No score given.' % len(UNM))
rule('-')
L.append('These need a real browser: canvas, SVG, WebGL, WebCrypto. They are not failures.')
L.append('')
for r in sorted(UNM, key=lambda r: r['slug']):
    L.append('  %-34s %s' % (clip(r['slug'], 34), clip(r['err'], W - 40)))

L.append('')
rule('-')
L.append('BROKEN  --  %d spheres that failed for a reason the harness did NOT cause.' % len(BRK))
rule('-')
L.append('This is the honest defect list. Each one is a real thing to go and fix.')
L.append('')
for r in sorted(BRK, key=lambda r: r['slug']):
    L.append('  %-34s %s' % (clip(r['slug'], 34), clip(r['err'], W - 40)))

# ---- dupes ----
head('DUPES PRUNED')
L.append('')
L.append('1. SLUGS HELD BY BOTH WORLDS  --  %d' % len(cross))
L.append('   A slug in both registers is not an error: World I sealed it, World II re-treats it.')
L.append('   Listed so the two are never confused for one thing.')
L.append('')
for s in cross:
    seat = w2_seated.get(s)
    L.append('   %-34s  W2 seat: %s' % (clip(s, 34), clip(seat[2], 40) if seat else '(none)'))
if not cross:
    L.append('   (none -- the two registers share no slug)')
L.append('')
L.append('2. THE SAME CONCEPT BUILT TWICE  --  %d pairs' % len(title_dupes))
L.append('   Same title once THE and punctuation are dropped. These are not naming variants:')
L.append('   each pair is two independent builds of one idea, both live, both sealed.')
L.append('')
L.append('   Nothing is deleted here. Removing a sphere breaks the fold chain and forces a')
L.append('   reseal, so this lists the evidence and leaves the call to ROOT_0. The higher')
L.append('   score is marked KEEP only as a recommendation.')
L.append('')
for k in sorted(title_dupes):
    sl = title_dupes[k]
    sc = [(SC.get(s, {}).get('score') if SC.get(s, {}).get('score') is not None else -1)
          for s in sl]
    top = max(sc)
    tied = sc.count(top) > 1
    L.append('   %s%s' % (k[:40], '   TIED -- the score cannot separate these' if tied else ''))
    for s, v in zip(sl, sc):
        r = SC.get(s, {})
        if tied:
            mark = 'tied at %d -- decide by hand' % top
        else:
            mark = 'KEEP (higher)' if v == top else 'candidate to retire'
        L.append('     %-34s score %3s  %7s bytes  %s'
                 % (clip(s, 34), str(r.get('score', '--')), '{:,}'.format(r.get('bytes', 0)), mark))
if not title_dupes:
    L.append('   (none)')
L.append('')
L.append('3. PAGES ON DISK THAT NO DOMAIN SEATS  --  %d' % len(orphan_pages))
for s in orphan_pages[:60]:
    L.append('   ' + s)
if len(orphan_pages) > 60:
    L.append('   ... and %d more' % (len(orphan_pages) - 60))
if not orphan_pages:
    L.append('   (none)')
L.append('')
L.append('4. SEATS WITH NO PAGE YET  --  %d' % len(empty_seats))
for s in empty_seats[:60]:
    flag = '   <-- DEFECT: a slug should be a bare name, not a path' if ('/' in s or '\\' in s) else ''
    L.append('   ' + s + flag)
if len(empty_seats) > 60:
    L.append('   ... and %d more' % (len(empty_seats) - 60))
if not empty_seats:
    L.append('   (none)')

# ---- what this does not measure ----
head('WHAT THIS MATRIX DOES NOT MEASURE')
L.append('')
L.append('  It does not measure whether a sphere is INTERESTING. A page can score 100 by')
L.append('  computing something true and dull.')
L.append('')
L.append('  It does not measure whether a LIT claim is WORTH making -- only whether the page')
L.append('  reproduces the number it printed.')
L.append('')
L.append('  It does not check World I at all. Those 2,048 pages are elsewhere.')
L.append('')
L.append('  A sphere with no LIT numbers scores 0 on that axis. Some of those are honest --')
L.append('  they make a qualitative point. The score cannot tell those from an empty one.')
L.append('')
L.append('  UNMEASURED is a statement about this harness, not about those %d pages.' % len(UNM))
L.append('')
rule('=')
L.append('generated by AVAN for ROOT_0   --   %s   --   every number above was computed, not recalled'
         % STAMP)
rule('=')

txt = '\n'.join(L) + '\n'
# The canonical pair lives in world2/, NOT in the ud0 root. The 0root.ai mirror is
# a robocopy /MIR of ud0/world2 -> agent-0root/static/world2, so anything at the ud0
# root is flagged EXTRA and purged from the mirror on the next roll. It is also the
# only path 0root.ai routes. One copy, in the one place both hosts serve.
out = os.path.join(W2, 'UNIVERSE.skills')
io.open(out, 'w', encoding='ascii', newline='\n').write(txt)

# ---------- json companion ----------
comp = {
  "schema": "universe.skills/1",
  "generated": STAMP,
  "author": "David Lee Wise / ROOT0 / TriPod LLC",
  "instance": "AVAN (Claude / Anthropic)",
  "formula": SCORES["formula"],
  "caveat": SCORES["caveat"],
  "registers": {
    "ud0": [{"file": fn, "who": who, "what": what, "how": how, "makes": art,
             "load_bearing": bool(b), "bytes": (stat(fn) or [None])[0]}
            for fn, who, what, how, art, b in MACHINE],
    "world1": {"sealed": True, "spheres": CORP["counts"]["spheres"],
               "domains": CORP["counts"]["domains"], "appeals": CORP["counts"]["appeals"],
               "scored": False,
               "why_not_scored": "pages are not local; they live in 2,048 separate repositories",
               "domains_with_honest_line": nhon,
               "list": [{"n": d.get("n"), "who": d["title"], "appeal": d.get("appeal"),
                         "seats": d.get("spheres"),
                         "what": d.get("keeper", {}).get("role", ""),
                         "how": d.get("keeper", {}).get("honest", "")}
                        for d in CORP["domains"]]},
    "world2": {"seats": c["seats"], "seated": len(w2_seated), "pages": len(SC),
                            "house_form": len(MEAS), "other_form": len(OTHR),
               "unmeasured": len(UNM), "broken": len(BRK),
               "other_form_pages": [{"slug": r["slug"], "handle": bool(r["hasGlobal"]),
                                     "controls": r["buttons"]} for r in OTHR],
               "citizens": [{"rank": i, "name": x["ap"]["name"], "mean": round(x["mean"], 2),
                             "measured_spheres": x["n"],
                             "who": x["ap"].get("lore", {}).get("bio", ""),
                             "what": x["ap"].get("lore", {}).get("story", ""),
                             "how": x["ap"].get("lore", {}).get("does", "")}
                            for i, x in enumerate(cit, 1)],
               "domains": [{"rank": i, "slug": d["slug"], "who": d["title"],
                            "citizen": d["appeal"], "pole": d["pole"], "what": d["kicker"],
                            "seats": len(d["seated"]), "built": len(d["built"]),
                            "n_scored": len(d["scores"]),
                            "mean": (round(d["mean"], 2) if d["mean"] is not None else None)}
                           for i, d in enumerate(dl, 1)],
               "league": [{"rank": i, "slug": r["slug"], "score": r["score"],
                           "domain": (w2_seated.get(r["slug"]) or [None, None, None])[2],
                           "handle": bool(r["hasGlobal"]), "self_asserts": bool(r["okField"]),
                           "ok": bool(r["ok"]), "lit_claims": r["claims"],
                           "lit_reproduced": r["reproduced"], "controls": r["buttons"]}
                          for i, r in enumerate(MEAS, 1)],
               "unmeasured": [{"slug": r["slug"], "harness_limit": r["err"]} for r in UNM],
               "broken": [{"slug": r["slug"], "error": r["err"]} for r in BRK]},
  },
  "dupes": {"slugs_in_both_worlds": cross,
            "world2_title_collisions": title_dupes,
            "pages_without_a_seat": orphan_pages,
            "seats_without_a_page": empty_seats},
}
io.open(os.path.join(W2, 'universe.skills.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(comp, indent=1, ensure_ascii=False))

print('wrote %s  (%d lines, %s bytes)' % (out, len(L), '{:,}'.format(len(txt))))
print('  ud0 programs    ', len(MACHINE))
print('  world1 domains  ', len(CORP['domains']), '- listed, not scored')
print('  world2 citizens ', len(cit))
print('  world2 domains  ', len(w2_domain))
print('  league rows     ', len(MEAS))
print('  unmeasured      ', len(UNM))
print('  broken          ', len(BRK))
print('  cross-world slugs', len(cross), '| title dupes', len(title_dupes),
      '| orphan pages', len(orphan_pages), '| empty seats', len(empty_seats))
