#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_world2_spheres.py — roll real WORLD II · THE FOLD spheres.

Each sphere is a self-contained Code-Monkeys instrument (dark green, 3D-pixel, honest
two-layer LIT/FIG) that fills one seat in a domain. This generator wraps each bespoke
instrument in the shared CM chrome (rain + scanline + .cm-top nav + seal footer), writes
ud0/world2/<slug>.html, and wires the sphere into fold.json — into the top-level spheres[]
(so _dlw_fold.py SEALS it) AND into its domain's nested spheres[] (so the hub renders it).
Re-runnable: a sphere already present is updated in place, not duplicated.

Run: python _world2_spheres.py     then:  python _dlw_fold.py   (reseal ROOT_0)
"""
import json, os

W2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ud0", "world2")

def chrome(s):
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{s['title']} · WORLD II — THE FOLD</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');
*{{box-sizing:border-box}}
body{{margin:0;background:#070b07;color:#a8e6b4;font-family:'VT323',ui-monospace,monospace;font-size:19px;line-height:1.5}}
#rain{{position:fixed;inset:0;z-index:0;opacity:.5}}
.cm-scan{{position:fixed;inset:0;z-index:40;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,0),rgba(0,0,0,0) 2px,rgba(0,0,0,.28) 3px,rgba(0,0,0,0) 4px)}}
.cm-top{{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 14px;background:rgba(4,7,4,.85);border-bottom:3px solid #255c2c;font-family:'Press Start 2P',ui-monospace,monospace;font-size:9.5px;color:#39fc6b;backdrop-filter:blur(3px)}}
.cm-top a{{color:#39fc6b;text-decoration:none}}.cm-top a:hover{{color:#ffd23f}}.cm-top .sl{{color:{s['accent']}}}
main{{position:relative;z-index:10;max-width:900px;margin:0 auto;padding:70px 20px 60px}}
.bc{{font-family:'Press Start 2P',monospace;font-size:9px;color:#4c7a54;margin-bottom:14px}}
.bc b{{color:{s['accent']}}}
h1{{font-family:'Press Start 2P',monospace;font-size:22px;color:{s['accent']};text-shadow:3px 3px 0 rgba(0,0,0,.6);margin:0 0 8px;line-height:1.35}}
.kick{{font-size:20px;color:{s['accent']};font-style:italic;opacity:.9;margin-bottom:20px}}
.panel{{background:#0c130b;border:3px solid {s['accent']};box-shadow:0 0 0 3px #0a0e0a,0 0 20px color-mix(in srgb,{s['accent']} 30%,transparent);padding:18px 20px;margin:18px 0;display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start}}
canvas.inst{{image-rendering:pixelated;background:#050805;border:2px solid #255c2c;flex:none}}
.ctrl{{flex:1;min-width:240px}}
.rd{{font-size:19px;margin:8px 0;color:#cfe8d0}}
.rd b{{color:#39fc6b;font-size:22px;text-shadow:0 0 8px rgba(57,252,107,.5)}}
.rd.fate b,.fate{{color:{s['accent']}}}
input[type=range]{{width:120px;vertical-align:middle;accent-color:{s['accent']}}}
.btns{{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap}}
.btns button{{font-family:'Press Start 2P',monospace;font-size:8px;color:{s['accent']};background:transparent;border:2px solid {s['accent']};padding:8px 10px;cursor:pointer}}
.btns button:hover{{background:{s['accent']};color:#0a0e0a}}
.net{{font-family:ui-monospace,monospace;font-size:14px;color:#cfe8d0}}
.net .n{{display:inline-block;border:1px solid #255c2c;padding:4px 7px;margin:2px;border-radius:3px}}
.net .fwd{{color:#39fc6b}}.net .bwd{{color:{s['accent']}}}
.lossbar{{height:12px;background:#050805;border:1px solid #255c2c;margin-top:6px}}
.lossbar i{{display:block;height:100%;background:linear-gradient(90deg,{s['accent']},#ff2d95);transition:width .1s}}
.note{{background:#0a0f0a;border-left:4px solid #255c2c;padding:14px 16px;margin-top:22px;font-size:17px;color:#cfe8d0;line-height:1.6}}
.lit{{color:#0a0e0a;background:#39fc6b;font-family:'Press Start 2P',monospace;font-size:8px;padding:2px 5px}}
.fig{{color:#0a0e0a;background:{s['accent']};font-family:'Press Start 2P',monospace;font-size:8px;padding:2px 5px}}
.seal{{font-family:'Press Start 2P',monospace;font-size:8px;color:#4c7a54;margin-top:24px;border-top:2px solid #255c2c;padding-top:14px}}
</style></head><body>
<canvas id="rain"></canvas><div class="cm-scan"></div>
<div class="cm-top"><a href="./">&#9664; THE FOLD</a><span>0ROOT.AI // WORLD II &middot; {s['appeal_name']} &middot; {s['domain_title']}</span><span class="sl">&#9670; .dlw.fold</span></div>
<main>
<div class="bc">THE FOLD / <b>{s['appeal_name']}</b> / {s['domain_title']} / <b>{s['title']}</b></div>
<h1>{s['title']}</h1>
<div class="kick">{s['kicker']}</div>
{s['body']}
<div class="note"><span class="lit">LIT</span> {s['lit']}<br><br><span class="fig">FIG</span> {s['fig']}</div>
<div class="seal">&#9670; sealed .dlw.fold &rarr; folded to ROOT_0 &middot; a sphere of {s['domain_title']} &middot; David Lee Wise (ROOT0), with AVAN</div>
</main>
<script>
// green binary rain
(function(){{var c=document.getElementById('rain'),g=c.getContext('2d'),W,H,cols,drops,fs=14;
function rs(){{W=c.width=innerWidth;H=c.height=innerHeight;cols=Math.floor(W/fs);drops=Array(cols).fill(0);}}
rs();addEventListener('resize',rs);
setInterval(function(){{g.fillStyle='rgba(7,11,7,.09)';g.fillRect(0,0,W,H);g.fillStyle='#1aa63a';g.font=fs+'px VT323,monospace';
for(var i=0;i<cols;i++){{g.fillText(Math.random()<.5?'0':'1',i*fs,drops[i]*fs);if(drops[i]*fs>H&&Math.random()>.975)drops[i]=0;drops[i]++;}}}},70);}})();
{s['script']}
</script></body></html>"""

