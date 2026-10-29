// Read-only verification of frozen evidence; writes only this revision's audit.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const repo=path.resolve(import.meta.dirname,'../../..');
const read=p=>fs.readFileSync(path.join(repo,p),'utf8');
const json=p=>JSON.parse(read(p));
const jsonl=p=>read(p).trim().split(/\r?\n/).map(JSON.parse);
function csv(p){
 const lines=read(p).trim().split(/\r?\n/);
 const split=line=>{const cols=[];let s='',q=false;for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'){if(q&&line[i+1]==='"'){s+='"';i++;}else q=!q;}else if(c===','&&!q){cols.push(s);s='';}else s+=c;}cols.push(s);return cols;};
 const head=split(lines.shift()); return lines.map(l=>Object.fromEntries(split(l).map((v,i)=>[head[i],v])));
}
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(repo,p))).digest('hex');
const approx=(a,b,name)=>assert.ok(Math.abs(a-b)<1e-8, name+': '+a+' != '+b);
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const variants=['morph','no_forgetting','fixed_reset','stateless_summary','agentless_adapted','rgfl_adapted','bm25','graph'];
const prefix='docs/evaluation_assets/';
const frozen={
 'labels.jsonl':'6f3fbc58060cf91d3e4432f56570e7f972e0dd89b9f8ce324c5cce2db01c2434',
 'manifest.json':'5804bc400edab84687bd48e62419c681cc0c74c1d615203bd92a41b0d1156e38',
 'membership.json':'99aaf611ed2de5aa0b3d978cc0fcbdddd341ad3ca3613aa42757a66c55ca09ad',
 'predictions.jsonl':'cc5945f2c2c98911344dee6e9145c2f216f35c74f8cc7a953ae18dcf6983a325',
 'snapshot.json':'2fabea19a841b97f302ef1497a53d83a6290f8bd16f60185beb582b87d9b9986',
 'tracker.json':'50a887307578607e53a5b18ae42775352f2d5775e4d2ba50a9948cc6893e7481'
};
const checks=[];
for(const [name,expected] of Object.entries(frozen)){const actual=sha(prefix+'snapshot/'+name);checks.push({file:prefix+'snapshot/'+name,sha256:actual,expected_sha256:expected,match:actual===expected});}
const completePrimary=checks.every(x=>x.match);
const rawPrimary=read(prefix+'snapshot/predictions.jsonl');
const lines=rawPrimary.split(/\r?\n/);
const rows=[];let malformed=0;for(const line of lines){if(!line.trim())continue;try{rows.push(JSON.parse(line));}catch{malformed++;}}
const primaryIntegrity={complete:completePrimary,parseable_records:rows.length,malformed_records:malformed,expected_records:7291,ends_with_newline:rawPrimary.endsWith('\n')};
const labels=new Map(jsonl(prefix+'snapshot/labels.jsonl').map(x=>[x.instance_id,x]));
const membership=json(prefix+'snapshot/membership.json');
const cohorts=json(prefix+'cohorts.json');
const index=new Map();
for(const r of rows){
 const key=[r.track,r.instance_id,r.variant,r.seed].join('|');
 assert.ok(!index.has(key),'duplicate prediction '+key);index.set(key,r);
 assert.equal(r.revision,labels.get(r.instance_id).revision,'source revision');
 if(r.track!=='retrieval'){assert.equal(r.model_id,'Qwen/Qwen2.5-Coder-7B-Instruct');assert.equal(r.model_revision,'c03e6d358207e414f1eca0bb1891e29f1db0e242');}
}
const seeds=v=>['bm25','graph'].includes(v)?[1]:[1,2,3];
const get=(id,v)=>seeds(v).map(s=>index.get([seeds(v).length===1?'retrieval':'main',id,v,s].join('|')));
const acc=(r,level,k)=>{const ranking=[...new Set((level==='files'?r.ranking:r.function_ranking)||[])];const targets=labels.get(r.instance_id)[level];return +ranking.slice(0,k).some(p=>targets.includes(p));};
const mrr=(r,level)=>{const rank=[...new Set((level==='files'?r.ranking:r.function_ranking)||[])];const gold=labels.get(r.instance_id)[level];const i=rank.findIndex(p=>gold.includes(p));return i<0?0:1/(i+1);};
const summary=csv(prefix+'summary.csv');
const recomputed=[];
if(completePrimary) for(const [bench,all] of Object.entries(membership)){
 const ids=all.filter(id=>variants.every(v=>get(id,v).every(Boolean)));
 assert.deepEqual([...ids].sort(),[...cohorts[bench].common].sort(),'complete cohort '+bench);
 for(const v of variants){
  const file=ids.filter(id=>labels.get(id).files.length), fn=ids.filter(id=>labels.get(id).functions.length);
  const issueMetric=(eligible,level,f)=>mean(eligible.map(id=>mean(get(id,v).map(r=>f(r,level)))));
  const out={benchmark:bench,variant:v,n_common:ids.length,n_file:file.length,n_function:fn.length};
  for(const [level,eligible,name] of [['files',file,'files'],['functions',fn,'functions']]){
   for(const k of [1,5,10])out[name+'_top'+k]=issueMetric(eligible,level,(r,l)=>acc(r,l,k));
   out[name+'_mrr']=issueMetric(eligible,level,mrr);
  }
  out.tokens_mean=mean(file.map(id=>mean(get(id,v).map(r=>(r.input_tokens||0)+(r.output_tokens||0)))));
  out.resets_mean=mean(file.map(id=>mean(get(id,v).map(r=>r.resets||0))));
  const saved=summary.find(r=>r.benchmark===bench&&r.variant===v);assert.ok(saved);
  for(const [k,val] of Object.entries(out))if(typeof val==='number' && !(v==='bm25'||v==='graph') || typeof val==='number'&&!k.startsWith('functions_')){if(saved[k]!==undefined && saved[k]!=='')approx(val,Number(saved[k]),bench+'/'+v+'/'+k);}
  recomputed.push(out);
 }
}
const pilotDir='experiments/pilot/results/analysis/';
const scores=csv(pilotDir+'scores.csv');
assert.equal(scores.length,400);assert.equal(new Set(scores.map(x=>[x.model_id,x.variant,x.instance_id,x.seed].join('|'))).size,400);
const pilotSummary=json(pilotDir+'summary.json');
const pilot=[];
for(const s of pilotSummary){
 const r=scores.filter(x=>x.model_id===s.model&&x.variant===s.variant);
 assert.equal(r.length,50);assert.equal(new Set(r.map(x=>x.instance_id)).size,50);
 const fn=r.filter(x=>x.function_eligible==='True');assert.equal(fn.length,48);
 const out={model:s.model,variant:s.variant,files:r.length,functions:fn.length};
 for(const [key,field,subset] of [['top1','top1',r],['top5','top5',r],['function_top1','function_top1',fn],['tokens','tokens',r],['end_to_end_seconds','end_to_end_seconds',r],['resets','resets',r]]){out[key]=mean(subset.map(x=>+x[field]));approx(out[key],s[key],'pilot/'+s.model+'/'+s.variant+'/'+key);}
 out.final_nonempty=r.filter(x=>x.has_hypotheses==='True').length;pilot.push(out);
}
const completion=json(pilotDir+'completeness.json');
assert.equal(completion.complete,true);assert.equal(completion.missing,0);assert.equal(completion.observed,400);
const verification=json(pilotDir+'final-verification.json');
assert.equal(verification.verified_primary_records,400);assert.equal(verification.verified_control_records,100);
const quality=json(pilotDir+'quality.json');
for(const p of pilot.filter(x=>x.model.startsWith('deepseek')))assert.equal(p.final_nonempty,quality.variants[p.variant].with_hypotheses);
const control=json(pilotDir+'controls.json');
assert.equal(control.scores.length,100);
for(const s of control.summary){const rows=control.scores.filter(x=>x.variant===s.variant);assert.equal(rows.length,50);for(const k of ['top1','top5','top10'])approx(mean(rows.map(x=>x[k])),s[k],'control '+k);}
const manuscript=read('docs/JSS/history/main-before-completed-study.tex');
for(const row of summary){if(['morph','stateless_summary'].includes(row.variant))assert.ok(manuscript.includes((100*Number(row.files_top1)).toFixed(2)), 'primary table binding '+row.benchmark+'/'+row.variant);}
// Verify every numerical cell in the main ranking table against saved aggregates.
const rankingBlock=manuscript.slice(manuscript.indexOf('\\label{tab:eval-ranking}'),manuscript.indexOf('\\end{tabular}',manuscript.indexOf('\\label{tab:eval-ranking}')));
const names={morph:'\\tool{}',no_forgetting:'Continuous context',fixed_reset:'Fixed-interval reset',stateless_summary:'Observation-only view',agentless_adapted:'Agentless adaptation',rgfl_adapted:'RGFL adaptation',bm25:'BM25',graph:'Graph retrieval'};
for(const v of variants){
 const line=rankingBlock.split(/\r?\n/).find(l=>l.startsWith(names[v]+' &'));assert.ok(line,'ranking table row '+v);
 const actual=(line.slice(line.indexOf('&')).match(/\d+(?:\.\d+)?/g)||[]).map(Number);
 const expected=[];
 for(const bench of ['SWE-bench_Lite','SWE-bench_Verified']){
  const r=summary.find(r=>r.benchmark===bench&&r.variant===v);
  expected.push(...['files_top1','files_top5','files_top10'].map(k=>Number((100*Number(r[k])).toFixed(2))),Number(Number(r.files_mrr).toFixed(3)));
  if(!['bm25','graph'].includes(v))expected.push(Number((100*Number(r.functions_top1)).toFixed(2)),Number(Number(r.functions_mrr).toFixed(3)));
 }
 assert.deepEqual(actual,expected,'all ranking cells '+v);
}
const bib=read('docs/JSS/references.bib');
const citeKeys=[...manuscript.matchAll(/\\cite\w*\{([^}]+)\}/g)].flatMap(x=>x[1].split(','));
for(const k of citeKeys)assert.ok(new RegExp('@\\w+\\{'+k.trim()+',').test(bib),'missing citation '+k);
const highlights=read('docs/JSS/highlights.txt').trim().split(/\r?\n/).filter(Boolean);
assert.ok(highlights.length>=3&&highlights.length<=5);
for(const h of highlights)assert.ok(h.replace(/^[-*] /,'').length<=85,'highlight too long');
const audit={status:completePrimary?'passed':'partial: historical prediction export failed integrity; pilot point-estimate checks passed',primary_integrity:primaryIntegrity,created_utc:new Date().toISOString(),scope:'Primary hash audit and saved-aggregate table binding; independent pilot point-estimate recomputation. Truncated primary export prevents independent historical rebuilding. No new model inference, bootstrap recomputation or fresh HPC trace/signature verification.',frozen_files:checks,primary_records:rows.length,primary:recomputed.length?recomputed:summary.map(x=>({...x,verification:"saved aggregate only; raw export incomplete"})),pilot_records:scores.length,pilot,controls:control.summary,citations:new Set(citeKeys).size,highlights:highlights.map(x=>({text:x,length:x.replace(/^[-*] /,'').length})),manuscript_source:'docs/JSS/history/main-before-completed-study.tex',manuscript_sha256:sha('docs/JSS/history/main-before-completed-study.tex'),bibliography_sha256:sha('docs/JSS/references.bib')};
fs.mkdirSync(path.join(repo,'docs/JSS/validation'),{recursive:true});
fs.writeFileSync(path.join(repo,'docs/JSS/validation/evidence-audit.json'),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify({status:audit.status,primary_records:rows.length,primary_rows:recomputed.length,primary_ranking_rows_bound:variants.length,pilot_records:scores.length,citations:audit.citations,highlights:highlights.length}));
process.exitCode=completePrimary?0:2;

