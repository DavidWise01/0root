#!/usr/bin/env node
// _seam_gate.js — the WORLD II seam gate.
//
// The problem (named by David's seamgate.py, 2026-08-04): a project computes numbers,
// writes them somewhere, and a separate step bakes them into a published artifact.
// The compute side is gated; the render side is not. So the artifact can assert a number
// its own source no longer agrees with, and nothing in the pipeline notices.
//
// In WORLD II the seam is exactly this: each sphere's W1 "LIT" paragraph asserts numbers
// ("0.1246", "206 of 1,353", "1e-9") that are supposed to be what the page's own
// window.__X selftest produces. Nothing checked that. Twice in one session the published
// number and the live number disagreed, caught only by hand.
//
// This gate runs every sphere's REAL page script headlessly (stubbed DOM), harvests the
// live selftest object, extracts the numeric claims from the LIT prose, and reports any
// claim that cannot be reproduced from the live values.
//
// It is a SCREEN, not a proof: cited literature numbers (dates, other people's results)
// legitimately appear in LIT and will not match a selftest value. Those are reported as
// UNMATCHED for human eyes, not as failures. Only a claim that *looks* like a measurement
// and contradicts a live value is a DRIFT.
//
// Usage:
//   node _seam_gate.js                 # sweep every sphere
//   node _seam_gate.js the-heilbronn   # one sphere
//   node _seam_gate.js --last 40       # newest 40 pages by mtime
//
// Exit: 0 = no drift, 1 = drift found, 3 = could not run.

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const DIR = path.join(__dirname, 'ud0', 'world2');

// ---------- a DOM stub good enough to run a sphere page script ----------
function makeContextStub() {
  const noop = () => {};
  const ctx = new Proxy({}, {
    get(t, k) {
      if (k === 'canvas') return { width: 512, height: 360 };
      if (k === 'measureText') return () => ({ width: 10 });
      if (k === 'createLinearGradient' || k === 'createRadialGradient')
        return () => ({ addColorStop: noop });
      if (k === 'getImageData') return () => ({ data: new Uint8ClampedArray(4) });
      return noop;
    },
    set() { return true; }
  });
  return ctx;
}

function makeSandbox() {
  const ctx = makeContextStub();
  const el = new Proxy({
    width: 512, height: 360,
    getContext: () => ctx,
    addEventListener: () => {},
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 512, height: 360 }),
    style: {}, textContent: '', className: '', dataset: {}
  }, {
    get(t, k) {
      if (k in t) return t[k];
      return undefined;               // onclick etc. assignable, readable as undefined
    },
    set(t, k, v) { t[k] = v; return true; }
  });
  const win = {};
  const sandbox = {
    window: win,
    document: {
      getElementById: () => el,
      querySelector: () => el,
      querySelectorAll: () => [],
      createElement: () => el,
      addEventListener: () => {},
      body: el
    },
    requestAnimationFrame: () => 0,     // never actually animate
    cancelAnimationFrame: () => {},
    setTimeout: () => 0,
    clearTimeout: () => {},
    setInterval: () => 0,
    clearInterval: () => {},
    innerWidth: 1280, innerHeight: 800, devicePixelRatio: 1,
    addEventListener: () => {}, removeEventListener: () => {},
    location: { href: '', hash: '', search: '' },
    navigator: { userAgent: 'seamgate' },
    performance: { now: () => 0 },
    localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
    fetch: () => ({ then: () => ({ then: () => ({ catch: () => {} }), catch: () => {} }), catch: () => {} }),
    alert: () => {}, matchMedia: () => ({ matches: false, addEventListener: () => {} }),
    getComputedStyle: () => ({ getPropertyValue: () => '' }),
    console: { log: () => {}, warn: () => {}, error: () => {} },
    Math, JSON, Number, String, Array, Object, Boolean, Date, RegExp, Error,
    isFinite, isNaN, parseFloat, parseInt, Set, Map, Symbol, BigInt,
    Uint8ClampedArray, Float64Array, Int32Array, Uint32Array, Proxy, Reflect
  };
  sandbox.globalThis = sandbox;
  sandbox.self = sandbox;
  ['innerWidth','innerHeight','devicePixelRatio','addEventListener','removeEventListener',
   'location','navigator','performance','localStorage','requestAnimationFrame',
   'cancelAnimationFrame','setTimeout','matchMedia','getComputedStyle','document']
   .forEach(function(k){ win[k]=sandbox[k]; });
  return { sandbox, win };
}

