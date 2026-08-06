// Score every World II sphere on measurable properties only.
//
// Reuses the seam gate's own reader and sandbox. Two rules keep this honest:
//
//  1. The sandbox is a thin DOM stub, not a browser. A page that dies on
//     `appendChild is not a function` or `THREE is not defined` is telling me my
//     harness is thin, not that the page is broken. Those are marked UNMEASURED
//     and ranked separately -- scoring them zero would be scoring my own stub.
//  2. A missing `ok` field is not a failing `ok`. Recorded as three states.
//
// Nothing subjective goes into the score; the formula is written into the output.
const fs = require('fs');
const path = require('path');
const G = require('./_seam_gate.js');

const DIR = path.join(__dirname, 'ud0', 'world2');
const NOT = /^(index|fold|fold-chain|atlas|roster)\b/;

// A failure is the harness's fault when it names a DOM / graphics / encoding
// facility the stub does not implement.
const SANDBOX = /appendChild|querySelector|createElementNS|getAttribute|fillText|insertBefore|removeChild|setAttribute|createElement|innerHTML|classList|addEventListener|getContext|THREE is not defined|TextEncoder|TextDecoder|shader compile|crypto|requestAnimationFrame|getComputedStyle|ResizeObserver/i;

const files = fs.readdirSync(DIR)
  .filter(f => /^[a-z0-9][a-z0-9-]*\.html$/.test(f) && !NOT.test(f));

const out = [];
for (const f of files) {
  const slug = f.replace(/\.html$/, '');
  const raw = fs.readFileSync(path.join(DIR, f), 'utf8');
  const rec = {
    slug,
    bytes: raw.length,
    canvases: (raw.match(/<canvas\b/g) || []).length,
    buttons: (raw.match(/<button\b/g) || []).length,
    hasInverse: /AVAN&rsquo;s addition|AVAN’s addition/.test(raw) ? 1 : 0,
    windows: (raw.match(/class="win"/g) || []).length,
    hasGlobal: 0, okField: 0, ok: 0, okFalse: 0,
    claims: 0, reproduced: 0, drift: 0, unmatched: 0,
    status: 'MEASURED', err: null
  };

  let sp;
  try { sp = G.readSphere(path.join(DIR, f)); }
  catch (e) { rec.status = 'BROKEN'; rec.err = 'unreadable'; out.push(rec); continue; }
  if (!sp.script) { rec.status = 'BROKEN'; rec.err = 'ships no script'; out.push(rec); continue; }

  const r = G.runScript(sp.script);
  if (r.error) {
    rec.err = r.error;
    rec.status = SANDBOX.test(r.error) ? 'UNMEASURED' : 'BROKEN';
    out.push(rec); continue;
  }
  const keys = Object.keys(r.globals || {});
  if (!keys.length) { rec.err = 'exposes no window.__ handle'; out.push(rec); continue; }

  rec.hasGlobal = 1;
  const obj = r.globals[keys[0]];
  rec.global = keys[0];
  if (obj && typeof obj === 'object' && 'ok' in obj) {
    rec.okField = 1;
    rec.ok = obj.ok === true ? 1 : 0;
    rec.okFalse = obj.ok === false ? 1 : 0;
  }

  const values = G.flatten(obj);
  const claims = G.litClaims(sp.lit || '');
  rec.claims = claims.length;
  for (const c of claims) {
    if (G.reproduces(c, values)) { rec.reproduced++; continue; }
    let near = false;
    const lo = c.kind === 'intcount' ? 0.9 : 0.5;
    const hi = c.kind === 'intcount' ? 1.1 : 2;
    for (const x of values) {
      if (!isFinite(x) || x === 0) continue;
      const ratio = Math.abs(c.val) / Math.abs(x);
      if (ratio > lo && ratio < hi && Math.abs(c.val - x) > 1e-12) { near = true; break; }
    }
    if (near) rec.drift++; else rec.unmatched++;
  }
  out.push(rec);
}

// ---- the score, out of 100. Every term is measured; none is taste. ----
// 40  exposes a live handle (it can be checked at all)
// 20  that handle asserts its own correctness and passes
// 20  share of its published LIT numbers that reproduce against live values
// 10  interactive controls, capped at 4
//  5  the five-window house form
//  5  carries an AVAN inverse
for (const r of out) {
  if (r.status === 'UNMEASURED') { r.score = null; continue; }
  const claimShare = r.claims ? r.reproduced / r.claims : 0;
  r.claimShare = +claimShare.toFixed(3);
  r.score = Math.round(
    40 * r.hasGlobal +
    20 * r.ok +
    20 * claimShare +
    10 * Math.min(1, r.buttons / 4) +
     5 * (r.windows >= 5 ? 1 : r.windows / 5) +
     5 * r.hasInverse
  );
}

const measured = out.filter(r => r.status === 'MEASURED');
const unmeasured = out.filter(r => r.status === 'UNMEASURED');
const broken = out.filter(r => r.status === 'BROKEN');

measured.sort((a, b) => b.score - a.score || b.reproduced - a.reproduced || a.slug.localeCompare(b.slug));

fs.writeFileSync(path.join(__dirname, '_skills_scores.json'), JSON.stringify({
  formula: '40 live handle + 20 self-assert passes + 20 LIT reproduction + 10 controls(cap 4) + 5 five-window + 5 AVAN inverse',
  caveat: 'UNMEASURED = died on a DOM/WebGL/crypto facility the offline stub lacks. That is a limit of the harness, not a verdict on the page.',
  pages: out.length,
  measured: measured.length,
  unmeasured: unmeasured.length,
  broken: broken.length,
  withHandle: measured.filter(r => r.hasGlobal).length,
  selfAsserting: measured.filter(r => r.okField).length,
  okTrue: measured.filter(r => r.ok).length,
  okFalse: measured.filter(r => r.okFalse).length,
  spheres: measured.concat(unmeasured, broken)
}, null, 1));

const P = (n, d) => (100 * n / d).toFixed(1) + '%';
console.log('pages           :', out.length);
console.log('  MEASURED      :', measured.length);
console.log('  UNMEASURED    :', unmeasured.length, '(harness stub too thin)');
console.log('  BROKEN        :', broken.length);
console.log('of the measured:');
console.log('  live handle   :', measured.filter(r => r.hasGlobal).length, P(measured.filter(r => r.hasGlobal).length, measured.length));
console.log('  self-asserting:', measured.filter(r => r.okField).length);
console.log('    ok true     :', measured.filter(r => r.ok).length);
console.log('    ok false    :', measured.filter(r => r.okFalse).length);
console.log('  no handle     :', measured.filter(r => !r.hasGlobal).length);
console.log('score  top', measured[0].score, measured[0].slug, '| median', measured[Math.floor(measured.length/2)].score);
console.log('\nBROKEN list:');
for (const b of broken) console.log('  ', b.slug, '--', (b.err || '').slice(0, 70));
