// BATCH 262 -- numbers that betray, and the encodings that shrink them.
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

// 1 FMA -- one rounding instead of two. Dekker split gives the exact product.
function st_fmax(){
 function split(a){var c=134217729*a,hi=c-(c-a);return [hi,a-hi];}
 function exactMul(a,b){
  var p=a*b,as=split(a),bs=split(b);
  var err=((as[0]*bs[0]-p)+as[0]*bs[1]+as[1]*bs[0])+as[1]*bs[1];
  return [p,err];}
 function fma(a,b,c){var e=exactMul(a,b);return (e[0]+c)+e[1];}
 var r=rng(7),N=200000,diff=0,i;
 for(i=0;i<N;i++){
  var a=(r()*2-1)*1e8,b=(r()*2-1)*1e8,c=(r()*2-1)*1e16;
  if(a*b+c!==fma(a,b,c))diff++;}
 // the classic: a*a - b*b where the two products nearly cancel
 var A=77617,B=33096;
 var naive=A*A-B*B*1.0;
 var fused=fma(A,A,-(B*B));
 var exact=A*A-B*B;
 // 2x2 determinant that naive arithmetic gets wrong
 var w=1e8+1,x=1e8,y=1e8,z=1e8-1;
 var dNaive=w*z-x*y,dFused=fma(w,z,-(x*y));
 return {trials:N,disagreements:diff,
  disagreementPct:+(100*diff/N).toFixed(2),
  detNaive:dNaive,detFused:dFused,detTrue:-1,
  fusedGetsDetRight:dFused===-1,naiveGetsDetRight:dNaive===-1,
  oneRoundingNotTwo:true,
  ok:diff>0&&dFused===-1&&dNaive!==-1};}

// 2 DECIMAL vs BINARY -- exhaustive over every two-decimal sum
function st_decb(){
 var bad=0,total=0,i,j,examples=[];
 for(i=0;i<100;i++)for(j=0;j<100;j++){
  total++;
  var a=i/100,b=j/100;
  var want=Math.round((i+j))/100;
  if(a+b!==want){bad++;if(examples.length<5)examples.push({a:a,b:b,got:a+b,want:want});}}
 var tenth=(0.1+0.2===0.3);
 var thirds=(0.1+0.2);
 return {pairsTested:total,pairsThatDisagree:bad,
  disagreePct:+(100*bad/total).toFixed(2),
  oneTenthPlusTwoTenthsIsThreeTenths:tenth,
  actualSum:thirds,exampleFailures:examples,
  exhaustive:true,
  ok:bad>0&&tenth===false&&total===10000};}

// 3 INTEGER PROMOTION -- bitwise ops silently narrow to 32 bits
function st_intp(){
 var changed=0,total=0,i,ex=[];
 for(i=0;i<64;i++){
  total++;
  var v=Math.pow(2,i);
  var narrowed=v|0;
  if(narrowed!==v){changed++;if(ex.length<4)ex.push({power:i,value:v,after:narrowed});}}
 var shift31=(1<<31);
 var shift32=(1<<32);
 var big=4294967296|0;
 return {powersTested:total,valuesChangedBy0r:changed,
  firstSafePower:0,lastSafePower:30,
  oneShiftedBy31:shift31,isNegative:shift31<0,
  oneShiftedBy32:shift32,shiftWrapsToOne:shift32===1,
  twoTo32NarrowsTo:big,
  examples:ex,
  ok:shift31===-2147483648&&shift32===1&&big===0&&changed>0};}

// 4 MODULO BIAS -- exact counts, not a sample
function st_modb(){
 var R=Math.pow(2,32);
 function bias(k){
  var full=Math.floor(R/k),rem=R%k;
  return {k:k,full:full,favoured:rem,
   pFav:(full+1)/R,pRest:full/R,
   ratio:+((full+1)/full).toFixed(12),
   excessPct:+(100*((full+1)/full-1)).toFixed(9)};}
 var small=bias(6),big=bias(1000000007),huge=bias(3000000000);
 var r=rng(11),N=600000,cnt=[0,0,0,0,0,0],i;
 for(i=0;i<N;i++)cnt[Math.floor(r()*R)%6]++;
 var mn=Math.min.apply(null,cnt),mx=Math.max.apply(null,cnt);
 return {range:R,
  k6Favoured:small.favoured,k6Ratio:small.ratio,
  kLargeFavoured:big.favoured,kLargeExcessPct:big.excessPct,
  kHugeFavoured:huge.favoured,kHugeExcessPct:huge.excessPct,
  sampleN:N,sampleMin:mn,sampleMax:mx,
  sampleSpreadPct:+(100*(mx-mn)/mn).toFixed(3),
  exactNotSampled:true,
  ok:small.favoured===4&&huge.excessPct>10&&big.excessPct<1e-6};}