# ── THE BOWL — gradient descent on a convex quadratic (real) ──
BOWL_BODY = """<div class="panel">
 <canvas class="inst" id="bowl" width="420" height="420"></canvas>
 <div class="ctrl">
  <div class="rd">loss &nbsp;f(x,y)=x²+y² : <b id="bl">—</b></div>
  <div class="rd">position : <span id="bxy" style="color:#ffd23f">—</span> &middot; step <span id="bit">0</span></div>
  <div class="rd">&eta; learning rate <input type="range" id="blr" min="0.02" max="1.2" step="0.02" value="0.30"> <b id="blrv" style="font-size:18px">0.30</b></div>
  <div class="rd fate">fate: <span id="bfate">—</span></div>
  <div class="btns"><button id="bstep">step</button><button id="brun">&#9654; run</button><button id="breset">reset</button></div>
 </div>
</div>"""
BOWL_SCRIPT = """(function(){
var cv=document.getElementById('bowl'),g=cv.getContext('2d'),W=cv.width,H=cv.height;
var st={x:0.9,y:0.7,lr:0.30,it:0,path:[]};
function loss(x,y){return x*x+y*y;}
function px(x,y){var s=W/2.6;return [W/2+x*s,H/2+y*s];}
function draw(){g.clearRect(0,0,W,H);
 for(var r=0.2;r<=1.25;r+=0.2){var c=px(0,0),p=px(r,0),rad=p[0]-c[0];
  g.strokeStyle='rgba(57,252,107,'+(0.10+0.11*(1.25-r))+')';g.lineWidth=1;g.beginPath();g.arc(c[0],c[1],rad,0,7);g.stroke();}
 g.strokeStyle='#ffd23f';g.lineWidth=2;g.beginPath();
 st.path.forEach(function(p,i){var q=px(p[0],p[1]);i?g.lineTo(q[0],q[1]):g.moveTo(q[0],q[1]);});g.stroke();
 var m=px(0,0);g.fillStyle='#00f5ff';g.fillRect(m[0]-3,m[1]-3,6,6);
 var b=px(st.x,st.y);g.fillStyle='#ff2d95';g.fillRect(b[0]-6,b[1]-6,12,12);g.fillStyle='#ffc4de';g.fillRect(b[0]-6,b[1]-6,12,4);}
function readout(){document.getElementById('bl').textContent=loss(st.x,st.y).toFixed(5);
 document.getElementById('bit').textContent=st.it;
 document.getElementById('bxy').textContent='('+st.x.toFixed(3)+', '+st.y.toFixed(3)+')';
 var f=Math.abs(1-2*st.lr);
 document.getElementById('bfate').textContent=f<1?('converges  |1-2\\u03b7|='+f.toFixed(2)+' < 1'):(f>1?('DIVERGES  |1-2\\u03b7|='+f.toFixed(2)+' > 1'):'lands on 0 in one step');}
function reset(){st.x=0.9;st.y=0.7;st.it=0;st.path=[[st.x,st.y]];draw();readout();}
function step(){var gx=2*st.x,gy=2*st.y;st.x-=st.lr*gx;st.y-=st.lr*gy;st.it++;
 st.path.push([st.x,st.y]);if(st.path.length>500)st.path.shift();draw();readout();}
var run=null;
document.getElementById('bstep').onclick=step;
document.getElementById('breset').onclick=function(){if(run){clearInterval(run);run=null;document.getElementById('brun').textContent='\\u25b6 run';}reset();};
document.getElementById('brun').onclick=function(){var b=this;if(run){clearInterval(run);run=null;b.textContent='\\u25b6 run';return;}
 b.textContent='\\u25fc stop';run=setInterval(function(){step();if(st.it>240||loss(st.x,st.y)>1e6){clearInterval(run);run=null;b.textContent='\\u25b6 run';}},55);};
document.getElementById('blr').oninput=function(){st.lr=parseFloat(this.value);document.getElementById('blrv').textContent=st.lr.toFixed(2);readout();};
reset();window.__bowl=st;})();"""

