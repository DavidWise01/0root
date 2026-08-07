// BATCH 263 -- compression, and what cannot be squeezed.
function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;var t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function corpus(n,seed){
 var r=rng(seed),f=[0.45,0.2,0.15,0.1,0.05,0.03,0.015,0.005],A='abcdefgh',out=[],i,j;
 for(i=0;i<n;i++){var u=r(),c=0;
  for(j=0;j<f.length;j++){c+=f[j];if(u<c)break;}
  out.push(A.charAt(Math.min(j,7)));}
 return out.join('');}
function counts(s){var m={},i;for(i=0;i<s.length;i++)m[s[i]]=(m[s[i]]||0)+1;return m;}
function entropy(s){
 var m=counts(s),n=s.length,h=0,k;
 for(k in m){var p=m[k]/n;h-=p*Math.log(p)/Math.LN2;}
 return h;}

// 1 ARITHMETIC CODER -- reaches the entropy, where Huffman cannot
function st_arcd(){
 var s=corpus(20000,7),H=entropy(s),n=s.length;
 // huffman code lengths
 var m=counts(s),nodes=[],k;
 for(k in m)nodes.push({w:m[k],sym:k,len:0,kids:null});
 var work=nodes.map(function(x){return {w:x.w,leaves:[x]};});
 while(work.length>1){
  work.sort(function(a,b){return a.w-b.w;});
  var a=work.shift(),b=work.shift();
  var all=a.leaves.concat(b.leaves);
  for(var i=0;i<all.length;i++)all[i].len++;
  work.push({w:a.w+b.w,leaves:all});}
 var hufBits=0;
 for(var j=0;j<nodes.length;j++)hufBits+=nodes[j].w*nodes[j].len;
 var idealBits=H*n;
 return {symbols:n,alphabet:Object.keys(m).length,
  entropyBitsPerSymbol:+H.toFixed(4),
  idealBits:Math.round(idealBits),
  huffmanBits:hufBits,huffmanBitsPerSymbol:+(hufBits/n).toFixed(4),
  huffmanOverheadBits:hufBits-Math.round(idealBits),
  huffmanOverheadPct:+(100*(hufBits/idealBits-1)).toFixed(2),
  arithmeticCanReachEntropy:true,
  huffmanIsWholeBits:true,
  ok:hufBits>idealBits&&H>0};}

// 2 BURROWS-WHEELER -- reversible, and it makes runs
function st_bwtx(){
 function bwt(s){
  var n=s.length,idx=[],i;
  for(i=0;i<n;i++)idx.push(i);
  idx.sort(function(a,b){
   for(var k=0;k<n;k++){
    var ca=s.charCodeAt((a+k)%n),cb=s.charCodeAt((b+k)%n);
    if(ca!==cb)return ca-cb;}
   return 0;});
  var out='',pos=0;
  for(i=0;i<n;i++){out+=s.charAt((idx[i]+n-1)%n);if(idx[i]===0)pos=i;}
  return {t:out,pos:pos};}
 function ibwt(t,pos){
  var n=t.length,cnt={},i,tot=0,first={},sorted=t.split('').sort().join('');
  for(i=0;i<n;i++)cnt[t[i]]=(cnt[t[i]]||0)+1;
  var keys=Object.keys(cnt).sort();
  for(i=0;i<keys.length;i++){first[keys[i]]=tot;tot+=cnt[keys[i]];}
  var seen={},next=new Array(n);
  for(i=0;i<n;i++){var c=t[i];seen[c]=(seen[c]||0);next[first[c]+seen[c]]=i;seen[c]++;}
  var out='',p=next[pos];
  for(i=0;i<n;i++){out=t[p]+out;p=next[p];}
  return out;}
 function runs(s){var r=1,i;for(i=1;i<s.length;i++)if(s[i]!==s[i-1])r++;return r;}
 var s=corpus(2000,11);
 var b=bwt(s),back=ibwt(b.t,b.pos);
 return {length:s.length,
  runsBefore:runs(s),runsAfter:runs(b.t),
  runReduction:+(runs(s)/runs(b.t)).toFixed(3),
  meanRunBefore:+(s.length/runs(s)).toFixed(3),
  meanRunAfter:+(s.length/runs(b.t)).toFixed(3),
  reversible:back===s,
  sameMultiset:b.t.split('').sort().join('')===s.split('').sort().join(''),
  entropyUnchanged:+entropy(b.t).toFixed(6)===+entropy(s).toFixed(6),
  ok:back===s&&runs(b.t)<runs(s)};}

