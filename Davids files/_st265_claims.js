// BATCH 265 -- WHO RUNS NEXT. Scheduling.
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

// 1 CONVOY EFFECT -- one long job, and everything short waits behind it
function st_cnvy(){
 var r=rng(3),jobs=[],i;
 for(i=0;i<200;i++)jobs.push(r()<0.05?200+Math.floor(r()*100):1+Math.floor(r()*8));
 function meanWait(order){
  var t=0,w=0,k;
  for(k=0;k<order.length;k++){w+=t;t+=order[k];}
  return {meanWait:w/order.length,makespan:t};}
 var fifo=meanWait(jobs.slice());
 var sjf =meanWait(jobs.slice().sort(function(a,b){return a-b;}));
 var longJobs=jobs.filter(function(j){return j>100;}).length;
 return {jobs:jobs.length,longJobs:longJobs,
  shortJobs:jobs.length-longJobs,
  fifoMeanWait:+fifo.meanWait.toFixed(1),
  sjfMeanWait:+sjf.meanWait.toFixed(1),
  ratio:+(fifo.meanWait/sjf.meanWait).toFixed(2),
  makespanFifo:fifo.makespan,makespanSjf:sjf.makespan,
  sameTotalWork:fifo.makespan===sjf.makespan,
  ok:fifo.meanWait>sjf.meanWait&&fifo.makespan===sjf.makespan};}

// 2 WORK STEALING -- idle workers take from whoever still has some
function st_wstl(){
 var r=rng(5),W=8,N=2000,i,k;
 var tasks=[];for(i=0;i<N;i++)tasks.push(1+Math.floor(r()*20));
 // static: round-robin partition up front, each worker runs its own to the end
 var stat=[];for(i=0;i<W;i++)stat.push(0);
 for(i=0;i<N;i++)stat[i%W]+=tasks[i];
 var staticMakespan=Math.max.apply(null,stat);
 // stealing: same partition, but an idle worker takes the back of the longest queue
 var q=[];for(i=0;i<W;i++)q.push([]);
 for(i=0;i<N;i++)q[i%W].push(tasks[i]);
 var load=[];for(i=0;i<W;i++)load.push(0);
 var steals=0,guard=0;
 while(guard++<200000){
  // every worker drains its own queue; when empty it steals from the longest
  var idle=-1,longest=-1,lmax=0;
  for(k=0;k<W;k++){
   if(q[k].length===0&&idle<0)idle=k;
   if(q[k].length>lmax){lmax=q[k].length;longest=k;}}
  if(idle<0){ // nobody idle: everyone pops one
   var any=false;
   for(k=0;k<W;k++)if(q[k].length){load[k]+=q[k].shift();any=true;}
   if(!any)break;
   continue;}
  if(lmax<2)break;                       // nothing worth stealing
  q[idle].push(q[longest].pop());steals++;}
 for(k=0;k<W;k++)while(q[k].length)load[k]+=q[k].shift();
 var stealMakespan=Math.max.apply(null,load);
 var total=tasks.reduce(function(a,b){return a+b;},0);
 return {workers:W,tasks:N,totalWork:total,
  idealMakespan:+(total/W).toFixed(1),
  staticMakespan:staticMakespan,
  stealingMakespan:stealMakespan,
  steals:steals,
  staticIdlePct:+(100*(1-total/(W*staticMakespan))).toFixed(2),
  stealingIdlePct:+(100*(1-total/(W*stealMakespan))).toFixed(2),
  ok:stealMakespan<=staticMakespan&&steals>0};}

