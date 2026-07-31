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