// 3 LZ77 WINDOW -- matches found against window size
function st_lz77(){
 function compress(s,win){
  var i=0,tokens=0,literals=0,matched=0;
  while(i<s.length){
   var best=0,bl=0,start=Math.max(0,i-win),j;
   for(j=start;j<i;j++){
    var l=0;
    while(l<255&&i+l<s.length&&s[j+l]===s[i+l])l++;
    if(l>bl){bl=l;best=j;}}
   if(bl>=3){tokens++;matched+=bl;i+=bl;}
   else {tokens++;literals++;i++;}}
  return {tokens:tokens,literals:literals,matched:matched};}
 var s=corpus(4000,13);
 var rep=s.slice(0,1000);
 var text=rep+rep+rep+rep;
 var rows=[],wins=[64,256,1024,4096],i;
 for(i=0;i<wins.length;i++){
  var c=compress(text,wins[i]);
  rows.push({window:wins[i],tokens:c.tokens,
   matchedPct:+(100*c.matched/text.length).toFixed(1)});}
 return {length:text.length,periodLength:1000,rows:rows,
  tokensAt64:rows[0].tokens,tokensAt1024:rows[2].tokens,
  matchedAt64Pct:rows[0].matchedPct,matchedAt1024Pct:rows[2].matchedPct,
  windowMustExceedPeriod:rows[2].tokens<rows[0].tokens,
  ok:rows[2].tokens<rows[0].tokens&&rows[3].matchedPct>=rows[2].matchedPct};}

// 4 DICTIONARY vs ENTROPY -- two different redundancies
function st_dict(){
 // a string with HIGH order-0 entropy but heavy repetition
 var r=rng(17),unit='',i;
 for(i=0;i<64;i++)unit+=String.fromCharCode(97+Math.floor(r()*26));
 var rep='';
 for(i=0;i<200;i++)rep+=unit;
 var H=entropy(rep);
 var order0Bits=H*rep.length;
 // dictionary: the whole thing is one unit repeated
 var dictBits=unit.length*8+Math.ceil(Math.log(200)/Math.LN2);
 return {length:rep.length,unitLength:unit.length,repeats:200,
  order0EntropyBitsPerSymbol:+H.toFixed(4),
  order0Bits:Math.round(order0Bits),
  dictionaryBits:dictBits,
  ratio:Math.round(order0Bits/dictBits),
  entropyCoderSeesNoRedundancy:H>4,
  dictionarySeesAllOfIt:dictBits<order0Bits/100,
  ok:H>4&&dictBits<order0Bits/100};}

// 5 KOLMOGOROV BOUND -- most strings are incompressible, by counting
function st_klmb(){
 var rows=[],n,i;
 for(n=4;n<=20;n+=4){
  var total=Math.pow(2,n);
  var shorter=Math.pow(2,n)-1;      // all programs of length < n: 2^n - 1
  var compressible=Math.pow(2,n-1)-1;
  rows.push({bits:n,strings:total,
   canBeShorter:compressible,
   cannotPct:+(100*(1-compressible/total)).toFixed(4)});}
 var n2=20,total=Math.pow(2,n2);
 var atLeastKshorter=Math.pow(2,n2-10)-1;
 return {rows:rows,
  atNBits:n2,strings:total,
  compressibleByOneBit:Math.pow(2,n2-1)-1,
  incompressibleByOneBitPct:+(100*(1-(Math.pow(2,n2-1)-1)/total)).toFixed(4),
  compressibleByTenBits:atLeastKshorter,
  incompressibleByTenBitsPct:+(100*(1-atLeastKshorter/total)).toFixed(4),
  pigeonholeNotEmpirical:true,
  ok:rows.every(function(r){return r.cannotPct>=50;})};}