// 3 FAIR SHARE -- max-min: nobody gets more until everybody small is satisfied
function st_fshr(){
 var demands=[2,2.6,4,10,40],cap=30;
 // max-min: give everyone an equal share; anyone wanting less is capped and
 // their leftover is redivided among the rest
 var alloc=demands.map(function(){return 0;});
 var done=demands.map(function(){return false;});
 var remaining=cap,rounds=0;
 while(true){
  rounds++;
  var open=done.filter(function(d){return !d;}).length;
  if(!open)break;
  var share=remaining/open,progressed=false;
  for(var i=0;i<demands.length;i++){
   if(done[i])continue;
   if(demands[i]<=share){alloc[i]=demands[i];remaining-=demands[i];done[i]=true;progressed=true;}}
  if(!progressed){
   for(var j=0;j<demands.length;j++)if(!done[j]){alloc[j]=remaining/open;done[j]=true;}
   remaining=0;break;}}
 var equal=demands.map(function(){return cap/demands.length;});
 var equalWaste=0;
 for(var k=0;k<demands.length;k++)if(equal[k]>demands[k])equalWaste+=equal[k]-demands[k];
 var served=alloc.reduce(function(a,b){return a+b;},0);
 return {capacity:cap,demands:demands,
  allocation:alloc.map(function(x){return +x.toFixed(3);}),
  totalAllocated:+served.toFixed(3),
  rounds:rounds,
  equalSplit:equal.map(function(x){return +x.toFixed(2);}),
  equalSplitWasted:+equalWaste.toFixed(2),
  smallestFullySatisfied:alloc[0]===demands[0],
  largestGetsRemainder:alloc[4]>alloc[3],
  ok:Math.abs(served-cap)<1e-9&&alloc[0]===demands[0]&&equalWaste>0};}

// 4 STARVATION -- strict priority starves the low; aging is the fix
function st_strv(){
 function run(aging){
  var r=rng(9),T=20000,q=[],served={hi:0,lo:0},waits=[],t,i;
  var lowWaitMax=0;
  for(t=0;t<T;t++){
   if(r()<0.60)q.push({p:0,born:t});        // high priority, heavy arrival
   if(r()<0.20)q.push({p:5,born:t});        // low priority
   if(!q.length)continue;
   var best=0;
   for(i=1;i<q.length;i++){
    var pi=q[i].p-(aging?(t-q[i].born)/500:0);
    var pb=q[best].p-(aging?(t-q[best].born)/500:0);
    if(pi<pb)best=i;}
   var job=q.splice(best,1)[0];
   var w=t-job.born;
   if(job.p===0)served.hi++;else{served.lo++;if(w>lowWaitMax)lowWaitMax=w;}
   waits.push(w);}
  return {hi:served.hi,lo:served.lo,lowWaitMax:lowWaitMax,backlog:q.length};}
 var strict=run(false),aged=run(true);
 return {ticks:20000,
  strictHighServed:strict.hi,strictLowServed:strict.lo,
  strictLowBacklog:strict.backlog,strictLowMaxWait:strict.lowWaitMax,
  agedHighServed:aged.hi,agedLowServed:aged.lo,
  agedLowBacklog:aged.backlog,agedLowMaxWait:aged.lowWaitMax,
  lowServedGain:aged.lo-strict.lo,
  highGaveUp:strict.hi-aged.hi,
  ok:aged.lo>strict.lo&&aged.backlog<strict.backlog};}

// 5 TIME SLICE -- the quantum has an optimum, and both sides of it are bad
function st_tslc(){
 var switchCost=2,jobs=[],r=rng(11),i;
 for(i=0;i<50;i++)jobs.push(5+Math.floor(r()*60));
 function run(q){
  var rem=jobs.slice(),t=0,switches=0,done=[],i2;
  var guard=0;
  while(guard++<400000){
   var any=false;
   for(i2=0;i2<rem.length;i2++){
    if(rem[i2]<=0)continue;
    any=true;
    var slice=Math.min(q,rem[i2]);
    t+=slice;rem[i2]-=slice;
    if(rem[i2]<=0)done.push({job:i2,at:t});
    t+=switchCost;switches++;}
   if(!any)break;}
  var turn=done.reduce(function(a,d){return a+d.at;},0)/done.length;
  var work=jobs.reduce(function(a,b){return a+b;},0);
  return {quantum:q,total:t,switches:switches,
   overhead:switches*switchCost,
   overheadPct:+(100*switches*switchCost/t).toFixed(2),
   meanTurnaround:+turn.toFixed(1)};}
 var rows=[1,2,4,8,16,32,64,128].map(run);
 var best=rows[0];
 for(i=1;i<rows.length;i++)if(rows[i].meanTurnaround<best.meanTurnaround)best=rows[i];
 return {jobs:jobs.length,switchCost:switchCost,rows:rows,
  bestQuantum:best.quantum,bestTurnaround:best.meanTurnaround,
  tinyQuantumOverheadPct:rows[0].overheadPct,
  hugeQuantumTurnaround:rows[rows.length-1].meanTurnaround,
  optimumIsInterior:best.quantum!==rows[0].quantum&&best.quantum!==rows[rows.length-1].quantum,
  ok:rows[0].overheadPct>rows[rows.length-1].overheadPct&&best.meanTurnaround<rows[0].meanTurnaround};}

