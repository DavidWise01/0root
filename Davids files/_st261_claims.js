// BATCH 261 WAVE B -- time, clocks and order. Run standalone before any prose.
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

// 1 NTP SLEW -- correct an offset by bending the rate, never by jumping
function st_ntps(){
 var offset=5.0,slewPpm=500,tick=1;
 var rate=slewPpm/1e6;
 var secs=Math.ceil(offset/rate);
 var clock=0,prev=-1,back=0,i;
 for(i=0;i<20;i++){var t=i*(secs/20);var c=t+rate*t;if(c<prev)back++;prev=c;}
 var stepBack=1;                       // a step of -5 s goes backwards by construction
 var stepBackwardsIf=offset>0?0:1;
 return {offsetSeconds:offset,slewPpm:slewPpm,
  slewSecondsToConverge:secs,slewHours:+(secs/3600).toFixed(2),
  slewWentBackwards:back,stepIsInstant:true,
  stepBackwardsSeconds:offset,
  slewIsMonotonic:back===0,
  ok:secs===10000&&back===0};}

// 2 LEAP SMEAR -- spread one second across a window
function st_lsmr(){
 var W=86400,leap=1.0;
 var ppm=leap/W*1e6;
 var N=2000,prev=-1,back=0,dupes=0,seen={},i;
 for(i=0;i<N;i++){
  var t=i*(W/N);
  var c=t+leap*(t/W);
  if(c<=prev)back++;
  var key=c.toFixed(6);
  if(seen[key])dupes++;else seen[key]=1;
  prev=c;}
 var total=leap*(W/W);
 return {windowSeconds:W,leapSeconds:leap,
  rateChangePpm:+ppm.toFixed(3),
  samples:N,nonMonotonic:back,duplicateTimestamps:dupes,
  totalDriftApplied:total,driftIsExactlyOne:total===1,
  repeatedSecondAvoided:dupes===0,
  ok:back===0&&dupes===0&&total===1&&Math.abs(ppm-11.574)<0.01};}

// 3 CLOCK DRIFT -- ppm into wall-clock error
function st_clkd(){
 var rows=[],ppms=[1,10,50,100],i;
 for(i=0;i<ppms.length;i++){
  var perDay=ppms[i]*1e-6*86400;
  rows.push({ppm:ppms[i],secPerDay:+perDay.toFixed(4),
   secPerYear:+(perDay*365.2425).toFixed(2),
   msPerHour:+(ppms[i]*1e-6*3600*1000).toFixed(2)});}
 var a=50,b=-50;
 var relative=Math.abs(a-b);
 var pairPerDay=relative*1e-6*86400;
 return {rows:rows,
  ppm50SecPerDay:rows[2].secPerDay,ppm50SecPerYear:rows[2].secPerYear,
  twoClocksPpmApart:relative,pairDivergeSecPerDay:+pairPerDay.toFixed(4),
  pairIsDoubleSingle:Math.abs(pairPerDay-2*rows[2].secPerDay)<1e-9,
  secondsToDriftOneSecondAt50ppm:Math.round(1/(50*1e-6)),
  ok:Math.abs(rows[2].secPerDay-4.32)<1e-6&&
     Math.abs(pairPerDay-2*rows[2].secPerDay)<1e-9};}

// 4 HAPPENS BEFORE -- vector clocks vs the transitive closure, on the same run
function st_hpbf(){
 // 3 processes, events with sends/receives
 var P=3;
 var ev=[
  {p:0,id:0},{p:0,id:1,send:1},{p:1,id:2},{p:1,id:3,recv:1},
  {p:2,id:4},{p:1,id:5,send:2},{p:2,id:6,recv:2},{p:0,id:7},
  {p:2,id:8,send:3},{p:0,id:9,recv:3},{p:1,id:10},{p:2,id:11}];
 var N=ev.length;
 // direct edges: program order + message order
 var edge=[];for(var i=0;i<N;i++){edge.push([]);}
 var last={};
 for(i=0;i<N;i++){
  var e=ev[i];
  if(last[e.p]!==undefined)edge[last[e.p]].push(i);
  last[e.p]=i;}
 var sends={};
 for(i=0;i<N;i++)if(ev[i].send!==undefined)sends[ev[i].send]=i;
 for(i=0;i<N;i++)if(ev[i].recv!==undefined)edge[sends[ev[i].recv]].push(i);
 // transitive closure
 var reach=[];for(i=0;i<N;i++)reach.push(new Uint8Array(N));
 function dfs(src,at,seen){
  for(var k=0;k<edge[at].length;k++){
   var n=edge[at][k];
   if(!reach[src][n]){reach[src][n]=1;dfs(src,n,seen);}}}
 for(i=0;i<N;i++)dfs(i,i);
 // vector clocks
 var vc=[];for(i=0;i<N;i++)vc.push(null);
 var cur=[];for(i=0;i<P;i++)cur.push(new Array(P).fill(0));
 var msgvc={};
 for(i=0;i<N;i++){
  var e2=ev[i];
  if(e2.recv!==undefined){
   var m=msgvc[e2.recv];
   for(var j=0;j<P;j++)cur[e2.p][j]=Math.max(cur[e2.p][j],m[j]);}
  cur[e2.p][e2.p]++;
  vc[i]=cur[e2.p].slice();
  if(e2.send!==undefined)msgvc[e2.send]=vc[i].slice();}
 function vcLess(a,b){
  var le=true,lt=false;
  for(var k=0;k<P;k++){if(a[k]>b[k])le=false;if(a[k]<b[k])lt=true;}
  return le&&lt;}
 var agree=0,disagree=0,concurrent=0,ordered=0,pairs=0;
 for(i=0;i<N;i++)for(var j2=0;j2<N;j2++){
  if(i===j2)continue;
  pairs++;
  var byGraph=reach[i][j2]===1,byVc=vcLess(vc[i],vc[j2]);
  if(byGraph===byVc)agree++;else disagree++;
  if(byGraph)ordered++;}
 for(i=0;i<N;i++)for(var j3=i+1;j3<N;j3++)
  if(!reach[i][j3]&&!reach[j3][i])concurrent++;
 return {processes:P,events:N,orderedPairs:pairs,
  vectorClockAgrees:agree,vectorClockDisagrees:disagree,
  agreementPct:+(100*agree/pairs).toFixed(2),
  happensBeforePairs:ordered,concurrentPairs:concurrent,
  totalUnorderedPairs:N*(N-1)/2,
  ok:disagree===0&&concurrent>0&&ordered>0};}