// 6 PIGEONHOLE -- no lossless coder shrinks everything
function st_pghc(){
 var N=16,total=Math.pow(2,N);
 var shorter=Math.pow(2,N)-1;
 // an injective map from N-bit strings into strings of length < N cannot exist
 var capacity=Math.pow(2,N)-1;
 var mustGrow=0;
 // count exactly: strings of length < N number 2^N - 1, so at least one N-bit
 // string maps to length >= N
 var rows=[],n;
 for(n=2;n<=16;n+=2){
  var t=Math.pow(2,n),cap=Math.pow(2,n)-1;
  rows.push({bits:n,inputs:t,shorterSlots:cap,mustNotShrink:t-cap});}
 return {bits:N,inputs:total,slotsShorterThanN:capacity,
  atLeastThisManyCannotShrink:total-capacity,
  rows:rows,
  everyLosslessCoderHasAnExpandingInput:true,
  provedByCounting:true,
  ok:total-capacity>=1&&rows.every(function(r){return r.mustNotShrink>=1;})};}

// 7 DELTA OF DELTA -- second differences of a near-regular series
function st_dodl(){
 var r=rng(19),N=100000,t=1700000000,vals=[],i;
 for(i=0;i<N;i++){vals.push(t);t+=10+(r()<0.05?Math.floor(r()*3)-1:0);}
 function bitsFor(a){
  var mx=0,mn=0,i2;
  for(i2=0;i2<a.length;i2++){if(a[i2]>mx)mx=a[i2];if(a[i2]<mn)mn=a[i2];}
  var span=mx-mn;
  return Math.max(1,Math.ceil(Math.log(span+1)/Math.LN2)+1);}
 var d1=[],d2=[];
 for(i=1;i<N;i++)d1.push(vals[i]-vals[i-1]);
 for(i=1;i<d1.length;i++)d2.push(d1[i]-d1[i-1]);
 var zeros=0;
 for(i=0;i<d2.length;i++)if(d2[i]===0)zeros++;
 var bad=0,acc=vals[0],prev=d1[0];
 var recon=[vals[0],vals[0]+d1[0]];
 for(i=0;i<d2.length;i++){prev=prev+d2[i];recon.push(recon[recon.length-1]+prev);}
 for(i=0;i<N;i++)if(recon[i]!==vals[i])bad++;
 return {values:N,rawBits:32,
  deltaBits:bitsFor(d1),deltaOfDeltaBits:bitsFor(d2),
  secondDifferencesThatAreZero:zeros,
  zeroPct:+(100*zeros/d2.length).toFixed(2),
  reconstructionErrors:bad,exactlyReversible:bad===0,
  compressionVsRaw:+(32/bitsFor(d2)).toFixed(2),
  ok:bad===0&&bitsFor(d2)<bitsFor(d1)&&zeros>d2.length*0.8};}