// 6 LOTTERY -- proportional share by ticket, and how fast it converges
function st_lott(){
 var tickets=[10,20,30,40],total=100,r=rng(13);
 function draw(N){
  var win=[0,0,0,0],i,k;
  for(i=0;i<N;i++){
   var t=r()*total,acc=0;
   for(k=0;k<tickets.length;k++){acc+=tickets[k];if(t<acc){win[k]++;break;}}}
  return win;}
 function err(win,N){
  var e=0;
  for(var k=0;k<tickets.length;k++)e+=Math.abs(win[k]/N-tickets[k]/total);
  return e;}
 var rows=[100,1000,10000,100000].map(function(N){
  var w=draw(N);
  return {draws:N,shares:w.map(function(x){return +(100*x/N).toFixed(2);}),
   absError:+err(w,N).toFixed(4)};});
 var shrinks=true;
 for(var i=1;i<rows.length;i++)if(rows[i].absError>rows[i-1].absError)shrinks=false;
 return {tickets:tickets,targetShares:tickets.map(function(t){return t;}),
  rows:rows,
  errorAt100:rows[0].absError,errorAt100k:rows[3].absError,
  errorShrinks:shrinks,
  shrinkFactor:+(rows[0].absError/rows[3].absError).toFixed(1),
  fairOnlyInTheLimit:rows[0].absError>rows[3].absError*5,
  ok:shrinks&&rows[3].absError<rows[0].absError};}

// 7 CONTEXT SWITCH -- the direct cost is not the cost
function st_ctxs(){
 // a switch costs a fixed save/restore PLUS a cold cache that refills as it runs
 var save=1,footprint=64,missCost=0.5;
 function cost(runLength){
  // after a switch the working set is cold; it warms over the first `footprint`
  // units of run, so the penalty is bounded by how long you get to run
  var warm=Math.min(runLength,footprint);
  return save+warm*missCost;}
 var rows=[1,2,4,8,16,32,64,128,256].map(function(rl){
  var c=cost(rl);
  return {runLength:rl,switchCost:+c.toFixed(2),
   directCost:save,cacheCost:+(c-save).toFixed(2),
   pctOfRun:+(100*c/rl).toFixed(2)};});
 var atOne=rows[0],atBig=rows[rows.length-1];
 return {saveRestore:save,workingSetUnits:footprint,missCost:missCost,
  rows:rows,
  costAtRun1:atOne.switchCost,pctAtRun1:atOne.pctOfRun,
  costAtRun256:atBig.switchCost,pctAtRun256:atBig.pctOfRun,
  cacheShareAtRun256:+(100*atBig.cacheCost/atBig.switchCost).toFixed(1),
  directCostIsConstant:rows.every(function(r){return r.directCost===save;}),
  ok:atOne.pctOfRun>atBig.pctOfRun&&atBig.cacheCost>save};}

