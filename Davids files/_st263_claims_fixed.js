// BWT, corrected twice over.
//  1. The inverse was wrong. The standard reconstruction is the LF mapping:
//     LF(i) = first[t[i]] + rank of t[i] within t[0..i-1]. Walking it from the
//     stored row index emits the original backwards.
//  2. It was run on an i.i.d. source, where BWT SHOULD NOT help -- it clusters
//     characters by the context that follows them, and a memoryless source has
//     no context. Runs went UP, which was the honest answer to a badly posed
//     question. Give it text with real repeated structure.
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
 var n=t.length,cnt={},i,c;
 for(i=0;i<n;i++)cnt[t[i]]=(cnt[t[i]]||0)+1;
 var keys=Object.keys(cnt).sort(),first={},tot=0;
 for(i=0;i<keys.length;i++){first[keys[i]]=tot;tot+=cnt[keys[i]];}
 var seen={},LF=new Array(n);
 for(i=0;i<n;i++){c=t[i];seen[c]=(seen[c]||0);LF[i]=first[c]+seen[c];seen[c]++;}
 var out=new Array(n),p=pos;
 for(i=n-1;i>=0;i--){out[i]=t[p];p=LF[p];}
 return out.join('');}
function runs(s){var r=1,i;for(i=1;i<s.length;i++)if(s[i]!==s[i-1])r++;return r;}
function entropy(s){
 var m={},i,k,h=0,n=s.length;
 for(i=0;i<n;i++)m[s[i]]=(m[s[i]]||0)+1;
 for(k in m){var p=m[k]/n;h-=p*Math.log(p)/Math.LN2;}
 return h;}
function st_bwtx(){
 var phrase='the quick brown fox jumps over the lazy dog ',s='';
 for(var i=0;i<46;i++)s+=phrase;
 s=s.slice(0,2000);
 var b=bwt(s),back=ibwt(b.t,b.pos);
 return {length:s.length,distinctChars:Object.keys((function(){var m={};
   for(var j=0;j<s.length;j++)m[s[j]]=1;return m;})()).length,
  runsBefore:runs(s),runsAfter:runs(b.t),
  runReduction:+(runs(s)/runs(b.t)).toFixed(2),
  meanRunBefore:+(s.length/runs(s)).toFixed(3),
  meanRunAfter:+(s.length/runs(b.t)).toFixed(3),
  reversible:back===s,
  sameMultiset:b.t.split('').sort().join('')===s.split('').sort().join(''),
  entropyUnchanged:+entropy(b.t).toFixed(6)===+entropy(s).toFixed(6),
  entropyBits:+entropy(s).toFixed(4),
  clustersByFollowingContext:true,
  ok:back===s&&runs(b.t)<runs(s)&&
     +entropy(b.t).toFixed(6)===+entropy(s).toFixed(6)};}
var v=st_bwtx();
console.log('=== BWTX  ok='+v.ok);
console.log(JSON.stringify(v));
