// BATCH 264 claims -- THE SHAPE OF FAILURE.
// Ran 8/10 clean on the first pass. SPLB and CASF failed their own gates and
// were REBUILT, not reported: SPLB asserted that some partition of 5 nodes
// leaves no leader (it never does -- one side always holds three), and CASF ran
// with capacity above the base load, so nothing failed and there was no cascade
// to measure. The corrected pair is at the bottom of this file and is what
// shipped. Every published LIT number was then re-derived live from the built
// page before sealing.

// BATCH 264 -- the shape of failure.
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

// 1 PARTIAL FAILURE -- the third outcome nobody designs for
function st_prtf(){
 var N=100000,r=rng(3),ok=0,fail=0,unknown=0,i;
 for(i=0;i<N;i++){
  var u=r();
  if(u<0.94)ok++;                     // request arrived, reply arrived
  else if(u<0.97)fail++;              // request never arrived -- safe to retry
  else unknown++;}                    // request arrived, reply lost -- unknown
 // retry safety: only the fail bucket is safe without idempotency
 var safeToRetry=fail,unsafe=unknown;
 var dupRisk=unknown/N;
 return {requests:N,succeeded:ok,cleanlyFailed:fail,unknown:unknown,
  unknownPct:+(100*unknown/N).toFixed(2),
  safeToRetryWithoutIdempotency:safeToRetry,
  retryingUnknownDuplicates:unsafe,
  duplicateRiskPct:+(100*dupRisk).toFixed(2),
  withIdempotencyKeyAllSafe:N,
  ok:unknown>0&&safeToRetry<N};}

// 2 POISON MESSAGE -- one bad item, retried forever
function st_psnm(){
 function run(maxAttempts){
  var Q=[],i,processed=0,work=0,stuck=0;
  for(i=0;i<1000;i++)Q.push({id:i,poison:(i===7)});
  var attempts={},head=0,guard=0;
  while(head<Q.length&&guard<200000){
   guard++;
   var m=Q[head];
   attempts[m.id]=(attempts[m.id]||0)+1;
   work++;
   if(m.poison){
    if(maxAttempts>0&&attempts[m.id]>=maxAttempts){head++;stuck++;continue;}
    continue;}
   processed++;head++;}
  return {processed:processed,work:work,deadLettered:stuck,drained:head>=Q.length};}
 var none=run(0),dlq=run(3);
 return {messages:1000,poisonAt:7,
  noDlqProcessed:none.processed,noDlqWork:none.work,noDlqDrained:none.drained,
  dlqProcessed:dlq.processed,dlqWork:dlq.work,dlqDrained:dlq.drained,
  dlqDeadLettered:dlq.deadLettered,
  oneMessageBlockedTheRest:none.processed<999,
  ok:none.drained===false&&dlq.drained===true&&dlq.processed===999};}

// 3 SPLIT BRAIN -- quorum is what stops two leaders, exhaustively
function st_splb(){
 var N=5,total=Math.pow(2,N),bothLead=0,quorumBoth=0,noLeader=0,rows=[];
 for(var m=0;m<total;m++){
  var a=0;for(var i=0;i<N;i++)if((m>>i)&1)a++;
  var b=N-a;
  // naive: any non-empty side elects a leader
  if(a>0&&b>0)bothLead++;
  // quorum: a side leads only with a strict majority
  var aq=a>N/2,bq=b>N/2;
  if(aq&&bq)quorumBoth++;
  if(!aq&&!bq)noLeader++;}
 for(var k=0;k<=N;k++)rows.push({sideA:k,sideB:N-k,
  naiveLeaders:(k>0&&N-k>0)?2:1,
  quorumLeaders:((k>N/2)?1:0)+((N-k>N/2)?1:0)});
 return {nodes:N,partitions:total,
  naiveBothLead:bothLead,quorumBothLead:quorumBoth,
  quorumNoLeader:noLeader,
  quorumNeverAllowsTwo:quorumBoth===0,
  availabilityCost:+(100*noLeader/total).toFixed(2),
  rows:rows,exhaustive:true,
  ok:bothLead>0&&quorumBoth===0&&noLeader>0};}