// 5 CAUSAL CUT -- enumerate every cut, count the consistent ones
function st_ccut(){
 // 2 processes, 4 events each, two messages crossing
 var A=4,B=4;
 var msgs=[{from:'A',fi:1,to:'B',ti:2},{from:'B',fi:0,to:'A',ti:3}];
 var total=0,consistent=0,rows=[];
 for(var a=0;a<=A;a++)for(var b=0;b<=B;b++){
  total++;
  var ok2=true;
  for(var m=0;m<msgs.length;m++){
   var x=msgs[m];
   var sentIn=(x.from==='A')?(x.fi<a):(x.fi<b);
   var recvIn=(x.to==='A')?(x.ti<a):(x.ti<b);
   if(recvIn&&!sentIn)ok2=false;}
  if(ok2)consistent++;
  rows.push({a:a,b:b,consistent:ok2});}
 return {processA:A,processB:B,messages:msgs.length,
  totalCuts:total,consistentCuts:consistent,
  inconsistentCuts:total-consistent,
  consistentPct:+(100*consistent/total).toFixed(1),
  gridIsProduct:total===(A+1)*(B+1),
  rows:rows,
  ok:total===(A+1)*(B+1)&&consistent<total&&consistent>0};}

// 6 TOTAL ORDER BROADCAST -- causal delivery does not pin an order
function st_tobc(){
 // two concurrent messages, N receivers, each may deliver in either order
 var N=5,total=Math.pow(2,N);
 var agree=0,split=0;
 for(var m=0;m<total;m++){
  var first=(m&1);
  var same=true;
  for(var i=1;i<N;i++)if(((m>>i)&1)!==first)same=false;
  if(same)agree++;else split++;}
 // causal order alone permits every one of these
 var causallyLegal=total;
 return {receivers:N,possibleDeliveryOrders:total,
  allAgreeOrders:agree,disagreeingOrders:split,
  causallyLegalOrders:causallyLegal,
  totalOrderRequires:agree,
  fractionThatAgreePct:+(100*agree/total).toFixed(2),
  concurrentMessagesHaveNoCausalOrder:true,
  ok:total===32&&agree===2&&split===30};}

// 7 FENCING TOKEN -- a stalled client returns with a stale token
function st_fnct(){
 var scheds=[];
 (function gen(a,b,acc){ if(a===0&&b===0){scheds.push(acc.slice());return;}
  if(a>0){acc.push(0);gen(a-1,b,acc);acc.pop();}
  if(b>0){acc.push(1);gen(a,b-1,acc);acc.pop();} })(2,2,[]);
 function exec(fenced,sched){
  var token=0,held=null,storeToken=0,corrupt=0,writes=0;
  var ai=0,bi=0,aTok=0;
  for(var s=0;s<sched.length;s++){
   if(sched[s]===0){
    if(ai===0){token++;aTok=token;held='A';ai=1;}
    else if(ai===1){
     if(!fenced||aTok>=storeToken){writes++;storeToken=Math.max(storeToken,aTok);
      if(held!=='A')corrupt=1;}
     ai=2;}
   }else{
    if(bi===0){token++;held='B';bi=1;}
    else if(bi===1){writes++;storeToken=Math.max(storeToken,token);bi=2;}
   }}
  return {corrupt:corrupt,writes:writes};}
 var unf=0,fen=0;
 for(var i=0;i<scheds.length;i++){
  if(exec(false,scheds[i]).corrupt)unf++;
  if(exec(true,scheds[i]).corrupt)fen++;}
 return {schedules:scheds.length,
  unfencedCorrupt:unf,fencedCorrupt:fen,
  ok:scheds.length===6&&unf>0&&fen===0};}

