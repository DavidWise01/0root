// Verification for the batch-261 render kit.
//
// The kit is a string of JS that will be concatenated after NOIR inside every
// sphere script. It draws; it must never touch a number. So the test does two
// things: run each helper against a RECORDING canvas stub and assert on the exact
// calls it emitted, and prove the helpers are pure with respect to their inputs.
const fs = require('fs');
const path = require('path');

// pull KIT out of the python source the same way the generator will see it
const src = fs.readFileSync(path.join(__dirname, '_world2_spheres.py'), 'utf8');
const m = src.match(/KIT = """([\s\S]*?)"""/);
if (!m) { console.log('FAIL: could not extract KIT from _world2_spheres.py'); process.exit(1); }
const KIT = m[1];

// ---- recording 2d context ----
function rec() {
  const calls = [];
  const g = {
    calls,
    fillStyle: '', strokeStyle: '', font: '', lineWidth: 0,
    shadowColor: '', shadowBlur: 0, lineCap: '', lineJoin: '',
    fillRect: (x, y, w, h) => calls.push(['fillRect', x, y, w, h]),
    fillText: (t, x, y) => calls.push(['fillText', t, x, y]),
    beginPath: () => calls.push(['beginPath']),
    moveTo: (x, y) => calls.push(['moveTo', x, y]),
    lineTo: (x, y) => calls.push(['lineTo', x, y]),
    stroke: () => calls.push(['stroke']),
    arc: (x, y, r) => calls.push(['arc', x, y, r]),
    fill: () => calls.push(['fill']),
    createLinearGradient: () => ({ addColorStop: () => {} }),
    createRadialGradient: () => ({ addColorStop: () => {} }),
  };
  return g;
}

const NOIRSTUB =
  'function nb(){}function ne(g,c,w){g.strokeStyle=c;g.lineWidth=w||2;}' +
  'function nf(g,c){g.fillStyle=c;}function ng(g){}' +
  'function nt(g,c,x,y,s,t){g.fillText(t,x,y);}' +
  'function ndot(g,x,y,r,c){g.arc(x,y,r);g.fill();}';

const K = new Function('return (function(){' + NOIRSTUB + KIT +
  'return {kfmt:kfmt,krow:krow,kpair:kpair,kcurve:kcurve,kgrid:kgrid,' +
  'korb:korb,kring:kring,kbits:kbits,kverdict:kverdict,kout:kout};})()')();

let pass = 0, fail = 0;
function ok(name, cond, detail) {
  if (cond) { pass++; console.log('  pass  ' + name); }
  else { fail++; console.log('  FAIL  ' + name + (detail ? '  -- ' + detail : '')); }
}

console.log('=== A. every helper is defined and callable ===');
for (const n of ['kfmt','krow','kpair','kcurve','kgrid','korb','kring','kbits','kverdict','kout'])
  ok(n + ' defined', typeof K[n] === 'function');

console.log('\n=== B. kfmt formats without inventing precision ===');
ok('integer gets separators', K.kfmt(1234567) === (1234567).toLocaleString());
ok('float rounds to 3dp', K.kfmt(1.23456789) === '1.235', 'got ' + K.kfmt(1.23456789));
ok('exact float keeps value', K.kfmt(0.5) === '0.5', 'got ' + K.kfmt(0.5));
ok('zero survives', K.kfmt(0) === (0).toLocaleString());
ok('negative survives', K.kfmt(-42) === (-42).toLocaleString());
ok('string passes through', K.kfmt('abc') === 'abc');
ok('does not round integers', K.kfmt(1563) === (1563).toLocaleString());

console.log('\n=== C. krow draws a track and a fill of the right width ===');
(function () {
  const g = rec();
  K.krow(g, 10, 20, 300, 'label', 1563, 0.5, 'green');
  const rects = g.calls.filter(c => c[0] === 'fillRect');
  ok('two rects (track + fill)', rects.length === 2, 'got ' + rects.length);
  ok('track is full width', rects[0][3] === 300, 'got ' + rects[0][3]);
  ok('fill is half width', rects[1][3] === 150, 'got ' + rects[1][3]);
  const texts = g.calls.filter(c => c[0] === 'fillText').map(c => c[1]);
  ok('label drawn', texts.indexOf('label') >= 0);
  ok('value drawn via kfmt', texts.indexOf((1563).toLocaleString()) >= 0, texts.join('|'));
})();

console.log('\n=== D. krow clamps rather than drawing off the end ===');
(function () {
  const over = rec(), under = rec();
  K.krow(over, 0, 0, 200, 'x', 1, 5.0, 'c');
  K.krow(under, 0, 0, 200, 'x', 1, -3.0, 'c');
  const o = over.calls.filter(c => c[0] === 'fillRect')[1][3];
  const u = under.calls.filter(c => c[0] === 'fillRect')[1][3];
  ok('frac > 1 clamps to width', o === 200, 'got ' + o);
  ok('frac < 0 clamps to minimum 2', u === 2, 'got ' + u);
})();