// 8 PREEMPTION -- what it buys, and what it charges
function st_prmp(){
 var r=rng(17),T=6000,arrivals=[],i;
 for(i=0;i<T;i++)if(r()<0.05)arrivals.push({at:i,len:1+Math.floor(r()*60),
   urgent:r()<0.15});
 function run(preempt){
  var t=0,q=[],cur=null,switches=0,resp=[],i2,done=0;
  var idx=0;
  for(t=0;t<T*3;t++){
   while(idx<arrivals.length&&arrivals[idx].at<=t){
    var a=arrivals[idx++];q.push({len:a.len,left:a.len,at:a.at,urgent:a.urgent});
    if(preempt&&cur&&a.urgent&&!cur.urgent){q.push(cur);cur=null;switches++;}}
   if(!cur&&q.length){
    var pick=0;
    for(i2=1;i2<q.length;i2++)if(q[i2].urgent&&!q[pick].urgent)pick=i2;
    cur=q.splice(pick,1)[0];
    if(cur.left===cur.len)resp.push({urgent:cur.urgent,resp:t-cur.at});}
   if(cur){cur.left--;if(cur.left<=0){done++;cur=null;}}}
  var urg=resp.filter(function(x){return x.urgent;});
  var norm=resp.filter(function(x){return !x.urgent;});
  function mean(a){return a.length?a.reduce(function(s,x){return s+x.resp;},0)/a.length:0;}
  return {switches:switches,done:done,
   urgentResp:+mean(urg).toFixed(1),normalResp:+mean(norm).toFixed(1),
   urgentN:urg.length,normalN:norm.length};}
 var off=run(false),on=run(true);
 return {arrivals:arrivals.length,
  urgentCount:arrivals.filter(function(a){return a.urgent;}).length,
  nonPreemptiveUrgentResp:off.urgentResp,
  preemptiveUrgentResp:on.urgentResp,
  urgentSpeedup:+(off.urgentResp/Math.max(0.1,on.urgentResp)).toFixed(2),
  nonPreemptiveNormalResp:off.normalResp,
  preemptiveNormalResp:on.normalResp,
  extraSwitches:on.switches-off.switches,
  ok:on.urgentResp<off.urgentResp&&on.switches>off.switches};}

// 9 EARLIEST DEADLINE FIRST -- optimal, and exactly where it stops being safe
function st_edlf(){
 // periodic tasks (period, cost). EDF is schedulable iff utilisation <= 1.
 // Fixed priority (rate-monotonic) has the tighter Liu-Layland bound.
 function util(ts){return ts.reduce(function(a,t){return a+t.c/t.p;},0);}
 function llBound(n){return n*(Math.pow(2,1/n)-1);}
 function simulate(ts,edf,horizon){
  var rem=ts.map(function(){return 0;}),dl=ts.map(function(t){return t.p;});
  var missed=0,t,i;
  for(t=0;t<horizon;t++){
   for(i=0;i<ts.length;i++)if(t%ts[i].p===0){rem[i]+=ts[i].c;dl[i]=t+ts[i].p;}
   var pick=-1;
   for(i=0;i<ts.length;i++){
    if(rem[i]<=0)continue;
    if(pick<0){pick=i;continue;}
    if(edf?(dl[i]<dl[pick]):(ts[i].p<ts[pick].p))pick=i;}
   if(pick>=0)rem[pick]--;
   for(i=0;i<ts.length;i++)if(t===dl[i]-1&&rem[i]>0)missed++;}
  return missed;}
 var set={tasks:[{p:4,c:1},{p:6,c:2},{p:12,c:2}]};
 var u=util(set.tasks),bound=llBound(3);
 var edfMiss=simulate(set.tasks,true,2400);
 var rmMiss =simulate(set.tasks,false,2400);
 return {tasks:set.tasks,
  utilisation:+u.toFixed(4),
  edfBound:1,rateMonotonicBound:+bound.toFixed(4),
  aboveRmBound:u>bound,withinEdfBound:u<=1,
  edfDeadlinesMissed:edfMiss,
  rateMonotonicDeadlinesMissed:rmMiss,
  horizon:2400,
  ok:u>bound&&u<=1&&edfMiss===0};}