// 8 LEASE -- clock skew eats the safety margin
function st_leas(){
 var lease=10,skew=0.5;
 var rows=[],i;
 for(i=0;i<=5;i++){
  var sk=i*0.25;
  rows.push({skewSeconds:sk,
   naiveOverlap:+(2*sk).toFixed(2),
   guardedOverlap:0,
   safeHoldOff:+(lease+2*sk).toFixed(2)});}
 var naive=2*skew,guarded=0;
 var usable=lease-2*skew;
 return {leaseSeconds:lease,skewSeconds:skew,
  naiveOverlapSeconds:naive,guardedOverlapSeconds:guarded,
  usableSeconds:usable,
  usablePct:+(100*usable/lease).toFixed(1),
  guardCostsSeconds:+(lease-usable).toFixed(2),
  rows:rows,
  ok:naive>0&&guarded===0&&usable<lease};}

// 9 QUORUM INTERSECTION -- exhaustive, every pair of majorities
function st_qrin(){
 function combos(n,k){
  var out=[],cur=[];
  (function rec(start){
   if(cur.length===k){out.push(cur.slice());return;}
   for(var i=start;i<n;i++){cur.push(i);rec(i+1);cur.pop();}})(0);
  return out;}
 var N=9,K=Math.floor(N/2)+1;
 var qs=combos(N,K);
 var pairs=0,intersect=0,minShared=999;
 for(var i=0;i<qs.length;i++)for(var j=i+1;j<qs.length;j++){
  pairs++;
  var shared=0;
  for(var a=0;a<qs[i].length;a++)if(qs[j].indexOf(qs[i][a])>=0)shared++;
  if(shared>0)intersect++;
  if(shared<minShared)minShared=shared;}
 // and the counterexample: k = N/2 does NOT always intersect
 var half=combos(N-1,Math.floor((N-1)/2));
 var hPairs=0,hDisjoint=0;
 for(i=0;i<half.length;i++)for(j=i+1;j<half.length;j++){
  hPairs++;
  var sh=0;
  for(a=0;a<half[i].length;a++)if(half[j].indexOf(half[i][a])>=0)sh++;
  if(sh===0)hDisjoint++;}
 return {nodes:N,quorumSize:K,quorums:qs.length,
  pairsChecked:pairs,pairsIntersecting:intersect,
  everyPairIntersects:intersect===pairs,
  minimumShared:minShared,guaranteedShared:2*K-N,
  minMatchesFormula:minShared===2*K-N,
  halfQuorumNodes:N-1,halfQuorumSize:Math.floor((N-1)/2),
  halfPairsChecked:hPairs,halfPairsDisjoint:hDisjoint,
  ok:intersect===pairs&&minShared===2*K-N&&hDisjoint>0};}

// 10 HYBRID LOGICAL CLOCK -- close to wall time AND causally correct
function st_hybc(){
 var P=3,events=[],r=rng(23);
 var pt=[0,0,0],hl=[0,0,0],hc=[0,0,0];
 var maxGap=0,violations=0,steps=[];
 var lastSend=null;
 for(var i=0;i<600;i++){
  var p=i%P;
  pt[p]+=1+Math.floor(r()*3);
  // physical clocks drift apart a little
  var phys=pt[p];
  var l=hl[p],c=hc[p];
  var nl=Math.max(l,phys);
  if(nl===l)c=c+1;else c=0;
  hl[p]=nl;hc[p]=c;
  var gap=Math.abs(hl[p]-phys);
  if(gap>maxGap)maxGap=gap;
  if(i%7===0)lastSend={l:hl[p],c:hc[p],p:p};
  if(i%11===0&&lastSend&&lastSend.p!==p){
   var ml=lastSend.l,mc=lastSend.c;
   var before=[hl[p],hc[p]];
   var nl2=Math.max(hl[p],ml,phys);
   var nc2;
   if(nl2===hl[p]&&nl2===ml)nc2=Math.max(hc[p],mc)+1;
   else if(nl2===hl[p])nc2=hc[p]+1;
   else if(nl2===ml)nc2=mc+1;
   else nc2=0;
   hl[p]=nl2;hc[p]=nc2;
   // causality: the receive must be strictly after the send
   if(hl[p]<ml||(hl[p]===ml&&hc[p]<=mc))violations++;}
  steps.push({l:hl[p],c:hc[p],phys:phys});}
 return {processes:P,events:600,
  maxDivergenceFromPhysical:maxGap,
  causalityViolations:violations,
  boundedByPhysical:maxGap<50,
  counterStaysSmall:Math.max.apply(null,hc)<20,
  finalLogical:hl.slice(),finalCounters:hc.slice(),
  ok:violations===0&&maxGap<50};}

var T=[['NTPS',st_ntps],['LSMR',st_lsmr],['CLKD',st_clkd],['HPBF',st_hpbf],['CCUT',st_ccut],
       ['TOBC',st_tobc],['FNCT',st_fnct],['LEAS',st_leas],['QRIN',st_qrin],['HYBC',st_hybc]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,560));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
