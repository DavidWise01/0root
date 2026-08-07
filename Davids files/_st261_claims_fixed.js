// FNCT and LEAS, corrected.
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

// FNCT -- the first model tracked "who holds the lock", which is not what fencing
// protects. Corruption is structural: a write LANDS carrying a token older than
// the highest token the store has already accepted. Under fencing the guard makes
// that state unreachable, which is the whole claim, so it must be counted and not
// assumed.
function st_fnct(){
 var scheds=[];
 (function gen(a,b,acc){ if(a===0&&b===0){scheds.push(acc.slice());return;}
  if(a>0){acc.push(0);gen(a-1,b,acc);acc.pop();}
  if(b>0){acc.push(1);gen(a,b-1,acc);acc.pop();} })(2,2,[]);
 function exec(fenced,sched){
  var token=0,storeToken=0,corrupt=0,writes=0,rejected=0;
  var ai=0,bi=0,aTok=0,bTok=0;
  for(var s=0;s<sched.length;s++){
   if(sched[s]===0){
    if(ai===0){token++;aTok=token;ai=1;}
    else if(ai===1){
     if(fenced&&aTok<storeToken)rejected++;
     else {if(aTok<storeToken)corrupt=1;storeToken=Math.max(storeToken,aTok);writes++;}
     ai=2;}
   }else{
    if(bi===0){token++;bTok=token;bi=1;}
    else if(bi===1){
     if(fenced&&bTok<storeToken)rejected++;
     else {if(bTok<storeToken)corrupt=1;storeToken=Math.max(storeToken,bTok);writes++;}
     bi=2;}
   }}
  return {corrupt:corrupt,writes:writes,rejected:rejected};}
 var unf=0,fen=0,rej=0,bad=[];
 for(var i=0;i<scheds.length;i++){
  var u=exec(false,scheds[i]),f=exec(true,scheds[i]);
  if(u.corrupt){unf++;bad.push(scheds[i].join(''));}
  if(f.corrupt)fen++;
  rej+=f.rejected;}
 return {schedules:scheds.length,
  unfencedCorrupt:unf,fencedCorrupt:fen,
  fencedRejections:rej,corruptingSchedules:bad,
  ok:scheds.length===6&&unf>0&&fen===0&&rej>0};}

// LEAS -- the first version WROTE guardedOverlap = 0 into every row rather than
// measuring it, which is the same mistake as asserting a fairness result. Run both
// disciplines over one timeline and COUNT the instants where two holders overlap.
function st_leas(){
 var LEASE=10,STEP=0.01;
 function run(skew,guard){
  // holder A takes the lease at t=0 by its own clock, which is fast by +skew.
  // holder B may take it once A's lease has expired by B's clock, slow by -skew.
  var aExpiresTrue=LEASE-skew;              // A believes it holds until LEASE
  var bStartsTrue=LEASE+skew-(guard?0:2*skew);
  if(guard)bStartsTrue=LEASE+skew;
  var overlap=0,ticks=0;
  for(var t=0;t<LEASE+4*skew+1;t+=STEP){
   ticks++;
   var aHolds=t<LEASE+skew;                 // A keeps writing until ITS clock says so
   var bHolds=t>=bStartsTrue;
   if(aHolds&&bHolds)overlap++;}
  return {overlapTicks:overlap,overlapSeconds:+(overlap*STEP).toFixed(2),ticks:ticks};}
 var skew=0.5;
 var naive=run(skew,false),guarded=run(skew,true);
 var rows=[],i;
 for(i=0;i<=5;i++){
  var sk=i*0.25;
  var n=run(sk,false),g=run(sk,true);
  rows.push({skewSeconds:sk,naiveOverlap:n.overlapSeconds,guardedOverlap:g.overlapSeconds});}
 var usable=LEASE-2*skew;
 return {leaseSeconds:LEASE,skewSeconds:skew,resolutionSeconds:STEP,
  naiveOverlapSeconds:naive.overlapSeconds,
  guardedOverlapSeconds:guarded.overlapSeconds,
  overlapMeasuredNotAssumed:true,
  usableSeconds:usable,usablePct:+(100*usable/LEASE).toFixed(1),
  guardCostsSeconds:+(LEASE-usable).toFixed(2),
  rows:rows,
  ok:naive.overlapSeconds>0&&guarded.overlapSeconds===0&&usable<LEASE};}

var T=[['FNCT',st_fnct],['LEAS',st_leas]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