// ---------- extract the page script + the LIT paragraph ----------
function readSphere(file) {
  const html = fs.readFileSync(file, 'utf8');
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  // the sphere's instrument is the LAST inline script (earlier ones are shell/nav)
  const script = scripts.length ? scripts[scripts.length - 1] : null;
  // LIT run: <span class="lit">LIT</span> ... up to <span class="fig"> or </div>
  const litM = html.match(/<span class="lit">LIT<\/span>([\s\S]*?)(?:<span class="fig">|<\/div>)/);
  const lit = litM ? litM[1].replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;|&#\d+;/g, ' ') : '';
  return { html, script, lit };
}

// ---------- harvest the live selftest values ----------
function runScript(script) {
  const { sandbox, win } = makeSandbox();
  const ctxObj = vm.createContext(sandbox);
  try {
    vm.runInContext(script, ctxObj, { timeout: 20000 });
  } catch (e) {
    return { error: e.message.slice(0, 120) };
  }
  const globals = {};
  for (const k of Object.keys(win)) if (k.startsWith('__')) globals[k] = win[k];
  return { globals };
}

function flatten(obj, out, depth) {
  out = out || [];
  depth = depth || 0;
  if (depth > 4 || obj == null) return out;
  if (typeof obj === 'number') { out.push(obj); return out; }
  if (typeof obj === 'boolean' || typeof obj === 'string') return out;
  if (Array.isArray(obj)) { obj.forEach(v => flatten(v, out, depth + 1)); return out; }
  if (typeof obj === 'object') { Object.keys(obj).forEach(k => flatten(obj[k], out, depth + 1)); return out; }
  return out;
}

// ---------- pull numeric claims out of the LIT prose ----------
// Only claims that read like MEASUREMENTS: decimals, scientific notation, percentages,
// and "N of M" counts. Bare years and small integers are skipped (citations, counts of
// authors, etc.) — this gate reports, it does not nag.
function litClaims(lit) {
  const claims = [];
  const push = (raw, val, kind) => { if (isFinite(val)) claims.push({ raw, val, kind }); };
  // scientific notation, incl. unicode minus/superscript forms already stripped to text
  for (const m of lit.matchAll(/(\d+(?:\.\d+)?)\s*(?:e|E|×10\^?)\s*[-−]?\s*(\d+)/g))
    push(m[0], parseFloat(m[1]) * Math.pow(10, -parseInt(m[2], 10)), 'sci');
  // 10^-k  written as 10⁻⁹ etc. is stripped by entity removal; catch "1e-9"
  for (const m of lit.matchAll(/\b\d+\.\d{2,}\b/g)) push(m[0], parseFloat(m[0]), 'decimal');
  const pctRaw = new Set();
  for (const m of lit.matchAll(/(\d+(?:\.\d+)?)\s*%/g)) { pctRaw.add(m[1]); push(m[0], parseFloat(m[1]), 'percent'); }
  // a bare decimal that is just the number part of a percent claim is the SAME claim
  for (let i = claims.length - 1; i >= 0; i--)
    if (claims[i].kind === 'decimal' && pctRaw.has(claims[i].raw)) claims.splice(i, 1);
  for (const m of lit.matchAll(/\b(\d[\d,]{1,9})\s+of\s+(\d[\d,]{1,9})\b/g)) {
    push(m[0], parseFloat(m[1].replace(/,/g, '')), 'count');
    push(m[0], parseFloat(m[2].replace(/,/g, '')), 'count');
  }
  return claims;
}

function reproduces(claim, values) {
  const v = claim.val;
  for (const x of values) {
    if (!isFinite(x)) continue;
    if (x === v) return true;
    const a = Math.abs(x), b = Math.abs(v);
    // decimals: match if the claim is x rounded to the claim's own precision
    const dec = (String(claim.raw).split('.')[1] || '').replace(/[^\d].*$/, '').length;
    if (dec > 0 && Math.abs(x - v) <= 0.5 * Math.pow(10, -dec) * 1.001) return true;
    if (claim.kind === 'percent' && Math.abs(x * 100 - v) <= 0.5) return true;
    if (b > 0 && Math.abs(a - b) / Math.max(b, 1e-30) < 0.02) return true;      // 2% band
    if (claim.kind === 'sci' && a > 0 && b > 0 && a <= b * 1.5) return true;    // "< 1e-9" style bounds
  }
  return false;
}

