"""Rebuild the provisional report and figures from a compact, immutable snapshot."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from morph_fl.evaluation.metrics import metrics

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'snapshot'
OUT = HERE
VARIANTS = ['morph', 'no_forgetting', 'fixed_reset', 'stateless_summary',
            'agentless_adapted', 'rgfl_adapted', 'bm25', 'graph']
NAMES = dict(zip(VARIANTS, ['MORPH-FL', 'Continuous context', 'Fixed reset',
                           'Stateless summary', 'Agentless adaptation', 'RGFL adaptation',
                           'BM25', 'Graph retrieval']))
COLORS = dict(zip(VARIANTS, ['#0072B2', '#E69F00', '#009E73', '#CC79A7',
                            '#D55E00', '#56B4E9', '#777777', '#222222']))
rows = [json.loads(s) for s in (SOURCE / 'predictions.jsonl').read_text().splitlines()]
labels = {r['instance_id']: r for r in map(json.loads, (SOURCE / 'labels.jsonl').read_text().splitlines())}
membership = json.loads((SOURCE / 'membership.json').read_text())
snapshot = json.loads((SOURCE / 'snapshot.json').read_text())
tracker = json.loads((SOURCE / 'tracker.json').read_text())
index = {}
for r in rows:
    key = (r['track'], r['instance_id'], r['variant'], r['seed'])
    assert key not in index, key
    assert r['revision'] == labels[r['instance_id']]['revision'], key
    if r['track'] != 'retrieval':
        expected = tracker['tracker']['models'][0]
        assert r['model_id'] == expected['id'] and r['model_revision'] == expected['revision']
    index[key] = r

plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.dpi': 140, 'savefig.bbox': 'tight'})

def save(fig, name):
    for ext in ('png', 'svg'):
        fig.savefig(OUT / f'{name}.{ext}')
    plt.close(fig)

def mean(v):
    return float(np.mean(v)) if len(v) else None

def seeds(v):
    return [1] if v in ('bm25', 'graph') else [1, 2, 3]

def get(i, v):
    return [index[('retrieval' if v in ('bm25', 'graph') else 'main', i, v, s)] for s in seeds(v)]

def has(i, v):
    return all(('retrieval' if v in ('bm25', 'graph') else 'main', i, v, s) in index for s in seeds(v))

def acc(r, level, k):
    ranking = list(dict.fromkeys(r['ranking'] if level == 'files' else r.get('function_ranking') or []))
    return int(bool(set(ranking[:k]) & set(labels[r['instance_id']][level])))

def issue_metric(i, v, level, metric):
    return mean([metrics(r['ranking'] if level == 'files' else r.get('function_ranking') or [],
                         labels[i][level])[metric] for r in get(i, v)])

def cluster_interval(ids, values):
    groups = defaultdict(list)
    for i, value in zip(ids, values):
        groups[labels[i].get('repo') or get(i, 'morph')[0]['repo']].append(value)
    groups = list(groups.values())
    if len(groups) < 2:
        return None, None
    rng = np.random.default_rng(20261023)
    estimates = []
    for _ in range(4000):
        sampled = rng.integers(0, len(groups), len(groups))
        estimates.append(mean([v for j in sampled for v in groups[j]]))
    return tuple(np.quantile(estimates, [.025, .975]).tolist())

panels = {}
summary = []
effects = []
for benchmark, members in membership.items():
    common = sorted(i for i in members if all(has(i, v) for v in VARIANTS))
    file_ids = [i for i in common if labels[i]['files']]
    func_ids = [i for i in common if labels[i].get('functions')]
    panels[benchmark] = {'common': common, 'files': file_ids, 'functions': func_ids}
    for v in VARIANTS:
        entry = {'benchmark': benchmark, 'variant': v, 'n_common': len(common),
                 'n_file': len(file_ids), 'n_function': len(func_ids)}
        for level, ids in [('files', file_ids), ('functions', func_ids)]:
            for metric in ['top1', 'top5', 'top10', 'mrr', 'recall10']:
                entry[f'{level}_{metric}'] = (None if level == 'functions' and v in ('bm25', 'graph') else mean([issue_metric(i, v, level, metric) for i in ids]))
        entry['tokens_mean'] = mean([mean([(r.get('input_tokens') or 0) + (r.get('output_tokens') or 0)
                                          for r in get(i, v)]) for i in file_ids])
        reset_values = [r['resets'] for i in file_ids for r in get(i, v) if r.get('resets') is not None]
        entry['resets_mean'] = mean(reset_values)
        summary.append(entry)
        if v != 'morph':
            diffs = [issue_metric(i, 'morph', 'files', 'top1') - issue_metric(i, v, 'files', 'top1') for i in file_ids]
            lo, hi = cluster_interval(file_ids, diffs)
            effects.append(dict(benchmark=benchmark, comparator=v, n=len(file_ids),
                                delta=mean(diffs), ci_low=lo, ci_high=hi))

for name, data in [('summary', summary), ('paired_effects', effects)]:
    with (OUT / f'{name}.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0])); writer.writeheader(); writer.writerows(data)
(OUT / 'cohorts.json').write_text(json.dumps(panels, indent=2) + '\n')

fig, axes = plt.subplots(1, len(panels), figsize=(13, 4.8), squeeze=False)
for ax, (bench, panel) in zip(axes[0], panels.items()):
    for v in VARIANTS:
        values = [100 * mean([mean([acc(r, 'files', k) for r in get(i, v)]) for i in panel['files']]) for k in range(1, 11)]
        ax.plot(range(1, 11), values, label=NAMES[v], color=COLORS[v],
                linewidth=2.6 if v == 'morph' else 1.4, linestyle='--' if v in ('bm25','graph') else '-')
    ax.set(title=f'{bench}: {len(panel["files"])} matched issues', xlabel='Rank cutoff k', ylabel='File Top-k accuracy (%)', ylim=(0, 100), xticks=[1, 3, 5, 10])
    ax.grid(alpha=.2)
axes[0][-1].legend(fontsize=8, loc='lower right')
fig.suptitle('Provisional Qwen results • all workflows × three seeds on common issues')
fig.tight_layout(); save(fig, 'file_topk')

fig, axes = plt.subplots(1, len(panels), figsize=(13, 4.8), squeeze=False)
for ax, (bench, panel) in zip(axes[0], panels.items()):
    for v in VARIANTS[:6]:
        values = [100 * mean([mean([acc(r, 'functions', k) for r in get(i, v)]) for i in panel['functions']]) for k in range(1, 11)]
        ax.plot(range(1, 11), values, label=NAMES[v], color=COLORS[v],
                linewidth=2.6 if v == 'morph' else 1.4, linestyle='--' if v in ('bm25','graph') else '-')
    ax.set(title=f'{bench}: {len(panel["functions"])} function-eligible issues', xlabel='Rank cutoff k', ylabel='Function Top-k accuracy (%)', ylim=(0,100), xticks=[1,3,5,10])
    ax.grid(alpha=.2)
axes[0][-1].legend(fontsize=8, loc='lower right')
fig.suptitle('Provisional function localization • same complete-workflow cohort')
fig.tight_layout(); save(fig, 'function_topk')

fig, axes = plt.subplots(1, len(panels), figsize=(13, 5), squeeze=False)
for ax, bench in zip(axes[0], panels):
    data = [r for r in effects if r['benchmark'] == bench]
    for j, r in enumerate(data):
        x = r['delta'] * 100
        if r['ci_low'] is not None:
            ax.plot([r['ci_low']*100, r['ci_high']*100], [j,j], color=COLORS[r['comparator']])
        ax.scatter(x,j,color=COLORS[r['comparator']],s=40)
    ax.axvline(0,color='black',linewidth=.8)
    ax.set(yticks=range(len(data)), yticklabels=[NAMES[r['comparator']] for r in data], title=bench,
           xlabel='MORPH-FL − comparator, file Top-1 (percentage points)')
    ax.invert_yaxis(); ax.grid(axis='x',alpha=.2)
fig.suptitle('Paired issue effects • exploratory 95% repository bootstrap intervals')
fig.tight_layout(); save(fig, 'paired_effects')

fig, axes = plt.subplots(1, len(panels), figsize=(13, 4.8), squeeze=False)
for ax, bench in zip(axes[0], panels):
    for r in [r for r in summary if r['benchmark'] == bench]:
        v=r['variant']; ax.scatter(r['tokens_mean']/1000,r['files_top1']*100,color=COLORS[v],s=100 if v=='morph' else 55, marker={'morph':'*','no_forgetting':'o','fixed_reset':'s','stateless_summary':'D','agentless_adapted':'^','rgfl_adapted':'v','bm25':'x','graph':'+'}[v], label=NAMES[v])
        
    ax.set(title=bench, xlabel='Mean logical tokens per completed attempt (thousands)', ylabel='File Top-1 accuracy (%)', ylim=(0,100))
    ax.grid(alpha=.2)
fig.suptitle('Measured accuracy and token use • matched Qwen cohort; retries excluded')
axes[0][-1].legend(loc='upper left', bbox_to_anchor=(1.01,1), fontsize=8)
fig.tight_layout(); save(fig,'accuracy_tokens')

# The report is generated below from the same scored cohort and frozen metadata.
def pct(x): return 'NR' if x is None else f'{100*x:.2f}%'
def dec(x): return 'NR' if x is None else f'{x:.3f}'
def table(headers, values):
    return '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---']*len(headers)) + ' |\n' + '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in values) + '\n\n'
counts=Counter(r['track'] for r in rows)
planned={'retrieval':1414,'main':63630,'ablations':12000,'budgets':12000,'misdirection':6000,'policy':4500}
total=sum(counts.values())
report=f'''# MORPH-FL: detailed results and evidence report

**Run:** `ufv-full-v12-20261020-01`. **Export began:** {snapshot['started_utc']}; **finished:** {snapshot['finished_utc']}. **Status: provisional, incomplete Qwen results.**

## 1. Findings

This report scores {total:,} captured study records ({100*total/99544:.2f}% of the 99,544-record design). Unlike the earlier execution-only report, it includes measured file/function localization and matched baseline comparisons. All model performance in sections 1–7 uses Qwen2.5-Coder-7B-Instruct. Other families have passed preflight but have no primary results in this export. The full study and scientific review remain incomplete.

The October 23 comparisons in sections 1–7 require the same issue to have all six primary workflows at **all three seeds**, plus both deterministic controls. Seeds are averaged within issue before reporting means and differences. Incomplete issues are excluded from comparisons, never scored as failures. Every benchmark uses its own membership and eligible proxy labels; Lite and Verified overlap and are not independent replications.

'''
report+='## 2. Coverage and provenance\n\n'
report+=table(['Track','Captured','Planned','Coverage'],[[k,f'{counts[k]:,}',f'{n:,}',f'{100*counts[k]/n:.2f}%'] for k,n in planned.items()])
report+='\n'+table(['Benchmark','Full split','Matched issues','File eligible','Function eligible','Repositories (file cohort)'],[[b,len(membership[b]),len(p['common']),len(p['files']),len(p['functions']),len({get(i,'morph')[0]['repo'] for i in p['files']})] for b,p in panels.items()])
report+='''
The export reads a fixed byte prefix of each prediction file, set at export start, and includes only newline-terminated JSON records. Files can grow afterward. Progress tracker counts can therefore differ from captured predictions. Preflight/smoke records are excluded. The exporter reads predictions and evaluator labels only; it does not execute models, benchmark code, or change active results. It ran in scheduled job **18053** on a separate P5000 allocation.

Frozen inputs are in [snapshot](evaluation_assets/snapshot/); the [capture manifest](evaluation_assets/snapshot/snapshot.json) records source paths, byte limits, record counts and SHA-256 digests. The [cohort lists](evaluation_assets/cohorts.json), [scored summary](evaluation_assets/summary.csv), and [paired effects](evaluation_assets/paired_effects.csv) make denominators and comparisons inspectable. Prediction/source revisions and Qwen model revision are checked before scoring. Runtime repairs remain documented in the [recovery record](../UFV/runtime_recovery_20261020.md).

## 3. Localization compared with baselines

The target is **unreviewed reference-patch file/function localization**, not human-adjudicated root cause or repair success. Top-k means at least one gold target in the first k deduplicated predictions; MRR is reciprocal first-hit rank; empty completed predictions are misses. Labels with no targets are ineligible separately at file and function level. Numbers are issue means after seed averaging.

'''
for bench,panel in panels.items():
    report+=f'### {bench}\n\n'
    report+=table(['Workflow','File Top-1','File Top-5','File Top-10','File MRR','Function Top-1','Function MRR'],[[NAMES[r['variant']],pct(r['files_top1']),pct(r['files_top5']),pct(r['files_top10']),dec(r['files_mrr']),pct(r['functions_top1']),dec(r['functions_mrr'])] for r in summary if r['benchmark']==bench])
report+='\n![Measured file Top-k curves](evaluation_assets/file_topk.png)\n\n**Figure 1.** Rank-cutoff curves on the same matched issues in each panel. A curve changes the ranking cutoff, not the token budget or training time. No missing-model results are interpolated.\n\n'
report+='\n![Measured function Top-k curves](evaluation_assets/function_topk.png)\n\n**Figure 2.** Function ranking uses its own nonempty-label eligibility subset. File-only BM25 and graph controls do not produce function predictions, so their function metrics are NR and omitted from these curves. A file hit does not imply a function hit.\n\n'
report+='## 4. How well is MORPH-FL performing?\n\n'
for bench in panels:
    data=[r for r in summary if r['benchmark']==bench]
    ours=next(r for r in data if r['variant']=='morph')
    best=max((r for r in data if r['variant']!='morph'), key=lambda r:r['files_top1'])
    report+=f"On **{bench}**, MORPH-FL achieves **{pct(ours['files_top1'])} file Top-1**, **{pct(ours['files_top5'])} Top-5**, and **{dec(ours['files_mrr'])} MRR** on {ours['n_file']} matched eligible issues. The strongest observed comparator by file Top-1 is **{NAMES[best['variant']]} ({pct(best['files_top1'])})**; MORPH-FL's difference is **{100*(ours['files_top1']-best['files_top1']):+.2f} percentage points**. This comparator is selected descriptively from this snapshot, not a prespecified best-baseline hypothesis.\n\n"
for bench in panels:
    by_variant = {r['variant']: r for r in summary if r['benchmark'] == bench}
    ours = by_variant['morph']
    continuous = by_variant['no_forgetting']
    lexical = by_variant['bm25']
    rank = 1 + sum(r['files_top1'] > ours['files_top1'] for r in by_variant.values())
    report += (f"For {bench}, MORPH-FL ranks **{rank} of {len(VARIANTS)}** by observed file Top-1 (ties share rank). "
               f"It differs from continuous context by **{100*(ours['files_top1']-continuous['files_top1']):+.2f} pp** "
               f"and BM25 by **{100*(ours['files_top1']-lexical['files_top1']):+.2f} pp**. "
               f"It uses **{ours['tokens_mean']/continuous['tokens_mean']:.2f}×** the completed-attempt tokens of continuous context. "
               f"Its function Top-1 is **{pct(ours['functions_top1'])}**; mean recorded resets are **{ours['resets_mean']:.3f}** per matched attempt. "
               "The reset count describes execution behavior; it does not isolate a causal reset benefit.\n\n")
report+=table(['Benchmark','Comparator','MORPH − comparator (pp)','Exploratory 95% interval (pp)'],[[r['benchmark'],NAMES[r['comparator']],f"{r['delta']*100:+.2f}",'NR' if r['ci_low'] is None else f"[{r['ci_low']*100:+.2f}, {r['ci_high']*100:+.2f}]" ] for r in effects])
report+='''
![Paired effects and uncertainty](evaluation_assets/paired_effects.png)

**Figure 3.** Positive differences favor MORPH-FL. Intervals use 4,000 repository-cluster bootstrap replicates (fixed seed 20261023), resampling repositories and retaining all their issues. These are descriptive, unadjusted intervals from an incomplete, repeatedly observed study. Few repositories and selective completion limit their stability. They are not final significance tests. The declared final 50-contrast family and Holm correction remain pending full coverage.

In this snapshot, **MORPH-FL does not demonstrate an advantage over the strongest baseline**: stateless summary leads on file Top-1, file MRR and function Top-1 in both splits. MORPH-FL is essentially level with continuous context and fixed reset on file Top-1, while consuming about 3% more tokens than continuous context. Its clearest positive result is against lexical retrieval on Verified (+13.24 pp Top-1); that advantage is only +0.48 pp on Lite. The adaptive reset mechanism triggers infrequently (about 0.27 resets per attempt), limiting the observed contrast with continuous context. These observations motivate investigation of ranking and function grounding; they do not establish why a method wins or loses.\n\nMORPH-FL's practical value depends on whether any ranking gain justifies additional tokens, probes, and wall time. A higher Top-5 with weak Top-1 means the target is often in the shortlist but is not reliably ranked first. Similar file results can coexist with poor function localization; file hits alone do not establish precise fault understanding. The Agentless and RGFL comparators are restricted component adaptations, not reproductions of their complete upstream pipelines.

## 5. Measured token use and efficiency

'''
report+=table(['Benchmark','Workflow','Mean logical tokens','Mean resets'],[[r['benchmark'],NAMES[r['variant']],f"{r['tokens_mean']:,.0f}",dec(r['resets_mean'])] for r in summary])
report+='''
![Accuracy versus observed token use](evaluation_assets/accuracy_tokens.png)

**Figure 4.** Each point uses the same file-eligible cohort as Figure 1. Token counts are input plus output of completed attempts, averaged across seeds then issues; they exclude interrupted/retried work. Deterministic controls have zero LLM tokens but nonzero compute cost. This is an observed cost comparison at the common 32k allowance, not an accuracy-versus-budget curve. The 16k/48k side studies are not yet available, so no budget line is fabricated. Cross-hardware wall-clock and total resource claims require further accounting; Slurm accounting is disabled.

## 6. Configuration, limitations, and next evidence

The full design has 707 unique issues from Lite (300) and Verified (500), with 93 shared IDs, five pinned checkpoint families and seeds 1/2/3. Primary runs use BF16, a 16,384-token native context, temperature 0.2, top-p 0.95, top-k 50, up to 16 rounds and a 32,000-token allowance. Qwen uses one A30; CodeLlama and NeMo use two. Consult the [protocol](../../experiments/full/protocol.json), [pins](../../experiments/full/pins.json), and [living tracker](../UFV/study_progress.md). Local future source revisions are distinct from the deployed frozen protocol.

These results reflect completed early shards; they are not a random sample. Historical failures and queued retries can change the subject mix. At this snapshot, AST-query recoveries still required successful receipts; consult the current tracker for subsequent execution history. Pipeline gates establish usable inference interfaces, not accuracy. Python-only static evidence, patch-proxy targets, fixed retrieval recall, prior pilot exposure, possible training contamination and overlapping splits limit interpretation. No full-study cross-family advantage, human causal correctness, calibration, repair success or retention/recovery rate is established.

The partial ablation rows are not used to infer component benefits: matched component cohorts and trajectory opportunity denominators remain necessary. Budget, misdirection and policy studies require their own matched analyses. Historical 25-record smoke results are excluded; they validate an earlier pipeline and cannot estimate full-study performance.

The extended study is now deferred pending the pilot output-quality diagnosis described above. Before resuming expansion, validate any warranted correction in a separately versioned development run. Any eventual full-study conclusion still requires complete model/seed/workflow coverage, invalid and missing response counts, reset-retention and wrong-lead opportunity audits, interrupted/retried costs, and the declared final paired inference and multiplicity procedure. The figures above summarize measured provisional performance only.

## 7. Reproduce this report

From the repository root, with NumPy and Matplotlib available:

```bash
PYTHONPATH=src /tmp/morph-review-venv/bin/python docs/TSE/evaluation_assets/build_report.py
```

Sections 1–7 and their figures use the immutable compact snapshot. The current-status section additionally reads the local tracker metadata and completed pilot results; refreshing that metadata does not change the historical tables. Generated PNG and SVG figures are stored beside the script. Historical snapshot source hashes:

'''
for p in sorted(SOURCE.iterdir()):
    if p.is_file(): report+=f'- `{p.name}`: `{hashlib.sha256(p.read_bytes()).hexdigest()}`\n'
# Append current evidence without changing the immutable October 23 snapshot.
root = HERE.parents[2]
latest = json.loads((root / 'hpc/logs/ufv-full-v12-20261020/study-progress.json').read_text())
progress = latest['tracker']['progress']
counts_now = {track: sum(info.get('completed', 0) for cell, info in progress.items()
                         if cell.startswith(track + '__')) for track in planned}
pilot = (root / 'docs/UFV/pilot_results.md').read_text().split('\n', 1)[1].strip()
pilot = '\n'.join('#' + line if line.startswith('## ') else line for line in pilot.splitlines())
current = f"""## Current experiment status — {latest['checked_utc'][:10]}

