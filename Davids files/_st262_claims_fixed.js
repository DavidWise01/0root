function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
// MODB -- the first gate asserted a LARGE divisor gives negligible bias. It is the
// other way round: bias grows with k/R, because a large k leaves few complete
// cycles in the range. k=1e9+7 over 2^32 gives 4 full cycles and a 25% excess.
function st_modb(){
 var R=Math.pow(2,32);
 function bias(k){
  var full=Math.floor(R/k),rem=R%k;
  return {k:k,fullCycles:full,favouredResidues:rem,
   ratio:+((full+1)/full).toFixed(12),
   excessPct:+(100*((full+1)/full-1)).toFixed(9)};}
 var tiny=bias(6),mid=bias(1000000007),huge=bias(3000000000);
 var rows=[],ks=[6,1000,1000000,100000000,1000000007,3000000000],i;
 for(i=0;i<ks.length;i++){var b=bias(ks[i]);
  rows.push({k:ks[i],fullCycles:b.fullCycles,excessPct:b.excessPct});}
 var r=rng(11),N=600000,cnt=[0,0,0,0,0,0];
 for(i=0;i<N;i++)cnt[Math.floor(r()*R)%6]++;
 var mn=Math.min.apply(null,cnt),mx=Math.max.apply(null,cnt);
 return {range:R,
  k6FullCycles:tiny.fullCycles,k6FavouredResidues:tiny.favouredResidues,
  k6ExcessPct:tiny.excessPct,
  kBillionFullCycles:mid.fullCycles,kBillionExcessPct:mid.excessPct,
  kHugeFullCycles:huge.fullCycles,kHugeExcessPct:huge.excessPct,
  biasGrowsWithK:tiny.excessPct<mid.excessPct&&mid.excessPct<huge.excessPct,
  rows:rows,
  sampleN:N,sampleMin:mn,sampleMax:mx,
  exactNotSampled:true,
  ok:tiny.fullCycles===715827882&&mid.excessPct===25&&huge.excessPct===100&&
     tiny.excessPct<mid.excessPct&&mid.excessPct<huge.excessPct};}
// FLEQ -- "equal but not within epsilon" measured 0, and that is not an empirical
// zero: a===b forces |a-b|=0, so the implication only runs one way. Name it as an
// implication rather than reporting a count that looks like a near miss.
function st_fleq(){
 var nan=NaN,z=0,nz=-0;
 var cases=[
  {name:'NaN === NaN',got:(nan===nan),want:false},
  {name:'0 === -0',got:(z===nz),want:true},
  {name:'1/0 === 1/-0',got:(1/z===1/nz),want:false},
  {name:'Object.is(0,-0)',got:Object.is(z,nz),want:false},
  {name:'0.1+0.2 === 0.3',got:(0.1+0.2===0.3),want:false}];
 var agree=0,i;
 for(i=0;i<cases.length;i++)if(cases[i].got===cases[i].want)agree++;
 var r=rng(13),N=200000,eqNotEps=0,epsNotEq=0,EPS=1e-9,j;
 for(j=0;j<N;j++){
  var a=(r()*2-1)*Math.pow(10,Math.floor(r()*12)-6);
  var b=a*(1+(r()*2-1)*1e-8);
  var eq=(a===b),near=(Math.abs(a-b)<EPS);
  if(eq&&!near)eqNotEps++;
  if(near&&!eq)epsNotEq++;}
 return {casesTested:cases.length,casesAsExpected:agree,cases:cases,
  sweepN:N,epsilon:EPS,
  equalButNotWithinEpsilon:eqNotEps,
  equalityImpliesEpsilonCloseness:eqNotEps===0,
  withinEpsilonButNotEqual:epsNotEq,
  epsilonDoesNotImplyEquality:epsNotEq>0,
  implicationIsOneWay:eqNotEps===0&&epsNotEq>0,
  ok:agree===cases.length&&eqNotEps===0&&epsNotEq>0};}
var T=[['MODB',st_modb],['FLEQ',st_fleq]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,700));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
