const fs=require('fs');const h=fs.readFileSync('index.html','utf8');
function grab(n){const i=h.indexOf('function '+n+'(');let d=0,j=h.indexOf('{',i);for(let k=j;;k++){if(h[k]=='{')d++;else if(h[k]=='}'){d--;if(!d)return h.slice(i,k+1);}}}
eval(grab('fnv1a_64').replace('function fnv1a_64','globalThis.fnv1a_64=function'));
const fp=fs.readFileSync(process.argv[2]);let p=0;const n=fp[p++];const sets=[];
for(let g=0;g<n;g++){const idx=fp[p++],c=fp[p++];const refs=[];for(let r=0;r<c;r++){refs.push({a:fp.readUInt16LE(p),h:fp.readBigUInt64LE(p+2)});p+=10;}sets.push({idx,refs});}
const D='C:/Users/beach/Downloads/';
for(const f of process.argv.slice(3)){const v=fs.readFileSync(f);
 const out=[];for(const s of sets){let ok=0;for(const r of s.refs){if(BigInt(fnv1a_64(v,r.a*2,32))===r.h)ok++;}if(ok)out.push(`${s.idx}:${ok}/${s.refs.length}${ok===s.refs.length?'*':''}`);}
 console.log(f.split('/').pop(),' -> ',out.join('  '));}
const s34=sets.find(s=>s.idx===34),s44=sets.find(s=>s.idx===44);
for(const s of [s34,s44])if(s)console.log('fp',s.idx,s.refs.map(r=>'$'+r.a.toString(16)).join(' '));
console.log('Reihenfolge in Datei:',sets.map(s=>s.idx).join(','));