# ── THE CHAIN RULE — a real 2-layer backprop ──
CHAIN_BODY = """<div class="panel">
 <div class="ctrl">
  <div class="net">forward &rarr;<br>
   <span class="n">x=<b class="fwd" id="cx">—</b></span> &rarr;
   <span class="n">w1=<b class="fwd" id="cw1">—</b></span> &rarr;
   <span class="n">a=w1·x=<b class="fwd" id="ca">—</b></span> &rarr;
   <span class="n">w2=<b class="fwd" id="cw2">—</b></span> &rarr;
   <span class="n">y=w2·a=<b class="fwd" id="cy">—</b></span> &rarr;
   <span class="n">L=(y−t)²=<b class="fwd" id="cL">—</b></span>
  </div>
  <div class="lossbar"><i id="cbar" style="width:0%"></i></div>
  <div class="net" style="margin-top:12px">&larr; backward (the chain rule)<br>
   <span class="n">∂L/∂y=<b class="bwd" id="gdy">—</b></span>
   <span class="n">∂L/∂a=<b class="bwd" id="gda">—</b></span>
   <span class="n">∂L/∂w2=<b class="bwd" id="gdw2">—</b></span>
   <span class="n">∂L/∂w1=<b class="bwd" id="gdw1">—</b></span>
  </div>
  <div class="rd" style="margin-top:12px">target t <input type="range" id="ct2" min="-1.5" max="1.5" step="0.1" value="1.0"> <b id="ctv" style="font-size:18px">1.0</b>
   &nbsp;&middot;&nbsp; &eta; <input type="range" id="clr" min="0.01" max="0.30" step="0.01" value="0.10"> <b id="clrv" style="font-size:18px">0.10</b></div>
  <div class="rd">step <span id="cit">0</span> &middot; loss <b id="cL2">—</b></div>
  <div class="btns"><button id="cstep">forward + backward + step</button><button id="crun">&#9654; run</button><button id="creset">reset</button></div>
 </div>
</div>"""
CHAIN_SCRIPT = """(function(){
var s={x:1.0,w1:0.80,w2:0.50,t:1.0,lr:0.10,it:0};
function fwd(){var a=s.w1*s.x,y=s.w2*a;return {a:a,y:y,L:(y-s.t)*(y-s.t)};}
function grads(f){var dy=2*(f.y-s.t);return {dy:dy,da:dy*s.w2,dw2:dy*f.a,dw1:dy*s.w2*s.x};}
function set(id,v){var e=document.getElementById(id);if(e)e.textContent=(+v).toFixed(3);}
function render(){var f=fwd(),gr=grads(f);
 set('cx',s.x);set('cw1',s.w1);set('ca',f.a);set('cw2',s.w2);set('cy',f.y);set('cL',f.L);set('cL2',f.L);
 set('gdy',gr.dy);set('gda',gr.da);set('gdw2',gr.dw2);set('gdw1',gr.dw1);
 document.getElementById('cit').textContent=s.it;
 document.getElementById('cbar').style.width=Math.min(100,f.L*45)+'%';}
function step(){var f=fwd(),gr=grads(f);s.w1-=s.lr*gr.dw1;s.w2-=s.lr*gr.dw2;s.it++;render();}
function reset(){s.w1=0.80;s.w2=0.50;s.it=0;render();}
var run=null;
document.getElementById('cstep').onclick=step;
document.getElementById('creset').onclick=function(){if(run){clearInterval(run);run=null;document.getElementById('crun').textContent='\\u25b6 run';}reset();};
document.getElementById('crun').onclick=function(){var b=this;if(run){clearInterval(run);run=null;b.textContent='\\u25b6 run';return;}
 b.textContent='\\u25fc stop';run=setInterval(function(){step();if(fwd().L<1e-6||s.it>400){clearInterval(run);run=null;b.textContent='\\u25b6 run';}},70);};
document.getElementById('clr').oninput=function(){s.lr=parseFloat(this.value);document.getElementById('clrv').textContent=s.lr.toFixed(2);};
document.getElementById('ct2').oninput=function(){s.t=parseFloat(this.value);document.getElementById('ctv').textContent=s.t.toFixed(1);render();};
reset();window.__chain=s;})();"""