// 10 MULTILEVEL FEEDBACK -- approximate SJF without knowing any job's length
function st_mlfq(){
 var r=rng(19),jobs=[],i;
 for(i=0;i<300;i++)jobs.push({len:r()<0.8?1+Math.floor(r()*6):100+Math.floor(r()*200)});
 var total=jobs.reduce(function(a,j){return a+j.len;},0);
 function fifo(){
  var t=0,turn=0;
  for(var k=0;k<jobs.length;k++){t+=jobs[k].len;turn+=t;}
  return turn/jobs.length;}
 function sjf(){
  var s=jobs.slice().sort(function(a,b){return a.len-b.len;});
  var t=0,turn=0;
  for(var k=0;k<s.length;k++){t+=s[k].len;turn+=t;}
  return turn/s.length;}
 function mlfq(){
  // 3 queues, quanta 4/16/64. A job that uses its whole quantum drops a level.
  var Q=[[],[],[]],quanta=[4,16,64],k;
  for(k=0;k<jobs.length;k++)Q[0].push({left:jobs[k].len,done:0});
  var t=0,turn=0,finished=0,guard=0;
  while(finished<jobs.length&&guard++<2000000){
   var lvl=-1;
   for(k=0;k<3;k++)if(Q[k].length){lvl=k;break;}
   if(lvl<0)break;
   var j=Q[lvl].shift();
   var slice=Math.min(quanta[lvl],j.left);
   t+=slice;j.left-=slice;
   if(j.left<=0){turn+=t;finished++;continue;}
   if(slice===quanta[lvl]&&lvl<2)Q[lvl+1].push(j);else Q[lvl].push(j);}
  return turn/jobs.length;}
 var f=fifo(),s=sjf(),m=mlfq();
 return {jobs:jobs.length,totalWork:total,
  shortJobs:jobs.filter(function(j){return j.len<50;}).length,
  fifoTurnaround:+f.toFixed(1),
  sjfTurnaround:+s.toFixed(1),
  mlfqTurnaround:+m.toFixed(1),
  mlfqKnowsNoJobLength:true,
  mlfqBeatsFifoBy:+(f/m).toFixed(2),
  gapToOracle:+(m/s).toFixed(2),
  ok:m<f&&s<=m};}

var T=[['CNVY',st_cnvy],['WSTL',st_wstl],['FSHR',st_fshr],['STRV',st_strv],['TSLC',st_tslc],
       ['LOTT',st_lott],['CTXS',st_ctxs],['PRMP',st_prmp],['EDLF',st_edlf],['MLFQ',st_mlfq]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,560));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}

