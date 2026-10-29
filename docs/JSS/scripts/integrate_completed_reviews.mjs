import fs from 'node:fs';
let p='docs/JSS/scripts/analyze_completed_study.mjs',t=fs.readFileSync(p,'utf8');
const a=t.indexOf('const intervals='),b=t.indexOf('const esc=',a);
if(a<0||b<0)throw Error('interval boundary');
t=t.slice(0,a)+String.raw`for(const p of paired){
 const section=reported.split('## '+p.model)[1]?.split('\n## ')[0];assert.ok(section,'model report block');
 const line=section.split(/\r?\n/).find(x=>x.startsWith('- '+p.comparator+': '));assert.ok(line,'paired report line');
 const values=line.match(/: ([+-]?\d+(?:\.\d+)?) percentage points \[([+-]?\d+(?:\.\d+)?), ([+-]?\d+(?:\.\d+)?)\]/);
 assert.ok(values,'interval source syntax');assert.equal(+values[1],p.delta_pp);
 p.interval=[+values[2],+values[3]];
}
`+t.slice(b);
t=t.replace("dir+'scores.csv',dir+'summary.json'","dir+'scores.csv',dir+'report.md',dir+'summary.json'");
fs.writeFileSync(p,t);
p='docs/JSS/main.tex';t=fs.readFileSync(p,'utf8').replace('discusses provisional evidence','discusses configuration-level evidence');
t=t.replace('Table~\\ref{tab:variants} defines all evaluated configurations. Additional implemented controls such as \\code{context_only}, \\code{single_hypothesis}, \\code{no_mde} and \\code{independent_agents} are outside the reported experiments; their presence in the library is not performance evidence.','Table~\\ref{tab:variants} defines the evaluated configurations. Additional library controls are outside this article, including \\artifactpath{context_only}, \\artifactpath{single_hypothesis}, \\artifactpath{no_mde} and \\artifactpath{independent_agents}. Their implementation is not performance evidence.');
fs.writeFileSync(p,t);
p='docs/JSS/sections/reproduction.tex';t=fs.readFileSync(p,'utf8').replaceAll('\\code{scores.csv}','\\artifactpath{scores.csv}').replaceAll('\\code{summary.json}','\\artifactpath{summary.json}').replaceAll('\\code{controls.json}','\\artifactpath{controls.json}').replaceAll('\\code{quality.json}','\\artifactpath{quality.json}').replaceAll('\\code{completeness.json}','\\artifactpath{completeness.json}').replaceAll('\\code{final-verification.json}','\\artifactpath{final-verification.json}');fs.writeFileSync(p,t);