// 4 GRAY FAILURE -- the probe and the user do not see the same machine
function st_gryf(){
 var N=200000,r=rng(7),probeOk=0,userOk=0,i;
 for(i=0;i<N;i++){
  // health probe: tiny, cached, no dependencies -- succeeds unless truly down
  if(r()<0.999)probeOk++;
  // real request: touches the slow dependency
  if(r()<0.62)userOk++;}
 var probePct=100*probeOk/N,userPct=100*userOk/N;
 return {samples:N,
  probeSuccessPct:+probePct.toFixed(2),
  userSuccessPct:+userPct.toFixed(2),
  gapPoints:+(probePct-userPct).toFixed(2),
  probeSaysHealthy:probePct>99,userSaysBroken:userPct<70,
  nodeIsRemovedFromRotation:false,
  ok:probePct>99&&userPct<70};}

// 5 CASCADING FAILURE -- retries multiply the load that caused them
function st_casf(){
 var rows=[],base=1000,i;
 for(var retries=0;retries<=4;retries++){
  var amp=1;
  for(i=1;i<=retries;i++)amp+=1;
  rows.push({retries:retries,amplification:amp,offeredLoad:base*amp});}
 // a dependency at 90% capacity; each retry adds load, which adds failures
 var cap=1200,load=base,fails=0,steps=[];
 for(i=0;i<8;i++){
  var served=Math.min(load,cap);
  var failed=load-served;
  steps.push({round:i,offered:load,served:served,failed:failed});
  load=base+failed*2;                 // every failure retried twice
  fails=failed;}
 var stable=steps[steps.length-1].failed===steps[steps.length-2].failed;
 return {baseLoad:base,capacity:cap,rows:rows,
  retriesPerFailure:2,
  finalOffered:steps[steps.length-1].offered,
  finalFailed:steps[steps.length-1].failed,
  amplificationAtEnd:+(steps[steps.length-1].offered/base).toFixed(2),
  steps:steps,convergedNotRecovered:stable&&steps[steps.length-1].failed>0,
  ok:steps[steps.length-1].offered>base&&steps[steps.length-1].failed>0};}

// 6 METASTABLE FAILURE -- two thresholds, and the gap between them
function st_metf(){
 // load at which it breaks vs load at which it recovers
 var cap=1000,trigger=0,recover=0,l;
 for(l=800;l<=2000;l+=10){
  // healthy start: breaks when offered exceeds capacity
  if(l>cap){trigger=l;break;}}
 // once broken, retries keep offered high: recovery needs load far below cap
 var amp=3;
 for(l=1000;l>=0;l-=10){
  if(l*amp<=cap){recover=l;break;}}
 var gap=trigger-recover;
 return {capacity:cap,retryAmplification:amp,
  breaksAtLoad:trigger,recoversAtLoad:recover,
  hysteresisGap:gap,
  gapAsPctOfCapacity:+(100*gap/cap).toFixed(1),
  removingTheTriggerIsNotEnough:recover<trigger,
  ok:recover<trigger&&gap>0};}

// 7 CORRELATED FAILURE -- independence is the whole assumption
function st_corf(){
 var p=0.01,n=3,rows=[];
 for(var rho=0;rho<=1.0001;rho+=0.2){
  // with correlation rho, P(all fail) interpolates between p^n and p
  var indep=Math.pow(p,n);
  var allFail=indep+(p-indep)*rho;
  rows.push({rho:+rho.toFixed(1),
   allFailProb:allFail,
   nines:+(-Math.log(allFail)/Math.LN10).toFixed(2)});}
 var indep=Math.pow(p,n),full=p;
 return {replicas:n,singleFailureProb:p,
  independentAllFail:indep,independentNines:+(-Math.log(indep)/Math.LN10).toFixed(2),
  fullyCorrelatedAllFail:full,fullyCorrelatedNines:+(-Math.log(full)/Math.LN10).toFixed(2),
  ratio:Math.round(full/indep),
  rows:rows,
  atRhoPoint2Nines:rows[1].nines,
  ok:full/indep>1000&&rows[0].nines>rows[5].nines};}

