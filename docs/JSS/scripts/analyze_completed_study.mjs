// Completed-study score-table analysis. No inference and no historical snapshot input.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'../../..'), out=path.join(root,'docs/JSS');
const read=p=>fs.readFileSync(path.join(root,p),'utf8'), json=p=>JSON.parse(read(p));
const dir='experiments/pilot/results/analysis/';
function csv(text){const lines=text.trim().split(/\r?\n/),h=lines.shift().split(',');return lines.map(l=>Object.fromEntries(l.split(',').map((v,i)=>[h[i],v])));}
const rows=csv(read(dir+'scores.csv')), saved=json(dir+'summary.json'), selection=json('experiments/pilot/results/pilot.json');
const complete=json(dir+'completeness.json'),receipt=json(dir+'final-verification.json'), controls=json(dir+'controls.json'), quality=json(dir+'quality.json');
const models=['Qwen/Qwen2.5-Coder-7B-Instruct','deepseek-ai/deepseek-coder-6.7b-instruct'];
const variants=['morph','no_forgetting','fixed_reset','stateless_summary'], names=['Full adaptive','Continuous','Fixed reset','Observation-only'];
const short=m=>m.startsWith('Qwen')?'Qwen':'DeepSeek';
const num=x=>Number(x),mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
const sum=a=>a.reduce((x,y)=>x+y,0), bool=x=>x==='True';
const approx=(a,b)=>assert.ok(Math.abs(a-b)<1e-8, a+' != '+b);
assert.equal(rows.length,400);assert.equal(complete.complete,true);assert.equal(complete.missing,0);
assert.equal(receipt.verified_primary_records,400);assert.equal(receipt.verified_control_records,100);
assert.equal(receipt.imported_primary_records,132);assert.equal(receipt.new_receipt_records,268);
assert.equal(selection.selected_ids.length,50);assert.equal(selection.seed,1);
assert.equal(selection.budget,32000);assert.equal(selection.rounds,16);
assert.deepEqual(selection.variants,variants);
assert.equal(selection.protocol_sha256,receipt.protocol_sha256);
assert.equal(new Set(rows.map(x=>[x.model_id,x.variant,x.instance_id,x.seed].join('|'))).size,400);
const groups=[], byKey=new Map();
for(const m of models)for(const [j,v]of variants.entries()){
 const rs=rows.filter(x=>x.model_id===m&&x.variant===v),fn=rs.filter(x=>bool(x.function_eligible));
 assert.equal(rs.length,50);assert.equal(fn.length,48);
 assert.deepEqual(rs.map(x=>x.instance_id).sort(),[...selection.selected_ids].sort());
 for(const r of rs){assert.equal(+r.seed,1);assert.equal(+r.budget,32000);assert.equal(bool(r.eligible),true);approx(+r.tokens,+r.input_tokens + +r.output_tokens);byKey.set([m,v,r.instance_id].join('|'),r);}
 const g={model:m,name:short(m),variant:v,workflow:names[j],n:50,function_n:48,top1:mean(rs.map(x=>+x.top1)),top5:mean(rs.map(x=>+x.top5)),top10:mean(rs.map(x=>+x.top10)),mrr:mean(rs.map(x=>+x.mrr)),function_top1:mean(fn.map(x=>+x.function_top1)),function_mrr:mean(fn.map(x=>+x.function_mrr)),tokens:mean(rs.map(x=>+x.tokens)),output_tokens:mean(rs.map(x=>+x.output_tokens)),seconds:mean(rs.map(x=>+x.end_to_end_seconds)),resets:mean(rs.map(x=>+x.resets)),reset_runs:rs.filter(x=>+x.resets>0).length,total_resets:sum(rs.map(x=>+x.resets)),final_pools:rs.filter(x=>bool(x.has_hypotheses)).length};
 const s=saved.find(x=>x.model===m&&x.variant===v);assert.ok(s);
 for(const k of ['top1','top5','function_top1','tokens','resets'])approx(g[k],s[k]);
 approx(g.seconds,s.end_to_end_seconds);
 if(m.startsWith('deepseek'))assert.equal(g.final_pools,quality.variants[v].with_hypotheses);
 groups.push(g);
}
assert.equal(controls.scores.length,100);
for(const v of ['bm25','graph']){
 const rs=controls.scores.filter(x=>x.variant===v);assert.equal(rs.length,50);
 assert.deepEqual(rs.map(x=>x.instance_id).sort(),[...selection.selected_ids].sort());
 const s=controls.summary.find(x=>x.variant===v);
 for(const k of ['top1','top5','top10','mrr'])approx(mean(rs.map(x=>x[k])),s[k]);
}
const subjects=rows.filter(x=>x.model_id===models[0]&&x.variant==='morph');
const repos=[...new Set(subjects.map(x=>x.repo))].sort();assert.equal(repos.length,12);
const paired=[];
for(const m of models)for(const v of variants.slice(1)){
 let leftOnly=0,rightOnly=0,poolLeftOnly=0,poolRightOnly=0;
 for(const id of selection.selected_ids){
 const l=byKey.get([m,'morph',id].join('|')),r=byKey.get([m,v,id].join('|'));
 leftOnly+=+(+l.top1===1&&+r.top1===0);rightOnly+=+(+l.top1===0&&+r.top1===1);
 poolLeftOnly+=+(bool(l.has_hypotheses)&&!bool(r.has_hypotheses));poolRightOnly+=+(!bool(l.has_hypotheses)&&bool(r.has_hypotheses));
 }
 paired.push({model:m,comparator:v,left_only:leftOnly,right_only:rightOnly,delta_pp:2*(leftOnly-rightOnly),pool_left_only:poolLeftOnly,pool_right_only:poolRightOnly});
}
// The intervals are preserved from the original 2,000-draw analysis, not retested.
const reported=read(dir+'report.md');
for(const p of paired){
 const section=reported.split('## '+p.model)[1]?.split('\n## ')[0];assert.ok(section,'model report block');
 const line=section.split(/\r?\n/).find(x=>x.startsWith('- '+p.comparator+': '));assert.ok(line,'paired report line');
 const values=line.match(/: ([+-]?\d+(?:\.\d+)?) percentage points \[([+-]?\d+(?:\.\d+)?), ([+-]?\d+(?:\.\d+)?)\]/);
 assert.ok(values,'interval source syntax');assert.equal(+values[1],p.delta_pp);
 p.interval=[+values[2],+values[3]];
}
const esc=x=>x.replaceAll('_','\\_'), pct=x=>(100*x).toFixed(0),f=x=>x.toFixed(3),count=(x,n)=>Math.round(x*n)+'/'+n,integer=x=>Math.round(x).toLocaleString('en-US');
function table(caption,label,spec,head,lines){return '\\begin{table}[t]\n\\caption{'+caption+'}\\label{'+label+'}\n\\centering\\small\n\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}'+spec+'@{}}\\toprule\n'+head+'\\\\\\midrule\n'+lines.join('\n')+'\n\\bottomrule\\end{tabular*}\n\\end{table}\n';}
const files={};
files['subjects.tex']=table('Repository composition of the fixed 50-issue sample. Function eligibility is determined separately by nonempty patch-derived targets.','tab:eval-coverage','lrr','Repository & Issues & Function-eligible',repos.map(repo=>esc(repo)+' & '+subjects.filter(x=>x.repo===repo).length+' & '+subjects.filter(x=>x.repo===repo&&bool(x.function_eligible)).length+'\\\\').concat(['\\midrule Total & 50 & 48\\\\']));
files['ranking.tex']=table('Ranking outcomes on all 50 study issues per workflow and model (seed 1). Top-5/10 are percentages; Top-1 cells show exact hits and denominators. Retrieval controls run once per issue and produce no function ranking.','tab:eval-ranking','llrrrrrr','LLM & Workflow & File Top-1 & Top-5 & Top-10 & File MRR & Fn. Top-1 & Fn. MRR',groups.map((g,i)=>(i===4?'\\midrule\n':'')+g.name+' & '+g.workflow+' & '+count(g.top1,50)+' & '+pct(g.top5)+' & '+pct(g.top10)+' & '+f(g.mrr)+' & '+count(g.function_top1,48)+' & '+f(g.function_mrr)+'\\\\').concat(['\\midrule\n\\multicolumn{2}{l}{BM25 (shared)} & 20/50 & 70 & 86 & '+f(controls.summary[0].mrr)+' & -- & --\\\\','\\multicolumn{2}{l}{Graph (shared)} & 20/50 & 70 & 86 & '+f(controls.summary[1].mrr)+' & -- & --\\\\']));
files['paired.tex']=table('Paired file Top-1 contrasts: full adaptive minus comparator. Counts concern target-hit status, not identity of the top-ranked path. Intervals are descriptive repository-cluster intervals from the saved 2,000-draw analysis.','tab:paired','llrrrr','LLM & Comparator & Full only & Comparator only & Difference (pp) & 95\\% interval',paired.map(p=>short(p.model)+' & '+names[variants.indexOf(p.comparator)]+' & '+p.left_only+' & '+p.right_only+' & '+(p.delta_pp>0?'+':'')+p.delta_pp+' & ['+p.interval[0]+', '+p.interval[1]+']\\\\'));
files['process.tex']=table('Reset exposure and final-pool availability. An empty pool returns retrieval file order. A nonempty pool establishes source-valid proposals, not correct causal explanations.','tab:eval-mechanisms','llrrrr','LLM & Workflow & Runs with reset & Total resets & Mean resets & Final pools',groups.map((g,i)=>(i===4?'\\midrule\n':'')+g.name+' & '+g.workflow+' & '+g.reset_runs+'/50 & '+g.total_resets+' & '+g.resets.toFixed(2)+' & '+g.final_pools+'/50\\\\'));
files['cost.tex']=table('Actual mean resources per completed study run. Tokens include input and output; elapsed seconds exclude interrupted/retried attempts. Different model tokenizers limit cross-model token comparisons.','tab:eval-cost','llrrr','LLM & Workflow & Total tokens & Output tokens & Seconds',groups.map((g,i)=>(i===4?'\\midrule\n':'')+g.name+' & '+g.workflow+' & '+integer(g.tokens)+' & '+integer(g.output_tokens)+' & '+g.seconds.toFixed(1)+'\\\\'));
files['funnel.tex']=table('DeepSeek output diagnostics from archived audit counts. Events may exceed case counts; hypothesis events are not distinct final hypotheses or correct explanations.','tab:eval-pilot','lrrrr','Workflow & Accepted responses & Invalid responses & Hypothesis events & Final pools',variants.map((v,i)=>{const q=quality.variants[v];return names[i]+' & '+q.events.agent_response+' & '+q.events.invalid_response+' & '+q.events.hypothesis+' & '+q.with_hypotheses+'/50\\\\';}));
fs.mkdirSync(path.join(out,'generated'),{recursive:true});
for(const [name,tex]of Object.entries(files)){const dest=path.join(out,'generated',name);if(process.argv.includes('--write'))fs.writeFileSync(dest,tex);else assert.equal(fs.readFileSync(dest,'utf8'),tex,'generated table differs '+name);}
const inputs=[dir+'scores.csv',dir+'report.md',dir+'summary.json',dir+'controls.json',dir+'completeness.json',dir+'quality.json',dir+'final-verification.json','experiments/pilot/results/pilot.json'];
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const sourceFiles=[];
function expand(rel){
 sourceFiles.push(rel);
 return read(rel).replace(/\\input\{([^}]+)\}/g,(_,name)=>expand('docs/JSS/'+name+(name.endsWith('.tex')?'':'.tex')));
}
const manuscript=expand('docs/JSS/main.tex'),bibliography=read('docs/JSS/references.bib');
for(const old of ['42.93','46.58','50.36','55.56','63{,}630','99{,}544'])assert.ok(!manuscript.includes(old),'excluded historical result '+old);
const keys=[...new Set([...manuscript.matchAll(/\\cite\w*\{([^}]+)\}/g)].flatMap(x=>x[1].split(',')))];
for(const key of keys)assert.ok(new RegExp('@\\w+\\{'+key.trim()+',').test(bibliography),'missing reference '+key);
const labels=[...manuscript.matchAll(/\\label\{([^}]+)\}/g)].map(x=>x[1]);assert.equal(new Set(labels).size,labels.length,'duplicate labels');
for(const match of manuscript.matchAll(/\\(?:ref|eqref|pageref)\{([^}]+)\}/g))assert.ok(labels.includes(match[1]),'missing label '+match[1]);
const highlights=read('docs/JSS/highlights.txt').trim().split(/\r?\n/);
assert.ok(highlights.length>=3&&highlights.length<=5);
for(const h of highlights)assert.ok(h.replace(/^[-*] /,'').length<=85,'highlight length');
const audit={status:'passed',scope:'Completed 50-issue score-table and generated-table audit only. Does not validate inaccessible raw signatures, original source execution or stored bootstrap intervals.',selection:{issues:50,repositories:12,function_eligible:48,models:2,workflows:4,seed:1},primary_records:400,control_records:100,reused:132,new:268,inputs:inputs.map(p=>({path:p,sha256:sha(p)})),groups,paired,repositories:repos.map(repo=>({repo,issues:subjects.filter(x=>x.repo===repo).length})),generated_tables:Object.keys(files)};
audit.manuscript_files=sourceFiles.map(p=>({path:p,sha256:sha(p)}));
audit.citation_keys=keys.length; audit.highlights=highlights.length;
fs.mkdirSync(path.join(out,'validation'),{recursive:true});fs.writeFileSync(path.join(out,'validation/completed-study-audit.json'),JSON.stringify(audit,null,2)+'\n');
console.log(JSON.stringify({status:'passed',primary:400,controls:100,issues:50,repositories:12,tables:Object.keys(files).length}));