# ── WARM CACHE — memoisation turns exponential recursion into linear (real call counts) ──
WARM_BODY = """<div class="panel"><div class="ctrl" style="flex:1">
 <div class="rd">compute &nbsp;fib(<b id="wn">20</b>) &nbsp; <input type="range" id="wnr" min="5" max="30" step="1" value="20"></div>
 <div class="rd">NAIVE recursion &mdash; calls: <b id="wnaive" style="color:#ff2d95">&mdash;</b></div>
 <div class="lossbar"><i id="wbn" style="width:0%;background:#ff2d95"></i></div>
 <div class="rd">MEMOISED &mdash; calls: <b id="wmemo">&mdash;</b></div>
 <div class="lossbar"><i id="wbm" style="width:0%"></i></div>
 <div class="rd fate">speedup: <b id="wratio">&mdash;</b>&times; fewer calls &nbsp;&middot;&nbsp; fib = <span id="wres" style="color:#5ad0ff">&mdash;</span></div>
 <div class="btns"><button id="wrun">run both</button></div>
</div></div>"""
WARM_SCRIPT = """(function(){
function naive(n,c){c.k++;return n<2?n:naive(n-1,c)+naive(n-2,c);}
function memo(n,m,c){c.k++;if(n<2)return n;if(m[n]!=null)return m[n];return m[n]=memo(n-1,m,c)+memo(n-2,m,c);}
function run(){var n=+document.getElementById('wnr').value;document.getElementById('wn').textContent=n;
 var cn={k:0},cm={k:0};var r1=naive(n,cn);memo(n,{},cm);
 document.getElementById('wnaive').textContent=cn.k.toLocaleString();
 document.getElementById('wmemo').textContent=cm.k.toLocaleString();
 document.getElementById('wres').textContent=r1;
 document.getElementById('wratio').textContent=(cm.k?cn.k/cm.k:0).toFixed(0);
 document.getElementById('wbn').style.width='100%';
 document.getElementById('wbm').style.width=Math.max(0.5,100*cm.k/cn.k)+'%';
 window.__cache={n:n,naive:cn.k,memo:cm.k,result:r1};}
document.getElementById('wnr').oninput=run;document.getElementById('wrun').onclick=run;run();})();"""