// 8 SILENT CORRUPTION -- what a checksum is actually for
function st_silc(){
 var N=200000,r=rng(11),bitErr=1e-4,blocks=0,corrupted=0,caught=0,silent=0,i;
 function crc8(b){var c=0,j;for(j=0;j<b.length;j++){c^=b[j];
  for(var k=0;k<8;k++)c=(c&128)?(((c<<1)^7)&255):((c<<1)&255);}return c;}
 for(i=0;i<N;i++){
  blocks++;
  var block=[(i*37)&255,(i*91)&255,(i*13)&255,(i*57)&255];
  var sum=crc8(block);
  var hit=r()<bitErr*32;
  if(hit){
   corrupted++;
   var pos=Math.floor(r()*4),bit=1<<Math.floor(r()*8);
   block[pos]^=bit;
   if(crc8(block)!==sum)caught++;else silent++;}}
 return {blocks:blocks,bitErrorRate:bitErr,
  corruptedBlocks:corrupted,caughtByCrc:caught,silentlyPassed:silent,
  detectionPct:+(100*caught/Math.max(1,corrupted)).toFixed(2),
  withoutChecksumAllSilent:corrupted,
  crc8EscapeRate:+(silent/Math.max(1,corrupted)).toFixed(6),
  ok:corrupted>0&&caught>0&&caught>silent};}

// 9 BACKPRESSURE -- refusing work is a feature
function st_bkpr(){
 function run(bounded){
  var T=20000,r=rng(13),q=0,served=0,shed=0,waitSum=0,waitN=0,cap=100;
  for(var t=0;t<T;t++){
   var arr=(r()<0.35)?2:1;
   for(var k=0;k<arr;k++){
    if(bounded&&q>=cap){shed++;continue;}
    q++;}
   if(q>0){waitSum+=q;waitN++;q--;served++;}}
  return {served:served,shed:shed,queue:q,
   meanWait:+(waitSum/Math.max(1,waitN)).toFixed(1)};}
 var un=run(false),bd=run(true);
 return {ticks:20000,capacity:100,
  unboundedServed:un.served,unboundedShed:un.shed,
  unboundedFinalQueue:un.queue,unboundedMeanWait:un.meanWait,
  boundedServed:bd.served,boundedShed:bd.shed,
  boundedFinalQueue:bd.queue,boundedMeanWait:bd.meanWait,
  waitRatio:+(un.meanWait/bd.meanWait).toFixed(1),
  throughputDiff:un.served-bd.served,
  ok:un.meanWait>bd.meanWait*5&&Math.abs(un.served-bd.served)<un.served*0.02};}

// 10 CIRCUIT BREAKER -- stop asking a thing that is not answering
function st_cirb(){
 function run(useBreaker){
  var T=6000,calls=0,failed=0,rejected=0,state='closed',consec=0,openedAt=-1,i;
  for(i=0;i<T;i++){
   var down=(i>=1000&&i<3000);
   if(useBreaker&&state==='open'){
    if(i-openedAt>=200){state='half';}
    else {rejected++;continue;}}
   calls++;
   var fail=down;
   if(fail){failed++;consec++;
    if(useBreaker&&consec>=5){state='open';openedAt=i;}}
   else {consec=0;if(state==='half')state='closed';}}
  return {calls:calls,failed:failed,rejected:rejected,state:state};}
 var off=run(false),on=run(true);
 return {ticks:6000,outageFrom:1000,outageTo:3000,
  noBreakerCalls:off.calls,noBreakerFailed:off.failed,
  breakerCalls:on.calls,breakerFailed:on.failed,breakerRejected:on.rejected,
  wastedCallsAvoided:off.failed-on.failed,
  reductionPct:+(100*(1-on.failed/off.failed)).toFixed(1),
  probesDuringOutage:Math.floor(2000/200),
  ok:on.failed<off.failed&&on.rejected>0};}