The separate exploratory pilot is **complete: 400/400 primary predictions and 100/100 retrieval controls**, independently verified on October 25. The extended study remains **deferred** pending output-quality diagnosis. No pilot jobs are queued or running; pending extended-study jobs remain held. See the [live pilot status](../UFV/pilot_progress.md) and [extended-study tracker](../UFV/study_progress.md).

The extended-study metadata snapshot at **{latest['checked_utc']} (UTC)** contains **{sum(counts_now.values()):,}/99,544 progress records**: {counts_now['retrieval']:,} retrieval, {counts_now['main']:,} primary, {counts_now['ablations']:,} ablation, {counts_now['budgets']:,} budget, {counts_now['misdirection']:,} misdirection and {counts_now['policy']:,} policy records. All five model preflights passed. These are execution counts, not a newly scored full-study export or proof of scientific completeness. Pilot-only records remain separate; its reused records already belong to the full run and must not be added again.

## Completed exploratory pilot: new results

{pilot}

### Local corrections and validation

The ambiguity-deduplication correction and finalization fixes are local development changes. Finalization now supports package invocation and validates receipt coverage without double-counting imported records in resumed cells. The October 27 check passed 123 tests and the HPC self-tests. These checks establish software behavior; they provide no new model accuracy evidence. The frozen pilot/full-study runtime and saved predictions remain preserved. See the [output-quality review](../UFV/pilot_quality_review.md) for the demonstrated prompt-growth defect and remaining diagnostic work.

## Preserved October 23 full-study snapshot

Sections 1–7 and Figures 1–4 below retain the immutable October 23 export: a different completion-selected cohort, six workflows and three-seed averaging. The pilot above uses 50 fixed issues, four workflows and seed 1; its results are not pooled with those tables. The 7,291 captured records below and 9,926 current progress records refer to different snapshot times and evidence types.

"""
report = report.replace('# MORPH-FL: detailed results and evidence report\n\n',
                        '# MORPH-FL: detailed results and evidence report\n\n' + current, 1)
(HERE.parent / 'EVALUATION_RESULTS_REPORT.md').write_text(report)
print('Scored',len(rows),'records; cohorts:',{b:len(p['files']) for b,p in panels.items()})