// WSTL -- 0 steals because a round-robin split of i.i.d. tasks is already
// balanced: 250 random draws per worker converge to the same sum, so there is no
// imbalance for stealing to fix. Static partitioning only hurts when the work is
// SKEWED, which is the case the technique exists for. Contiguous blocks over a
// heavy-tailed list is the real shape: one block lands on the tail.
function st_wstl(){
 var r=rng(5),W=8,N=2000,tasks=[],i,k;
 for(i=0;i<N;i++){
  // heavy tail, and it is not spread evenly through the list
  var heavy=(i>1500&&r()<0.30);
  tasks.push(heavy?200+Math.floor(r()*400):1+Math.floor(r()*10));}
 var total=tasks.reduce(function(a,b){return a+b;},0);
 var ideal=total/W;

 // static: contiguous blocks, decided up front, each worker runs its own to the end
 var block=Math.ceil(N/W),stat=[];
 for(k=0;k<W;k++){
  var s=0;
  for(i=k*block;i<Math.min(N,(k+1)*block);i++)s+=tasks[i];
  stat.push(s);}
 var staticMakespan=Math.max.apply(null,stat);

 // stealing: same blocks, but a worker that empties its own deque takes the next
 // undone task from the most loaded one. Counted as a steal when the task is run
 // by someone other than its original owner.
 var owner=[],left=[];
 for(i=0;i<N;i++){owner.push(Math.min(W-1,Math.floor(i/block)));left.push(tasks[i]);}
 var deque=[];for(k=0;k<W;k++)deque.push([]);
 for(i=0;i<N;i++)deque[owner[i]].push(i);
 var load=[],steals=0;
 for(k=0;k<W;k++)load.push(0);
 var guard=0;
 while(guard++<100000){
  // the worker that will be free soonest picks up the next task
  var free=0;
  for(k=1;k<W;k++)if(load[k]<load[free])free=k;
  var task=-1;
  if(deque[free].length){task=deque[free].shift();}
  else{
   var big=-1,bmax=0;
   for(k=0;k<W;k++)if(deque[k].length>bmax){bmax=deque[k].length;big=k;}
   if(big<0)break;
   task=deque[big].pop();steals++;}
  load[free]+=tasks[task];}
 var stealMakespan=Math.max.apply(null,load);

 return {workers:W,tasks:N,totalWork:total,
  idealMakespan:+ideal.toFixed(1),
  staticMakespan:staticMakespan,
  stealingMakespan:stealMakespan,
  steals:steals,
  staticOverIdeal:+(staticMakespan/ideal).toFixed(3),
  stealingOverIdeal:+(stealMakespan/ideal).toFixed(3),
  staticIdlePct:+(100*(1-total/(W*staticMakespan))).toFixed(2),
  stealingIdlePct:+(100*(1-total/(W*stealMakespan))).toFixed(2),
  speedup:+(staticMakespan/stealMakespan).toFixed(2),
  sameTotalWork:true,
  ok:stealMakespan<staticMakespan&&steals>0};}

// STRV -- both arms identical because arrivals were 0.80/tick against a service
// rate of 1.0: there was always spare capacity, so nothing could starve. Strict
// priority only starves the low queue when the HIGH queue alone can saturate the
// server, so that is where the experiment has to run.
function st_strv(){
 function run(aging,hiRate){
  var r=rng(9),T=20000,q=[],hi=0,lo=0,lowMax=0,t,i;
  for(t=0;t<T;t++){
   if(r()<hiRate)q.push({p:0,born:t});
   if(r()<0.20)q.push({p:5,born:t});
   if(!q.length)continue;
   var best=0;
   for(i=1;i<q.length;i++){
    var pi=q[i].p-(aging?(t-q[i].born)/200:0);
    var pb=q[best].p-(aging?(t-q[best].born)/200:0);
    if(pi<pb)best=i;}
   var job=q.splice(best,1)[0],w=t-job.born;
   if(job.p===0)hi++;else{lo++;if(w>lowMax)lowMax=w;}}
  var backlogLow=0;
  for(i=0;i<q.length;i++)if(q[i].p>0)backlogLow++;
  return {hi:hi,lo:lo,lowMax:lowMax,backlogLow:backlogLow,backlog:q.length};}
 var HI=0.95;                      // high priority alone nearly saturates
 var strict=run(false,HI),aged=run(true,HI);
 return {ticks:20000,highArrivalRate:HI,lowArrivalRate:0.20,serviceRate:1,
  offeredLoad:+(HI+0.20).toFixed(2),
  strictHighServed:strict.hi,strictLowServed:strict.lo,
  strictLowBacklog:strict.backlogLow,strictLowMaxWait:strict.lowMax,
  agedHighServed:aged.hi,agedLowServed:aged.lo,
  agedLowBacklog:aged.backlogLow,agedLowMaxWait:aged.lowMax,
  lowServedGain:aged.lo-strict.lo,
  highGaveUp:strict.hi-aged.hi,
  backlogDrop:strict.backlogLow-aged.backlogLow,
  ok:aged.lo>strict.lo&&aged.backlogLow<strict.backlogLow&&strict.backlogLow>0};}