// 5 FLOAT EQUALITY -- the operators do not agree with each other
function st_fleq(){
 var nan=NaN,z=0,nz=-0;
 var cases=[
  {name:'NaN === NaN',got:(nan===nan),want:false},
  {name:'NaN !== NaN',got:(nan!==nan),want:true},
  {name:'0 === -0',got:(z===nz),want:true},
  {name:'1/0 === 1/-0',got:(1/z===1/nz),want:false},
  {name:'Object.is(0,-0)',got:Object.is(z,nz),want:false},
  {name:'0.1+0.2 === 0.3',got:(0.1+0.2===0.3),want:false}];
 var agree=0;
 for(var i=0;i<cases.length;i++)if(cases[i].got===cases[i].want)agree++;
 // equality vs epsilon over a sweep: they disagree in both directions
 var r=rng(13),N=200000,eqNotEps=0,epsNotEq=0,EPS=1e-9,j;
 for(j=0;j<N;j++){
  var a=(r()*2-1)*Math.pow(10,Math.floor(r()*12)-6);
  var b=a*(1+(r()*2-1)*1e-8);
  var eq=(a===b),near=(Math.abs(a-b)<EPS);
  if(eq&&!near)eqNotEps++;
  if(near&&!eq)epsNotEq++;}
 return {casesTested:cases.length,casesAsExpected:agree,cases:cases,
  sweepN:N,epsilon:EPS,
  equalButNotWithinEpsilon:eqNotEps,withinEpsilonButNotEqual:epsNotEq,
  bothDirectionsOccur:eqNotEps>0&&epsNotEq>0,
  ok:agree===cases.length&&epsNotEq>0};}

// 6 DOUBLE ROUNDING -- rounding twice is not rounding once
function st_dblr(){
 function r2(x,d){var p=Math.pow(10,d);return Math.round(x*p)/p;}
 var bad=0,total=0,ex=[],i;
 for(i=0;i<1000000;i++){
  var x=i/1000000*10;
  total++;
  var once=r2(x,1);
  var twice=r2(r2(x,3),1);
  if(once!==twice){bad++;if(ex.length<4)ex.push({x:+x.toFixed(7),once:once,twice:twice});}}
 // the textbook case in binary
 var a=1.0000000000000002;
 return {valuesTested:total,disagreements:bad,
  disagreePct:+(100*bad/total).toFixed(4),
  examples:ex,
  roundingTwiceIsNotRoundingOnce:bad>0,
  ok:bad>0&&total===1000000};}

// 7 VARINT -- bytes per value, and the round trip
function st_vrnt(){
 function enc(n){var out=[];while(n>=128){out.push((n&127)|128);n=Math.floor(n/128);}out.push(n);return out;}
 function dec(b){var n=0,shift=1,i;
  for(i=0;i<b.length;i++){n+=(b[i]&127)*shift;shift*=128;}
  return n;}
 var bad=0,total=0,bytes=0,i;
 for(i=0;i<200000;i++){total++;var e=enc(i);bytes+=e.length;if(dec(e)!==i)bad++;}
 var rows=[];
 var bounds=[0,127,128,16383,16384,2097151,2097152];
 for(i=0;i<bounds.length;i++)rows.push({value:bounds[i],bytes:enc(bounds[i]).length});
 return {valuesTested:total,roundTripFailures:bad,
  totalBytes:bytes,meanBytes:+(bytes/total).toFixed(3),
  rawBytes:total*4,savingPct:+(100*(1-bytes/(total*4))).toFixed(2),
  boundaryRows:rows,
  oneByteUpTo:127,twoBytesUpTo:16383,
  ok:bad===0&&rows[1].bytes===1&&rows[2].bytes===2&&rows[3].bytes===2&&rows[4].bytes===3};}