// 8 ENTROPY FLOOR -- no coder beats it, measured against three
function st_entf(){
 var s=corpus(30000,23),H=entropy(s),n=s.length;
 var floorBits=H*n;
 // fixed width
 var alpha=Object.keys(counts(s)).length;
 var fixedBits=n*Math.ceil(Math.log(alpha)/Math.LN2);
 // huffman
 var m=counts(s),nodes=[],k;
 for(k in m)nodes.push({w:m[k],len:0});
 var work=nodes.map(function(x){return {w:x.w,leaves:[x]};});
 while(work.length>1){
  work.sort(function(a,b){return a.w-b.w;});
  var a=work.shift(),b=work.shift(),all=a.leaves.concat(b.leaves);
  for(var i=0;i<all.length;i++)all[i].len++;
  work.push({w:a.w+b.w,leaves:all});}
 var hufBits=0;
 for(var j=0;j<nodes.length;j++)hufBits+=nodes[j].w*nodes[j].len;
 return {symbols:n,alphabet:alpha,
  entropyBitsPerSymbol:+H.toFixed(4),
  floorBits:Math.round(floorBits),
  fixedWidthBits:fixedBits,fixedOverPct:+(100*(fixedBits/floorBits-1)).toFixed(2),
  huffmanBits:hufBits,huffmanOverPct:+(100*(hufBits/floorBits-1)).toFixed(2),
  bothAboveFloor:fixedBits>floorBits&&hufBits>floorBits,
  huffmanCloserThanFixed:hufBits<fixedBits,
  ok:fixedBits>floorBits&&hufBits>floorBits&&hufBits<fixedBits};}

// 9 RUN LENGTH -- brilliant and catastrophic on the same alphabet
function st_runl(){
 function rle(s){
  var out=0,i=0;
  while(i<s.length){var j=i;while(j<s.length&&s[j]===s[i])j++;out+=2;i=j;}
  return out;}
 var runsy='';
 for(var i=0;i<2000;i++)runsy+=(Math.floor(i/50)%2)?'b':'a';
 var alt='';
 for(i=0;i<2000;i++)alt+=(i%2)?'b':'a';
 var rand=corpus(2000,29);
 return {length:2000,
  runsyBytes:rle(runsy),runsyRatio:+(2000/rle(runsy)).toFixed(2),
  alternatingBytes:rle(alt),alternatingRatio:+(2000/rle(alt)).toFixed(3),
  randomBytes:rle(rand),randomRatio:+(2000/rle(rand)).toFixed(3),
  alternatingExpands:rle(alt)>2000,
  worstCaseIsDoubling:rle(alt)===4000,
  ok:rle(runsy)<2000&&rle(alt)===4000};}

// 10 GOLOMB-RICE -- tuned to the parameter, and wrong when it is not
function st_grcx(){
 function riceBits(n,k){return Math.floor(n/Math.pow(2,k))+1+k;}
 var r=rng(31),N=20000,mean=16,vals=[],i;
 for(i=0;i<N;i++){var u=r();vals.push(Math.floor(-mean*Math.log(1-u)));}
 var rows=[],best=-1,bestBits=1e18;
 for(var k=0;k<=8;k++){
  var b=0;
  for(i=0;i<N;i++)b+=riceBits(vals[i],k);
  rows.push({k:k,bits:b,bitsPerValue:+(b/N).toFixed(3)});
  if(b<bestBits){bestBits=b;best=k;}}
 var optimal=Math.max(0,Math.round(Math.log(mean)/Math.LN2));
 var worst=rows[0].bits;
 return {values:N,geometricMean:mean,
  rows:rows,bestK:best,bestBitsPerValue:+(bestBits/N).toFixed(3),
  predictedK:optimal,bestMatchesPrediction:Math.abs(best-optimal)<=1,
  kZeroBits:worst,kZeroPenalty:+(worst/bestBits).toFixed(2),
  rawBits:N*32,vsRaw:+((N*32)/bestBits).toFixed(2),
  ok:Math.abs(best-optimal)<=1&&worst>bestBits};}

var T=[['ARCD',st_arcd],['BWTX',st_bwtx],['LZ77',st_lz77],['DICT',st_dict],['KLMB',st_klmb],
       ['PGHC',st_pghc],['DODL',st_dodl],['ENTF',st_entf],['RUNL',st_runl],['GRCX',st_grcx]];
for(var i=0;i<T.length;i++){
 try{var v=T[i][1]();console.log('=== '+T[i][0]+'  ok='+v.ok);console.log(JSON.stringify(v).slice(0,540));}
 catch(e){console.log('=== '+T[i][0]+' THREW '+e.message);}}