// LOTT -- the gate demanded the error shrink at every step, which no single
// Monte Carlo run does; 10,000 draws came out worse than 1,000 by chance. The
// real claim is a RATE, and a rate needs many trials averaged, not one walk.
function st_lott(){
 var tickets=[10,20,30,40],total=100,TRIALS=200;
 function meanErr(N,seed0){
  var acc=0;
  for(var tr=0;tr<TRIALS;tr++){
   var r=rng(1000+seed0*7919+tr*104729),win=[0,0,0,0],i,k;
   for(i=0;i<N;i++){
    var t=r()*total,a=0;
    for(k=0;k<4;k++){a+=tickets[k];if(t<a){win[k]++;break;}}}
   var e=0;
   for(k=0;k<4;k++)e+=Math.abs(win[k]/N-tickets[k]/total);
   acc+=e;}
  return acc/TRIALS;}
 var Ns=[100,400,1600,6400],rows=[];
 for(var i=0;i<Ns.length;i++)
  rows.push({draws:Ns[i],meanAbsError:+meanErr(Ns[i],i).toFixed(5)});
 var shrinks=true;
 for(i=1;i<rows.length;i++)if(rows[i].meanAbsError>=rows[i-1].meanAbsError)shrinks=false;
 // each step is 4x the draws; 1/sqrt(N) predicts the error halves
 var ratios=[];
 for(i=1;i<rows.length;i++)
  ratios.push(+(rows[i-1].meanAbsError/rows[i].meanAbsError).toFixed(3));
 var nearTwo=ratios.every(function(x){return x>1.8&&x<2.2;});
 return {tickets:tickets,trialsPerPoint:TRIALS,rows:rows,
  errorShrinks:shrinks,
  quadruplingDrawsHalvesError:nearTwo,
  observedRatios:ratios,
  predictedRatio:2,
  errorAt100:rows[0].meanAbsError,errorAt6400:rows[3].meanAbsError,
  overallShrink:+(rows[0].meanAbsError/rows[3].meanAbsError).toFixed(2),
  fairOnlyInTheLimit:true,
  ok:shrinks&&nearTwo};}

// EDLF -- utilisation 0.75 sat BELOW the rate-monotonic bound of 0.7798, so both
// schedulers met every deadline and the comparison proved nothing. The gap only
// exists between the RM bound and 1.0, so the task set has to live there.
function st_edlf(){
 function util(ts){return ts.reduce(function(a,t){return a+t.c/t.p;},0);}
 function llBound(n){return n*(Math.pow(2,1/n)-1);}
 function simulate(ts,edf,horizon){
  var rem=ts.map(function(){return 0;}),dl=ts.map(function(t){return t.p;});
  var missed=0,t,i;
  for(t=0;t<horizon;t++){
   for(i=0;i<ts.length;i++)if(t%ts[i].p===0){
    if(rem[i]>0)missed++;                 // previous job never finished
    rem[i]+=ts[i].c;dl[i]=t+ts[i].p;}
   var pick=-1;
   for(i=0;i<ts.length;i++){
    if(rem[i]<=0)continue;
    if(pick<0){pick=i;continue;}
    if(edf?(dl[i]<dl[pick]):(ts[i].p<ts[pick].p))pick=i;}
   if(pick>=0)rem[pick]--;}
  return missed;}
 var tasks=[{p:5,c:2},{p:7,c:4}];        // U = 0.400 + 0.571 = 0.971
 var u=util(tasks),bound=llBound(2);
 var H=5*7*40;
 var edfMiss=simulate(tasks,true,H),rmMiss=simulate(tasks,false,H);
 return {tasks:tasks,
  utilisation:+u.toFixed(4),
  edfBound:1,rateMonotonicBound:+bound.toFixed(4),
  aboveRmBound:u>bound,withinEdfBound:u<=1,
  edfDeadlinesMissed:edfMiss,
  rateMonotonicDeadlinesMissed:rmMiss,
  horizon:H,
  bothSchedulersSameWork:true,
  ok:u>bound&&u<=1&&edfMiss===0&&rmMiss>0};}

var T=[['WSTL',st_wstl],['STRV',st_strv],['LOTT',st_lott],['EDLF',st_edlf]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,620));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