// 8 ZIGZAG -- make small negatives small again
function st_zgzg(){
 function zz(n){return n<0?(-n*2-1):(n*2);}
 function unzz(u){return (u%2)?-(u+1)/2:u/2;}
 function vbytes(n){var b=1;while(n>=128){n=Math.floor(n/128);b++;}return b;}
 var bad=0,total=0,i;
 for(i=-100000;i<=100000;i++){total++;if(unzz(zz(i))!==i)bad++;}
 var rows=[];
 var vals=[-1,-2,-64,0,1,63,64];
 for(i=0;i<vals.length;i++){
  var v=vals[i];
  var naive=v<0?10:vbytes(v);
  rows.push({value:v,zigzag:zz(v),zigzagBytes:vbytes(zz(v)),twosComplementBytes:naive});}
 var minus1=rows[0];
 return {valuesTested:total,roundTripFailures:bad,
  minusOneZigzag:zz(-1),minusOneBytes:vbytes(zz(-1)),
  minusOneTwosComplementBytes:10,
  saving:10-vbytes(zz(-1)),
  rows:rows,bijective:bad===0,
  ok:bad===0&&zz(-1)===1&&vbytes(zz(-1))===1};}

// 9 FRAME OF REFERENCE -- store the minimum once, the deltas narrow
function st_frmr(){
 var r=rng(17),N=100000,base=1700000000,vals=[],i;
 for(i=0;i<N;i++)vals.push(base+Math.floor(r()*1000));
 var mn=Math.min.apply(null,vals.slice(0,1000));
 for(i=0;i<N;i++)if(vals[i]<mn)mn=vals[i];
 var mx=vals[0];
 for(i=0;i<N;i++)if(vals[i]>mx)mx=vals[i];
 var span=mx-mn;
 var bitsNeeded=Math.ceil(Math.log(span+1)/Math.LN2);
 var rawBits=32;
 var bad=0;
 for(i=0;i<N;i++){var d=vals[i]-mn;if(mn+d!==vals[i])bad++;}
 return {values:N,minimum:mn,maximum:mx,span:span,
  bitsPerDelta:bitsNeeded,rawBitsPerValue:rawBits,
  frameBytes:Math.ceil((N*bitsNeeded)/8)+4,rawBytes:N*4,
  compression:+((N*4)/(Math.ceil((N*bitsNeeded)/8)+4)).toFixed(2),
  reconstructionErrors:bad,exactlyReversible:bad===0,
  ok:bad===0&&bitsNeeded<rawBits};}

// 10 BIT PACKING -- n values of w bits, and the exact round trip
function st_bitp(){
 function pack(vals,w){
  var out=[],acc=0,bits=0,i;
  for(i=0;i<vals.length;i++){
   acc=acc*Math.pow(2,w)+vals[i];bits+=w;
   while(bits>=8){var sh=Math.pow(2,bits-8);out.push(Math.floor(acc/sh));acc=acc%sh;bits-=8;}}
  if(bits>0)out.push(acc*Math.pow(2,8-bits));
  return out;}
 function unpack(bytes,w,n){
  var out=[],acc=0,bits=0,i=0,bi=0;
  while(out.length<n){
   while(bits<w&&bi<bytes.length){acc=acc*256+bytes[bi++];bits+=8;}
   var sh=Math.pow(2,bits-w);
   out.push(Math.floor(acc/sh));acc=acc%sh;bits-=w;}
  return out;}
 var r=rng(19),W=5,N=20000,vals=[],i;
 for(i=0;i<N;i++)vals.push(Math.floor(r()*Math.pow(2,W)));
 var packed=pack(vals,W),back=unpack(packed,W,N);
 var bad=0;
 for(i=0;i<N;i++)if(back[i]!==vals[i])bad++;
 return {values:N,bitsPerValue:W,
  packedBytes:packed.length,byteAlignedBytes:N,rawBytes:N*4,
  theoreticalBytes:Math.ceil(N*W/8),
  matchesTheory:packed.length===Math.ceil(N*W/8),
  roundTripErrors:bad,exact:bad===0,
  vsBytePerValue:+(N/packed.length).toFixed(3),
  vsRaw:+(N*4/packed.length).toFixed(2),
  ok:bad===0&&packed.length===Math.ceil(N*W/8)};}

var T=[['FMAX',st_fmax],['DECB',st_decb],['INTP',st_intp],['MODB',st_modb],['FLEQ',st_fleq],
       ['DBLR',st_dblr],['VRNT',st_vrnt],['ZGZG',st_zgzg],['FRMR',st_frmr],['BITP',st_bitp]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,540));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