# ── OFF BY ONE — the fencepost: N sections need N+1 posts (real) ──
OBO_BODY = """<div class="panel">
 <canvas class="inst" id="fence" width="440" height="200"></canvas>
 <div class="ctrl">
  <div class="rd">sections N : <b id="fn">6</b> <input type="range" id="fnr" min="2" max="12" step="1" value="6"></div>
  <div class="rd">loop <code>i&lt;N</code> &rarr; posts <b id="fbug" style="color:#ff2d95">&mdash;</b> <span style="color:#ff2d95">(hangs open)</span></div>
  <div class="rd">loop <code>i&lt;=N</code> &rarr; posts <b id="ffix">&mdash;</b> (closed)</div>
  <div class="rd fate">N sections need <b id="fneed">&mdash;</b> posts, not N.</div>
  <div class="btns"><button id="ftog">show buggy / fixed</button></div>
 </div>
</div>"""
OBO_SCRIPT = """(function(){
var cv=document.getElementById('fence'),g=cv.getContext('2d'),W=cv.width,H=cv.height;
var st={N:6,buggy:true};
function draw(){g.clearRect(0,0,W,H);var N=st.N,pad=28,gap=(W-2*pad)/N,y0=40,y1=H-40,posts=st.buggy?N:N+1;
 for(var s=0;s<N;s++){var xa=pad+s*gap,xb=pad+(s+1)*gap,closed=(s+1)<posts;
  g.strokeStyle=closed?'#39fc6b':'#ff2d95';g.lineWidth=3;g.beginPath();g.moveTo(xa,(y0+y1)/2);g.lineTo(xb,(y0+y1)/2);g.stroke();}
 for(var p=0;p<posts;p++){var x=pad+p*gap;g.fillStyle='#ffd23f';g.fillRect(x-4,y0,8,y1-y0);g.fillStyle='#fff3c0';g.fillRect(x-4,y0,8,4);}
 if(st.buggy){var xe=pad+N*gap;g.strokeStyle='#ff2d95';g.setLineDash([4,4]);g.lineWidth=2;g.strokeRect(xe-4,y0,8,y1-y0);g.setLineDash([]);}}
function upd(){var N=st.N;document.getElementById('fn').textContent=N;document.getElementById('fbug').textContent=N;
 document.getElementById('ffix').textContent=N+1;document.getElementById('fneed').textContent=N+1;draw();
 window.__fence={N:N,buggyPosts:N,fixedPosts:N+1};}
document.getElementById('fnr').oninput=function(){st.N=+this.value;upd();};
document.getElementById('ftog').onclick=function(){st.buggy=!st.buggy;draw();};
upd();})();"""

# ── THE KONAMI CODE — a real finite-state sequence matcher ──
KON_BODY = """<div class="panel"><div class="ctrl" style="flex:1">
 <div class="rd">the code: <b style="letter-spacing:3px">&uarr; &uarr; &darr; &darr; &larr; &rarr; &larr; &rarr; B A</b> &nbsp;(click or use arrow keys)</div>
 <div id="kseq" class="rd" style="font-size:28px;letter-spacing:8px;min-height:36px">&mdash;</div>
 <div class="btns" id="kpad"></div>
 <div class="rd fate" id="kstatus">locked &middot; 0 / 10</div>
 <div class="btns"><button id="kreset">reset</button></div>
</div></div>"""
KON_SCRIPT = """(function(){
var CODE=['U','U','D','D','L','R','L','R','B','A'];
var GLY={U:'\\u2191',D:'\\u2193',L:'\\u2190',R:'\\u2192',B:'B',A:'A'};
var idx=0,unlocked=false,pad=document.getElementById('kpad');
['U','D','L','R','B','A'].forEach(function(k){var b=document.createElement('button');b.textContent=GLY[k];b.onclick=function(){feed(k);};pad.appendChild(b);});
function render(){document.getElementById('kseq').innerHTML=CODE.map(function(c,i){return '<span style="color:'+(i<idx?'#39fc6b':'#4c7a54')+'">'+GLY[c]+'</span>';}).join(' ');
 document.getElementById('kstatus').innerHTML=unlocked?'<span style="color:#39fc6b">UNLOCKED &mdash; 30 LIVES</span>':('locked &middot; '+idx+' / 10');
 window.__konami={index:idx,unlocked:unlocked};}
function feed(k){if(unlocked)return;if(k===CODE[idx]){idx++;if(idx===CODE.length)unlocked=true;}else{idx=(k===CODE[0])?1:0;}render();}
document.getElementById('kreset').onclick=function(){idx=0;unlocked=false;render();};
addEventListener('keydown',function(e){var m={ArrowUp:'U',ArrowDown:'D',ArrowLeft:'L',ArrowRight:'R',b:'B',B:'B',a:'A',A:'A'};if(m[e.key]){feed(m[e.key]);e.preventDefault();}});
render();})();"""

