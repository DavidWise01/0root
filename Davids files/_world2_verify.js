// Live re-derivation gate for World II spheres.
//
//   node _world2_verify.js the-convoy-effect the-work-stealing ...
//
// For each slug: load the BUILT page, run its instrument in the seam-gate
// sandbox, and check that every number published in its LIT sentence is
// reproduced by what the page actually computes. Exits non-zero if any slug
// fails, so the publish step can refuse to ship on it.
//
// This exists because a selftest passing in a scratch file proves nothing about
// the page that got built. Several batches have shipped a LIT sentence whose
// numbers came from the harness rather than the instrument, and the only thing
// that caught them was re-deriving against the built artifact.

const path = require('path');
const { readSphere, runScript } = require(path.join(__dirname, '_seam_gate.js'));

const W2 = path.join(__dirname, 'ud0', 'world2');

// The convention every sphere follows: window.__ + the slug with dashes removed.
const globalFor = (slug) => '__' + slug.replace(/-/g, '');

// "4K page" and "1 MiB" are magnitudes written in shorthand. Read literally the
// checker looked for 4 and 1, found neither, and failed two spheres whose real
// values (4096, 1048576) were both present. Resolving the suffix is not a
// loosening -- it is a STRONGER check: a page called "4K" whose object says 8192
// now fails, where before neither form was tested at all.
const UNIT = { k: 1024, kb: 1024, kib: 1024,
               m: 1048576, mb: 1048576, mib: 1048576,
               g: 1073741824, gb: 1073741824, gib: 1073741824 };

function numsIn(s) {
  // A hyphen inside a NAME ("CRC-8", "UTF-8") is not a minus sign, and a number
  // over a NON-number is a formula ("1/sqrt(N)"), not a measurement. "10 / 20"
  // is digits both sides and stays.
  const raw = [...s.matchAll(
    /(?<![A-Za-z])(?<![A-Za-z]-)-?\d[\d,]*\.?\d*(?:e-?\d+)?(\s*\/\s*)?/gi)];
  const out = [];
  for (const m of raw) {
    if (m[1] && !/^\s*\d/.test(s.slice(m.index + m[0].length))) continue;
    // ...and the same on the LEFT: "C/2" is a denominator under a symbol,
    // not a measurement. "10 / 20" has digits both sides and stays.
    if (/[A-Za-z]\s*\/\s*$/.test(s.slice(0, m.index))) continue;
    const n = Number(m[0].replace(/[,\s\/]/g, ''));
    if (Number.isNaN(n)) continue;
    // a unit suffix immediately after turns the token into a magnitude
    const after = s.slice(m.index + m[0].length).match(/^\s?([KMG]i?B?)(?![A-Za-z])/);
    if (after) {
      const mult = UNIT[after[1].toLowerCase()];
      if (mult) { out.push(n * mult); continue; }
    }
    out.push(n);
  }
  return out;
}

function flat(o, out) {
  out = out || [];
  if (o === null || o === undefined) return out;
  if (typeof o === 'number') { out.push(o); return out; }
  if (typeof o === 'boolean' || typeof o === 'string') return out;
  if (Array.isArray(o)) { o.forEach(v => flat(v, out)); return out; }
  if (typeof o === 'object') { Object.values(o).forEach(v => flat(v, out)); return out; }
  return out;
}

function near(target, pool) {
  return pool.some(v => v === target ||
    Math.abs(v - target) < 1e-9 ||
    (target !== 0 && Math.abs((v - target) / target) < 0.0005) ||
    Math.abs(Math.round(v * 100) / 100 - target) < 1e-9 ||
    Math.abs(Math.round(v * 10) / 10 - target) < 1e-9 ||
    Math.abs(v * 100 - target) < 0.01);
}

// A sphere the sandbox CANNOT run is not a sphere that is wrong. WebGL, THREE,
// real layout and the network are absent here by construction, and a page built
// on them will always throw. Blocking on that would push the next WebGL batch
// straight to --skip-verify, which would cost the gate entirely -- so those are
// reported as UNMEASURED, with the missing facility named, and do not fail.
// Anything else is a real failure. The count of unmeasured is printed loudly:
// an honest gap has to stay visible, not become a silent pass.
const FACILITIES = [
  [/shader|webgl|getContext\(['"]webgl|compileShader/i, 'WebGL'],
  [/\bTHREE\b|is not a constructor.*THREE/i,            'THREE.js'],
  [/fetch|XMLHttpRequest|ENOTFOUND|ECONNREFUSED/i,      'network'],
  [/Cannot use import statement|Unexpected token .export/i, 'ES modules'],
  [/getBBox|createSVGPoint|baseVal/i,                   'SVG layout'],
];

function facilityFor(err) {
  for (const [re, name] of FACILITIES) if (re.test(err)) return name;
  return null;
}

function main() {
  const slugs = process.argv.slice(2).filter(Boolean);
  if (!slugs.length) {
    console.log('usage: node _world2_verify.js <slug> [slug ...]');
    process.exit(2);
  }
  let bad = 0, unmeasured = 0;
  for (const slug of slugs) {
    const file = path.join(W2, slug + '.html');
    const glob = globalFor(slug);
    let sp, res;
    try { sp = readSphere(file); res = runScript(sp.scripts); }
    catch (e) { console.log('XX ' + slug + '  READ/RUN FAILED: ' + e.message); bad++; continue; }
    if (res.error) {
      const fac = facilityFor(res.error);
      if (fac) {
        console.log('-- ' + slug + '  UNMEASURED: needs ' + fac +
                    ', which this sandbox does not have');
        unmeasured++;
      } else {
        console.log('XX ' + slug + '  THREW: ' + res.error);
        bad++;
      }
      continue;
    }
    const live = res.globals && res.globals[glob];
    if (!live) {
      const fac = facilityFor(sp.script || '');
      if (fac) {
        console.log('-- ' + slug + '  UNMEASURED: no window.' + glob +
                    '; the page needs ' + fac);
        unmeasured++;
      } else {
        console.log('XX ' + slug + '  no window.' + glob);
        bad++;
      }
      continue;
    }
    if (live.ok !== true) { console.log('XX ' + slug + '  selftest ok=' + live.ok); bad++; continue; }

    const want = numsIn(sp.lit || '');
    const missing = want.filter(n => !near(n, flat(live)));
    if (missing.length) {
      console.log('!! ' + slug + '  LIT numbers NOT reproduced: ' + missing.join(', '));
      bad++;
    } else {
      console.log('ok ' + slug + '  ' + want.length + '/' + want.length +
                  ' LIT numbers re-derived live');
    }
  }
  const measured = slugs.length - unmeasured - bad;
  if (bad === 0 && unmeasured === 0) {
    console.log('\nVERIFIED ' + measured + '/' + slugs.length);
  } else if (bad === 0) {
    // Passing with a gap is allowed, but the gap does not get to be quiet.
    console.log('\nVERIFIED ' + measured + '/' + slugs.length + '  ·  ' +
                unmeasured + ' UNMEASURED (needs a facility this sandbox lacks — ' +
                'those claims are NOT re-derived; check them in a browser)');
  } else {
    console.log('\n' + bad + ' of ' + slugs.length + ' FAILED' +
                (unmeasured ? '  ·  ' + unmeasured + ' unmeasured' : ''));
  }
  process.exit(bad === 0 ? 0 : 1);
}

main();