var T=[['PRTF',st_prtf],['PSNM',st_psnm],['SPLB',st_splb],['GRYF',st_gryf],['CASF',st_casf],
       ['METF',st_metf],['CORF',st_corf],['SILC',st_silc],['BKPR',st_bkpr],['CIRB',st_cirb]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,520));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}


// ===== CORRECTED GATES (these shipped) =====
// SPLB -- my gate demanded "some partition leaves no leader". With N=5 and a
// TWO-WAY split that never happens: one side always holds 3 or more. That is not
// a bug, it is exactly WHY clusters are odd-sized, and it only shows up by
// sweeping N. Even N has the tie.
function st_splb(){
 function sweep(N){
  var total=Math.pow(2,N),naiveTwo=0,quorumTwo=0,quorumZero=0;
  for(var m=0;m<total;m++){
   var a=0;for(var i=0;i<N;i++)if((m>>i)&1)a++;
   var b=N-a;
   if(a>0&&b>0)naiveTwo++;
   var aq=a>N/2,bq=b>N/2;
   if(aq&&bq)quorumTwo++;
   if(!aq&&!bq)quorumZero++;}
  return {N:N,partitions:total,naiveTwo:naiveTwo,quorumTwo:quorumTwo,
   quorumZero:quorumZero,
   zeroPct:+(100*quorumZero/total).toFixed(2)};}
 var rows=[],n;
 for(n=3;n<=8;n++)rows.push(sweep(n));
 var five=sweep(5),four=sweep(4);
 var oddAlwaysOne=rows.filter(function(r){return r.N%2===1;})
   .every(function(r){return r.quorumZero===0&&r.quorumTwo===0;});
 var evenHasTie=rows.filter(function(r){return r.N%2===0;})
   .every(function(r){return r.quorumZero>0;});
 return {rows:rows,
  atFiveNaiveTwoLeaders:five.naiveTwo,atFivePartitions:five.partitions,
  atFiveQuorumTwoLeaders:five.quorumTwo,atFiveQuorumNoLeader:five.quorumZero,
  atFourQuorumNoLeader:four.quorumZero,atFourPartitions:four.partitions,
  atFourNoLeaderPct:four.zeroPct,
  quorumNeverAllowsTwoAtAnyN:rows.every(function(r){return r.quorumTwo===0;}),
  oddSizesAlwaysElectExactlyOne:oddAlwaysOne,
  evenSizesCanDeadlock:evenHasTie,
  exhaustive:true,
  ok:five.naiveTwo>0&&rows.every(function(r){return r.quorumTwo===0;})&&
     oddAlwaysOne&&evenHasTie};}

// CASF -- capacity 1200 sat ABOVE the base load of 1000, so nothing ever failed
// and there was no cascade to measure. A cascade needs the dependency to lose
// capacity; the retries are what stop it recovering when it comes back.
function st_casf(){
 var base=1000,healthy=1200,degraded=600,retries=2;
 var load=base,steps=[],i;
 for(i=0;i<10;i++){
  var cap=(i>=2&&i<5)?degraded:healthy;   // a three-round degradation, then it heals
  var served=Math.min(load,cap),failed=load-served;
  steps.push({round:i,capacity:cap,offered:load,served:served,failed:failed});
  load=base+failed*retries;}
 var duringWorst=steps[4],afterHeal=steps[9];
 var peak=0;for(i=0;i<steps.length;i++)if(steps[i].offered>peak)peak=steps[i].offered;
 return {baseLoad:base,healthyCapacity:healthy,degradedCapacity:degraded,
  retriesPerFailure:retries,degradedRounds:3,
  peakOffered:peak,peakAmplification:+(peak/base).toFixed(2),
  offeredAtWorst:duringWorst.offered,failedAtWorst:duringWorst.failed,
  capacityRestoredAtRound:5,
  offeredAfterHeal:afterHeal.offered,failedAfterHeal:afterHeal.failed,
  recoveredAfterCapacityReturned:afterHeal.failed===0,
  steps:steps,
  ok:peak>base&&duringWorst.failed>0};}

var T=[['SPLB',st_splb],['CASF',st_casf]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,760));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