SPHERES = [
 {"slug":"the-bowl","title":"THE BOWL","appeal_name":"GRIND","appeal_slug":"grind",
  "domain_title":"GRADIENT DESCENT","domain_slug":"gradient-descent","accent":"#ffd23f","icon":"grind",
  "kicker":"roll downhill until the floor stops falling",
  "blurb":"real gradient descent on a convex bowl f(x,y)=x²+y². The step x -= 2ηx converges iff |1-2η|<1 — watch it settle, land in one shot at η=0.5, or blow up past η=1.",
  "lit":"Genuine gradient descent. The gradient of f(x,y)=x²+y² is (2x,2y); each step is x&larr;x&minus;η·2x. For this quadratic the update multiplies the coordinate by (1&minus;2η), so it <b>provably converges iff |1&minus;2η|&lt;1</b> (0&lt;η&lt;1), lands exactly on 0 at η=0.5, and diverges for η&ge;1. The path, the loss, and the fate readout are all computed live — no scripted animation.",
  "fig":"The 'ball rolling into a bowl' and the arcade dressing are the metaphor; the bowl is a top-down contour plot, not a real 3D render. The math underneath is the honest part.",
  "body":BOWL_BODY,"script":BOWL_SCRIPT},
 {"slug":"the-chain-rule","title":"THE CHAIN RULE","appeal_name":"GRIND","appeal_slug":"grind",
  "domain_title":"BACKPROP","domain_slug":"backprop","accent":"#9d00ff","icon":"glitch",
  "kicker":"the error, walked backward through the wires",
  "blurb":"a real two-layer network a=w1·x, y=w2·a, L=(y−t)². Forward computes the loss; backward applies the chain rule for every partial; one step drops the loss. Nothing faked.",
  "lit":"A genuine 2-layer net and genuine backprop. Forward: a=w1·x, y=w2·a, L=(y&minus;t)². Backward is the literal chain rule: ∂L/∂y=2(y&minus;t), ∂L/∂a=∂L/∂y·w2, ∂L/∂w2=∂L/∂y·a, ∂L/∂w1=∂L/∂a·x. Each number is recomputed every step from the actual weights; SGD (w&larr;w&minus;η·∂L/∂w) drives the loss toward 0. Change the target or η and it re-solves live.",
  "fig":"The glowing wires are decoration; the values on them are real. 'The error walked backward' is how backprop actually works, told as a picture.",
  "body":CHAIN_BODY,"script":CHAIN_SCRIPT},
 {"slug":"warm-cache","title":"WARM CACHE","appeal_name":"GRIND","appeal_slug":"grind",
  "domain_title":"WARM CACHE","domain_slug":"warm-cache","accent":"#5ad0ff","icon":"respawn",
  "kicker":"the second time is always faster",
  "blurb":"real recursion with a real call counter. Naive fib(n) makes O(φⁿ) calls; one memo cuts it to O(n). fib(20): 21,891 calls vs 39. Same answer, a thousandfold less work.",
  "lit":"Genuine recursion, genuinely counted. Naive Fibonacci recomputes the same subproblems, making <b>2·fib(n+1)&minus;1</b> calls (fib(20) &rarr; 21,891); a memo table makes each n once, <b>O(n)</b> calls (fib(20) &rarr; 39). Both run live and report their real call counts — the speedup you see is measured, not asserted.",
  "fig":"'Warm cache / the second time is faster' is the arcade line; the mechanism (overlapping subproblems, memoised) is the honest computer-science underneath.",
  "body":WARM_BODY,"script":WARM_SCRIPT},
 {"slug":"off-by-one","title":"OFF BY ONE","appeal_name":"GLITCH","appeal_slug":"glitch",
  "domain_title":"OFF BY ONE","domain_slug":"off-by-one","accent":"#7cfc00","icon":"glitch",
  "kicker":"the fencepost that ruins the fence",
  "blurb":"the fencepost error, drawn. A fence of N sections needs N+1 posts; the loop i<N builds only N and leaves the far end hanging open. Slide N and watch the gap.",
  "lit":"The classic fencepost / off-by-one. N sections require <b>N+1</b> posts (a post on both ends of every rail). A loop <code>for(i=0;i&lt;N)</code> places only N posts, so the last section has no right-hand post — the fence hangs open; <code>i&lt;=N</code> fixes it. The post counts and the open rail (red) are computed from N, not drawn by hand.",
  "fig":"The pixel fence is the picture; the bug is real and is exactly why <code>&lt;</code> vs <code>&lt;=</code> has cost real systems real money.",
  "body":OBO_BODY,"script":OBO_SCRIPT},
 {"slug":"the-konami-code","title":"THE KONAMI CODE","appeal_name":"CHEAT","appeal_slug":"cheat",
  "domain_title":"THE KONAMI CODE","domain_slug":"the-konami-code","accent":"#ffd23f","icon":"cheat",
  "kicker":"up up down down — unlock it all",
  "blurb":"a real finite-state sequence matcher. Feed ↑↑↓↓←→←→BA in order and it unlocks; one wrong key snaps the index back. The exact DFA arcade cabinets ran.",
  "lit":"A genuine finite-state matcher. An index walks the 10-symbol target; a correct symbol advances it, a wrong one resets it (to 1 if the miss is itself the first symbol, else 0). Reach 10 and it latches UNLOCKED. This is the real recogniser behind the cheat — click the pad or use the arrow keys; the state is live in window.__konami.",
  "fig":"'30 lives' is the Contra lore; the state machine deciding whether you typed the code is the real part.",
  "body":KON_BODY,"script":KON_SCRIPT},
]