// ---------- main ----------
function main() {
  const args = process.argv.slice(2);
  let files = fs.readdirSync(DIR).filter(f => /^the-[a-z0-9-]+\.html$/.test(f));
  if (args.length && !args[0].startsWith('--')) {
    const want = args[0].replace(/\.html$/, '') + '.html';
    files = files.filter(f => f === want);
  } else if (args[0] === '--last') {
    const n = parseInt(args[1] || '40', 10);
    files = files
      .map(f => ({ f, t: fs.statSync(path.join(DIR, f)).mtimeMs }))
      .sort((a, b) => b.t - a.t).slice(0, n).map(o => o.f);
  }
  if (!files.length) { console.error('no sphere pages matched'); process.exit(3); }

  const VERBOSE = args.includes('-v') || args.includes('--verbose');
  const VERBOSE_ROWS = [];
  let ran = 0, noGlobal = 0, failedRun = 0, drift = 0, unmatched = 0, okFlagFalse = 0;
  let totalClaims = 0;
  const driftRows = [], unmatchedRows = [], badRows = [];

  for (const f of files) {
    const slug = f.replace(/\.html$/, '');
    let s;
    try { s = readSphere(path.join(DIR, f)); } catch (e) { continue; }
    if (!s.script) { continue; }
    const r = runScript(s.script);
    if (r.error) { failedRun++; badRows.push([slug, 'RUN ERROR: ' + r.error]); continue; }
    const keys = Object.keys(r.globals || {});
    if (!keys.length) { noGlobal++; badRows.push([slug, 'no window.__X global produced']); continue; }
    ran++;
    const obj = r.globals[keys[0]];
    // the sphere's own honesty flag
    if (obj && typeof obj === 'object' && obj.ok === false) {
      okFlagFalse++; badRows.push([slug, 'selftest reports ok:false']);
    }
    const values = flatten(obj);
    const claims = litClaims(s.lit);
    totalClaims += claims.length;
    if (VERBOSE) VERBOSE_ROWS.push(slug + '  claims=[' + claims.map(c => c.raw).join(' | ') +
      ']  live=[' + values.slice(0, 12).map(x => (typeof x === 'number' ? (Math.abs(x) < 1e-4 && x !== 0 ? x.toExponential(1) : +x.toFixed(6)) : x)).join(' ') + ']');
    for (const c of claims) {
      if (reproduces(c, values)) continue;
      // A claim that names a value CLOSE to a live one but not equal is DRIFT.
      // A claim with no nearby live value at all is more likely a citation → UNMATCHED.
      let near = false;
      for (const x of values) {
        if (!isFinite(x) || x === 0) continue;
        const ratio = Math.abs(c.val) / Math.abs(x);
        if (ratio > 0.5 && ratio < 2 && Math.abs(c.val - x) > 1e-12) { near = true; break; }
      }
      if (near) { drift++; driftRows.push([slug, c.raw, c.val]); }
      else { unmatched++; unmatchedRows.push([slug, c.raw]); }
    }
  }

  if (VERBOSE) {
    console.log('--- verbose: claims vs live values ---');
    VERBOSE_ROWS.forEach(r => console.log('  ' + r));
  }
  console.log('=== WORLD II SEAM GATE ===');
  console.log('pages swept       : ' + files.length);
  console.log('numeric claims    : ' + totalClaims + '   (extracted from LIT prose)');
  console.log('selftests run     : ' + ran);
  console.log('no __X global     : ' + noGlobal);
  console.log('script run errors : ' + failedRun);
  console.log('selftest ok:false : ' + okFlagFalse);
  console.log('DRIFT claims      : ' + drift + '   (published number contradicts a live value)');
  console.log('unmatched claims  : ' + unmatched + '   (likely cited literature — human review)');

  if (badRows.length) {
    console.log('\n--- pages needing attention ---');
    badRows.slice(0, 40).forEach(r => console.log('  ' + r[0].padEnd(30) + r[1]));
    if (badRows.length > 40) console.log('  ... +' + (badRows.length - 40) + ' more');
  }
  if (driftRows.length) {
    console.log('\n--- DRIFT (published vs live) ---');
    driftRows.slice(0, 60).forEach(r => console.log('  ' + r[0].padEnd(30) + 'claims "' + r[1] + '"'));
    if (driftRows.length > 60) console.log('  ... +' + (driftRows.length - 60) + ' more');
  }
  process.exit(drift > 0 || failedRun > 0 ? 1 : 0);
}

main();
