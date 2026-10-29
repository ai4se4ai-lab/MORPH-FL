import fs from 'node:fs';
let p='docs/JSS/main.tex',t=fs.readFileSync(p,'utf8');
const changes=[
['\\subsection{RQ2: Contribution of Models, Resets, and Retention}','\\subsection{RQ2: Reset Exposure and Context-Configuration Contrasts}'],
['shows that the differences lie almost entirely at rank one.','shows that the largest context-policy differences concern Top-1, while Top-10 rates are close.'],
['and they rarely change the top file: in the Qwen pilot,','and changes to whether a patched file appears first are limited in the Qwen pilot:'],
['none of the context-policy contrasts favors \\tool{}.','none of the context-policy contrasts favors \\tool{} on file Top-1.'],
['fixed reset and continuous context have the same aggregate file metrics','fixed reset and continuous context have identical aggregate file Top-1, Top-5 and Top-10 rates'],
['The identical aggregate file metrics of continuous context and fixed-interval reset','The identical aggregate file Top-1, Top-5 and Top-10 rates of continuous context and fixed-interval reset'],
['and has the highest accuracy.','and has the highest observed file Top-1.'],
['The most accurate workflow, the observation-only view,','The workflow with the highest observed file Top-1, the observation-only view,'],
['The observation-only view is the most expensive in the pilot.','The observation-only view has the highest observed mean completed-case tokens and elapsed time in the pilot.'],
['This follows from Eq.~\\eqref{eq:reset}: with fewer than two live hypotheses, diversity is zero, so three rounds without a new observation satisfy the stall condition even when the investigation has produced nothing to circle around.','This is permitted by Eq.~\\eqref{eq:reset}: with fewer than two live hypotheses, diversity is zero, so three rounds without a new observation satisfy the stagnation part, subject to the remaining gates. These proxies can trigger even if no explanation was developed.'],
['only the report and the recorded observations, with no hypotheses and no dialogue, and never resets (Section~\\ref{sec:variants}).','the report and recorded observations in its memory view, alongside common instructions and source excerpts, with no hypotheses or dialogue, and never resets (Section~\\ref{sec:variants}).'],
];
for(const [a,b]of changes){if(!t.includes(a))throw Error('missing '+a);t=t.replace(a,b);}
const note=String.raw`
\paragraph{Local artifact integrity.}
The historical tables reproduce the saved report and scored aggregates. During this revision, the local compact \code{predictions.jsonl} was found truncated mid-record: its SHA-256 does not match the report's recorded digest. The other five compact snapshot files match their recorded digests. Primary point estimates could therefore not be independently rebuilt from this local prediction copy. Pilot point estimates are independently checked against its complete per-case score table; this does not revalidate inaccessible raw audit archives. \authoraction{restore the exact historical prediction export, verify its recorded SHA-256 and rebuild the primary tables before submission.}
`;
t=t.replace('\\subsection{RQ1: Localization Effectiveness}',note+'\n\\subsection{RQ1: Localization Effectiveness}');
t=t.replace('rebuilds the snapshot metrics and figures','rebuilds the snapshot metrics and figures once the truncated prediction export has been restored');
t=t.replace('The JSS Node audit independently recomputes point estimates from frozen rankings and labels without model inference.','The JSS Node audit checks snapshot hashes, reports the truncated export as a failed integrity check, verifies table bindings against saved primary aggregates, and independently recomputes pilot point estimates from per-case scores without model inference.');
fs.writeFileSync(p,t);
p='docs/JSS/scripts/verify_evidence.mjs';t=fs.readFileSync(p,'utf8');
t=t.replace("assert.equal(actual,expected,name+' frozen bytes'); checks.push({file:prefix+'snapshot/'+name,sha256:actual});","checks.push({file:prefix+'snapshot/'+name,sha256:actual,expected_sha256:expected,match:actual===expected});");
t=t.replace("const rows=jsonl(prefix+'snapshot/predictions.jsonl');","const completePrimary=checks.every(x=>x.match);\nconst rawPrimary=read(prefix+'snapshot/predictions.jsonl');\nconst lines=rawPrimary.split(/\\r?\\n/);\nconst rows=[];let malformed=0;for(const line of lines){if(!line.trim())continue;try{rows.push(JSON.parse(line));}catch{malformed++;}}\nconst primaryIntegrity={complete:completePrimary,parseable_records:rows.length,malformed_records:malformed,expected_records:7291,ends_with_newline:rawPrimary.endsWith('\\n')};");
t=t.replace('for(const [bench,all] of Object.entries(membership)){','if(completePrimary) for(const [bench,all] of Object.entries(membership)){');
t=t.replace("const audit={status:'passed',","const audit={status:completePrimary?'passed':'partial: historical prediction export failed integrity; pilot point-estimate checks passed',primary_integrity:primaryIntegrity,");
t=t.replace("scope:'Independent point-estimate recomputation and frozen byte integrity; no new model inference, no bootstrap recomputation, no fresh HPC trace/signature verification.'","scope:'Primary hash audit and saved-aggregate table binding; independent pilot point-estimate recomputation. Truncated primary export prevents independent historical rebuilding. No new model inference, bootstrap recomputation or fresh HPC trace/signature verification.'");
t=t.replace('primary:recomputed,','primary:recomputed.length?recomputed:summary.map(x=>({...x,verification:\"saved aggregate only; raw export incomplete\"})),');
t=t.replace("const manuscript=read('docs/JSS/main.tex');","const manuscript=read('docs/JSS/main.tex');\nfor(const row of summary){if(['morph','stateless_summary'].includes(row.variant))assert.ok(manuscript.includes((100*Number(row.files_top1)).toFixed(2)), 'primary table binding '+row.benchmark+'/'+row.variant);}");
fs.writeFileSync(p,t);console.log('Integrated empirical review and artifact limitation.');