def main():
    db = json.load(open(os.path.join(W2, "fold.json"), encoding="utf-8"))
    top = {s["slug"]: s for s in db["spheres"]}
    dom_by_slug = {}
    for a in db["appeals"]:
        for d in a.get("domains", []):
            dom_by_slug[d["slug"]] = d
    for sp in SPHERES:
        open(os.path.join(W2, sp["slug"] + ".html"), "w", encoding="utf-8").write(chrome(sp))
        # top-level spheres[] (SEALED)
        rec = {"slug": sp["slug"], "title": sp["title"], "kicker": sp["kicker"],
               "accent": sp["accent"], "blurb": sp["blurb"]}
        if sp["slug"] in top:
            top[sp["slug"]].update(rec)
        else:
            db["spheres"].append(rec)
        # nested domain spheres[] (RENDERED)
        d = dom_by_slug.get(sp["domain_slug"])
        if d is not None:
            d.setdefault("spheres", [])
            nest = {"slug": sp["slug"], "title": sp["title"], "accent": sp["accent"],
                    "icon": sp["icon"], "kicker": sp["kicker"]}
            ex = next((x for x in d["spheres"] if x.get("slug") == sp["slug"]), None)
            if ex: ex.update(nest)
            else: d["spheres"].append(nest)
        print(f"  rolled {sp['title']:16} -> {sp['appeal_name']} / {sp['domain_title']}  ({sp['slug']}.html)")
    db["counts"]["spheres"] = len(db["spheres"])
    db["counts"]["spheres_built"] = sum(len(d.get("spheres", [])) for a in db["appeals"] for d in a["domains"])
    json.dump(db, open(os.path.join(W2, "fold.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"built spheres now: {db['counts']['spheres']} sealed · {db['counts']['spheres_built']} seated in domains")

if __name__ == "__main__":
    print("ROLLING WORLD II SPHERES:")
    main()