console.log('\n=== E. kcurve reports the true range of the function it sampled ===');
(function () {
  const g = rec();
  const r = K.kcurve(g, 0, 0, 100, 50, 100, t => t * 10 - 3, 'c', 1);
  ok('min is exact', Math.abs(r.min - (-3)) < 1e-9, 'got ' + r.min);
  ok('max is exact', Math.abs(r.max - 7) < 1e-9, 'got ' + r.max);
  const pts = g.calls.filter(c => c[0] === 'moveTo' || c[0] === 'lineTo');
  ok('n+1 points plotted', pts.length === 101, 'got ' + pts.length);
  ok('first is a moveTo', g.calls.filter(c => c[0] === 'moveTo').length === 1);
})();

console.log('\n=== F. kcurve survives a flat function (no divide by zero) ===');
(function () {
  const g = rec();
  const r = K.kcurve(g, 0, 0, 100, 50, 20, () => 7, 'c', 1);
  const pts = g.calls.filter(c => c[0] === 'moveTo' || c[0] === 'lineTo');
  const finite = pts.every(p => isFinite(p[1]) && isFinite(p[2]));
  ok('constant function does not produce NaN', finite);
  ok('min equals max input', Math.abs(r.min - 7) < 1e-9);
})();

console.log('\n=== G. kgrid draws exactly one cell per non-null colour ===');
(function () {
  const g = rec();
  K.kgrid(g, 0, 0, 10, 4, 5, 5, i => (i % 3 === 0 ? null : 'c'));
  const rects = g.calls.filter(c => c[0] === 'fillRect').length;
  let expect = 0;
  for (let i = 0; i < 40; i++) if (i % 3 !== 0) expect++;
  ok('skips null cells', rects === expect, 'got ' + rects + ' expected ' + expect);
})();

console.log('\n=== H. kbits renders the bit pattern, MSB first ===');
(function () {
  const g = rec();
  K.kbits(g, 0x80000000, 0, 0, 4, 'ON', 'OFF', 32);
  const rects = g.calls.filter(c => c[0] === 'fillRect');
  ok('32 cells', rects.length === 32, 'got ' + rects.length);
  const g2 = rec();
  const seen = [];
  g2.fillRect = () => seen.push(g2.fillStyle);
  K.kbits(g2, 0x80000000, 0, 0, 4, 'ON', 'OFF', 32);
  ok('top bit is first and set', seen[0] === 'ON', 'got ' + seen[0]);
  ok('remaining bits clear', seen.slice(1).every(s => s === 'OFF'));
  const g3 = rec(); const seen3 = [];
  g3.fillRect = () => seen3.push(g3.fillStyle);
  K.kbits(g3, 1, 0, 0, 4, 'ON', 'OFF', 32);
  ok('bit 0 lands last', seen3[31] === 'ON', 'got ' + seen3[31]);
})();

console.log('\n=== I. korb skips nulls and projects finite coordinates ===');
(function () {
  const g = rec();
  K.korb(g, 100, 100, 37, 20, (i) => (i % 4 === 0 ? null : { x: i, z: -i, y: 3, c: 'c' }));
  const arcs = g.calls.filter(c => c[0] === 'arc');
  ok('15 of 20 drawn', arcs.length === 15, 'got ' + arcs.length);
  ok('all coordinates finite', arcs.every(a => isFinite(a[1]) && isFinite(a[2])));
})();

console.log('\n=== J. kverdict picks its colour from the verdict, not the text ===');
(function () {
  const good = rec(), bad = rec(); const gs = [], bs = [];
  good.fillRect = () => gs.push(good.fillStyle);
  bad.fillRect = () => bs.push(bad.fillStyle);
  K.kverdict(good, 0, 0, 100, true, 'fine');
  K.kverdict(bad, 0, 0, 100, false, 'fine');
  ok('true is the green fill', /125,226,176/.test(gs[0]), gs[0]);
  ok('false is the red fill', /255,60,90/.test(bs[0]), bs[0]);
})();

console.log('\n=== K. the kit never mutates its inputs ===');
(function () {
  const g = rec();
  const pt = { x: 5, z: 6, y: 7, c: 'c', r: 2 };
  const before = JSON.stringify(pt);
  K.korb(g, 0, 0, 10, 1, () => pt);
  ok('korb leaves the point object alone', JSON.stringify(pt) === before);
  const n = 1563;
  K.kfmt(n);
  ok('kfmt is pure', n === 1563);
})();

console.log('\n=== L. house-rule compliance of the KIT source itself ===');
ok('no Date.now', KIT.indexOf('Date.now') < 0);
ok('no Math.random', KIT.indexOf('Math.random') < 0);
ok('ASCII only', [...KIT].every(c => c.charCodeAt(0) < 127));
ok('no python-eaten escapes', !/\\[uUxN]/.test(KIT));
ok('balanced braces', (KIT.match(/\{/g) || []).length === (KIT.match(/\}/g) || []).length);
ok('every line has even quotes',
   KIT.split('\n').every(l => (l.match(/'/g) || []).length % 2 === 0));

console.log('\n' + pass + ' pass, ' + fail + ' fail');
process.exit(fail ? 1 : 0);
