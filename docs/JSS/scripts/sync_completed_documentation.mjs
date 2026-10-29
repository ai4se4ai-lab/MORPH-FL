import fs from 'node:fs';
let p='README.md',t=fs.readFileSync(p,'utf8');
t=t.replace('The study also includes deterministic BM25/graph controls and restricted Agentless/RGFL localization-stage adaptations. The adaptations are not reproductions of complete upstream systems.','The paper also evaluates deterministic BM25/graph retrieval controls. It does not claim competitiveness against complete external localization systems; earlier component adaptations belong to separate historical experiments.');
const a=t.indexOf('The results measure **unreviewed'),b=t.indexOf('| Model | Workflow |',a);
t=t.slice(0,a)+'The results measure **unreviewed reference-patch file/function proxies**, not adjudicated root causes or repair success. The current paper reports only the fully collected fixed study below; earlier 139/219-issue snapshot results are preserved outside the paper.\\n\\n### Completed two-model study\\n\\nFifty repository-balanced issues from twelve projects, two models, four workflows and seed 1 yield **400 investigations and 100 retrieval-control records**. Every specified key is present. Each model/workflow has 48 function-eligible issues. The study reuses 132 identity-validated Qwen predictions and is not independent confirmation.\\n\\n'+t.slice(b);
t=t.replace('on the pilot.','on these study issues.').replace('on completed pilot cases.','on completed study cases.').replace('See the [pilot report]','See the [study report]');
t=t.replace('The larger five-family study remains deferred in the reported experiment status; planned component, budget and recovery studies are not completed evidence.','Adaptive resets occur in 8/50 Qwen and 29/50 DeepSeek runs without extra file Top-1 hits over continuous context. The paper reports these exact exposure and paired-output analyses; larger experimental tracks are outside its scope.');
const c=t.indexOf('## Artifact integrity and reproduction'),d=t.indexOf('## Paper and documentation',c);
t=t.slice(0,c)+String.raw`## Artifact integrity and reproduction

The [current JSS artifact guide](docs/JSS/README.md) maps the study evidence and release requirements. With Node.js 22+, from the repository root:

~~~bash
node docs/JSS/scripts/analyze_completed_study.mjs
~~~

The analyzer checks all 400 investigation keys and 100 controls, eligibility, aggregate metrics, reset exposure, paired hits/pools and exact reconstruction of all six generated tables. The [completed-study audit](docs/JSS/validation/completed-study-audit.json) records input digests, including the original interval report. Add --write to regenerate the LaTeX table inputs. No model inference or raw-output/signature revalidation occurs; bootstrap intervals are preserved from their saved analysis.

Current paper tables do not use the historical compact snapshot. Its separately documented truncated prediction export remains unresolved; removing those results from the paper does not repair that archive. The earlier manuscript is preserved in [history](docs/JSS/history/main-before-completed-study.tex), and the historical evidence report retains its original status. The historical audit is separate from the passing completed-study audit.

Keep frozen v12 predictions, later corrected development runs and independent confirmation separate. Raw/environment release, a public persistent archive, final declarations and correction validation remain [author actions](docs/JSS/AUTHOR_ACTIONS.md).

`+t.slice(d);
t=t.replace('Restoration, corrected-runtime studies, confirmation and submission details','Current artifact release, corrected-runtime studies, confirmation and submission details');
t=t.replace('[Revision record](docs/JSS/REVISION_PROCESS.md) / [review responses](docs/JSS/reviews/RESPONSE_MATRIX.md)','[Current revision/review responses](docs/JSS/COMPLETED_STUDY_REVISION.md) / [earlier phase record](docs/JSS/REVISION_PROCESS.md)');
t=t.replace('[Evaluation report](docs/EVALUATION_RESULTS_REPORT.md) | Historical snapshot and complete pilot','[Evaluation report](docs/EVALUATION_RESULTS_REPORT.md) | Historical evidence retained separately from current paper scope');
t=t.replace('[Pilot protocol](experiments/pilot/README.md)','[Study collection protocol](experiments/pilot/README.md)');
fs.writeFileSync(p,t.replaceAll('~~~','\x60\x60\x60'));
p='docs/JSS/scripts/verify_evidence.mjs';t=fs.readFileSync(p,'utf8').replace("const manuscript=read('docs/JSS/main.tex');","const manuscript=read('docs/JSS/history/main-before-completed-study.tex');");
t=t.replace("manuscript_sha256:sha('docs/JSS/main.tex')","manuscript_source:'docs/JSS/history/main-before-completed-study.tex',manuscript_sha256:sha('docs/JSS/history/main-before-completed-study.tex')");
fs.writeFileSync(p,t);
p='docs/JSS/REVISION_PROCESS.md';t=fs.readFileSync(p,'utf8');t='> Superseded scope: the current manuscript reports only the complete 50-issue study. See [COMPLETED_STUDY_REVISION.md](COMPLETED_STUDY_REVISION.md). This earlier phase record is preserved, not a description of the current evidence base.\\n\\n'+t;fs.writeFileSync(p,t);
p='docs/JSS/CHANGELOG.md';t=fs.readFileSync(p,'utf8');t='> Latest revision: see [COMPLETED_STUDY_REVISION.md](COMPLETED_STUDY_REVISION.md) for the completed-only evidence base and three new review pairs. The earlier changes below are historical.\\n\\n'+t;fs.writeFileSync(p,t);
p='docs/JSS/SUBMISSION_CHECKLIST.md';t=fs.readFileSync(p,'utf8').replace('- [ ] Restore historical raw prediction export and revalidate/release the frozen artifact.','- [ ] Revalidate/release the complete fixed-study raw artifact and environment. The historical export is outside the current paper.');fs.writeFileSync(p,t);
p='docs/JSS/highlights.txt';t=fs.readFileSync(p,'utf8').replace('Adaptive resets show no demonstrated ranking or token advantage.','Adaptive resets add no file Top-1 hits over continuous context.');fs.writeFileSync(p,t);

