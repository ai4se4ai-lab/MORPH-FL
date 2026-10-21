"""Render the living study plan from read-only run metadata and receipts."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = ROOT / 'docs/UFV/study_progress.md'
CORE = ['morph', 'no_forgetting', 'fixed_reset', 'stateless_summary', 'agentless_adapted', 'rgfl_adapted']
ABLATIONS = ['context_only', 'single_hypothesis', 'no_mde', 'no_probes', 'no_skeptic', 'independent_agents', 'one_agent', 'rerank']


def render_document(state):
    s = state.get('tracker', {})
    run = state['run']
    models = s.get('models', [])
    data = s.get('data', {})
    n = data.get('unique_cases', 707)
    m = len(models) or 5
    sample = min(100, n)
    seeds = len(s.get('protocol', {}).get('seeds', [1, 2, 3]))
    planned = dict(retrieval=2*n, main=n*6*m*seeds, ablations=sample*8*m*seeds,
                   budgets=sample*8*m*seeds, misdirection=sample*4*m*seeds, policy=sample*3*m*seeds)
    progress = s.get('progress', {})
    receipts = s.get('receipts', {})
    stages = s.get('stages', [])
    results = s.get('results', 'Remote results not yet inspected')
    logs = s.get('log_root', '')
    active = {}
    for line in state.get('active', '').splitlines():
        if '|' in line:
            job, scheduler_state = line.split('|', 1)
            if active.get(job) != 'RUNNING':
                active[job] = scheduler_state
    # A scheduler-terminal run is not evidence of complete experimental coverage.
    report = s.get('completeness') or state.get('scientific_completeness')
    complete = bool((report or {}).get('complete'))
    completeness_label = 'verified complete' if complete else ('INCOMPLETE (coverage report)' if report else 'not yet established')

    def count(track, variant=None, model=None, budget=None, window=None):
        total = 0
        for name, info in progress.items():
            if not name.startswith(track + '__'):
                continue
            if model is not None and f'__m{model}__' not in name:
                continue
            if variant is None and budget is None and window is None:
                total += info.get('completed', 0)
            else:
                for key, value in info.get('conditions', {}).items():
                    v, b, w = key.split('@', 2)
                    if (variant is None or v == variant) and (budget is None or b == str(budget)) and (window is None or w == str(window)):
                        total += value
        return total

    def relevant(track):
        return [v for v in stages if v['name'] == track or v['name'].startswith(track + '_m')]

    def recovering(selected):
        failed_stages = [v for v in selected if v.get('failures')]
        return bool(failed_stages) and all(
            v.get('cells') == 1 and v.get('jobs')
            and active.get(v['jobs'][-1]) == 'RUNNING'
            and all(f.get('job') and f['job'] != v['jobs'][-1] for f in v['failures'])
            for v in failed_stages)

    def recovery_label(track):
        info = state.get('recovery_io') or {}
        if track == 'retrieval' and info.get('phase') == 'COMPACTING' and info.get('fraction') is not None:
            return f"RECOVERY RUNNING: checkpoint compaction {info['fraction']:.1%} of source bytes; telemetry {info.get('observed_utc', 'unknown')} UTC; awaiting verified receipt"
        return 'RECOVERY RUNNING: earlier attempt failed; awaiting verified receipt'

    def status(track):
        selected = relevant(track)
        if any(v.get('failures') for v in selected):
            if recovering(selected):
                return recovery_label(track)
            return 'ATTENTION: failed step'
        cells = sum(v['cells'] for v in selected)
        valid = [v for k,v in receipts.items() if k.startswith(track + '__') and v.get('complete')]
        if cells and len(valid) == cells and sum(v.get('records', 0) for v in valid) == planned[track]:
            return 'COMPLETE (receipts verified)'
        if count(track) >= planned[track]:
            return 'Records written; awaiting verified receipts'
        if any(active.get(j) == 'RUNNING' for v in selected for j in v.get('jobs', [])):
            return 'RUNNING'
        return 'PARTIAL / queued' if count(track) else 'WAITING'

    def step_status(name):
        selected = [v for v in stages if v['name'] == name]
        if any(v.get('failures') for v in selected):
            if recovering(selected):
                return 'RECOVERY RUNNING: earlier attempt failed; awaiting verified receipt'
            return 'ATTENTION: failed step'
        if selected and all(v.get('successful_steps', 0) == v.get('expected_steps', -1) for v in selected):
            return 'COMPLETE'
        if any(active.get(job) == 'RUNNING' for v in selected for job in v.get('jobs', [])):
            return 'RUNNING'
        return 'WAITING / unverified'

    def evidence(relative):
        return f'`R/{relative}`'

    rows = []
    def row(phase, primary, detailed, why, state_text, overview, where):
        rows.append([phase, primary, detailed, why, state_text, overview, where])

    def metrics(track, variant=None, model=None, budget=None, window=None):
        measured = [v for v in s.get('summary_rows', []) if v.get('track') == track and (variant is None or v.get('variant') == variant) and (model is None or v.get('model') == model) and (budget is None or v.get('budget') == str(budget)) and (window is None or v.get('window') == str(window))]
        values = [float(v['top1']) for v in measured if v.get('top1') not in ('', None)]
        if not values:
            return 'Accuracy/effect estimates not generated yet.'
        label = 'Complete' if complete else 'PARTIAL'
        return f'{label} summary-cell File Top-1 means (model/workflow/benchmark/condition): {min(values):.1%}–{max(values):.1%}; see denominators and paired intervals in analysis.'

    row('0', 'Design and reproducibility', 'Select five families; pin model revisions and licenses',
        'Test whether behavior generalizes across independently trained families; prevent checkpoint drift.',
        'COMPLETE' if len(models) == 5 else 'UNVERIFIED',
        '; '.join(v['id'] for v in models) or 'Awaiting model metadata.', '[Model evidence](../../experiments/full/models.md); '+evidence('model_selection.json')+'; frozen deployment `experiments/full/pins.json`')
    row('0', 'Design and reproducibility', 'Freeze shared protocol, seeds and outcome definitions',
        'Make workflow comparisons interpretable under common BF16, context, sampling and token budgets.',
        'COMPLETE' if s.get('protocol') else 'UNVERIFIED',
        f'{seeds} seeds; 16,384 context; 32k primary budget; up to 16 rounds. The frozen scientific protocol is authoritative; explicitly recorded runtime repairs are listed below. Local future changes are not deployed automatically.',
        'Frozen deployment `experiments/full/protocol.json`; `L/config/`; `L/run_manifest.json`')
    row('1', 'HPC and validation history', 'SSH/Slurm access, A30 allocation, SIF and dependency/Git packaging',
        'Run computation in scheduled GPU allocations and keep environments reproducible without many shared-filesystem package files.',
        'COMPLETE' if s.get('preflights') else 'UNVERIFIED', 'All five active gates demonstrate a working GPU runtime; CodeLlama/NeMo use two A30s, other families one.', '`/home/babaei/morph-ufv/runtime/`; `L/env/`; `L/gpu/`; [cluster guide](slurm_cluster_guide.md)')
    smoke = ROOT / 'hpc/logs/ufv-20261020/ufv-smoke-20261020-01/results/raw/analysis/completeness.json'
    smoke_data = json.loads(smoke.read_text()) if smoke.exists() else {}
    row('1', 'HPC and validation history', 'Original end-to-end smoke',
        'Exercise every stage interface before spending resources on the full study; smoke scores are not scientific full-study results.',
        'HISTORICAL COMPLETE' if smoke_data.get('complete') else 'Historical evidence not available locally',
        '25/25 small study records plus separate preflight records; validates the earlier runtime/pipeline only.',
        '[Archived smoke](../../hpc/logs/ufv-20261020/ufv-smoke-20261020-01/results/summary.md)')
    row('1', 'HPC and validation history', 'Runtime regression tests and native tokenizer/context checks',
        'Check code behavior, common context support, multi-turn formatting and the Mistral tokenizer correction before real model gates.',
        'HISTORICAL COMPLETE', 'Archived UFV validation: 15 applicable tests passed; all five tokenizer/context checks passed. Later local test counts and changes are recorded in the revision history, not substituted for active GPU evidence.',
        '[Runtime validation artifacts](../../hpc/logs/ufv-fivefam-20261020/validation/); [later regression evidence](five_family_transition.md#verification)')
    row('1', 'HPC and validation history', 'Failed original five-family run; v5/v8/v11 prompt/parser/schema validation',
        'Expose malformed JSON, echoed input, schema incompatibilities and smoke/full-budget mismatches before accepting model gates.',
        'ARCHIVED / SUPERSEDED', 'Original run had 0/99,544 study records and four failed model gates. Subsequent revisions are validation history, not additional independent study results.',
        '[Transition and validation history](five_family_transition.md); `hpc/logs/ufv-fivefam-20261020/`; `hpc/logs/ufv-review-*/`')
    row('1', 'HPC and validation history', 'v12 common task/schema and strict parser; local future fixes',
        'Ensure gates require actual task-shaped outputs; preserve invalid responses and prohibit treating copied input as hypotheses.',
        'ACTIVE v12 VALIDATED' if len(s.get('preflights', {})) == 5 else 'UNVERIFIED', 'All active gates checked below. Later local resume/launcher fixes remain future work unless separately deployed and revalidated.',
        '[Revision evidence](five_family_transition.md); frozen protocol hashes in `L/run_manifest.json`')
    row('2', 'Benchmark preparation', 'Load pinned Lite/Verified splits; deduplicate overlap and isolate proxy labels',
        'Cover both full benchmarks without double-running shared issues or leaking evaluator patches into model inputs.',
        step_status('data'), f"{n} unique issues; sizes {data.get('benchmark_sizes', {})}; overlap {data.get('overlap', 'unknown')}. Targets are unreviewed patch-change proxies.",
        evidence('data/manifest.json')+'; '+evidence('data/membership.json')+'; '+evidence('data/cases.jsonl')+'; '+evidence('data/labels.jsonl'))
    row('2', 'Benchmark preparation', 'Pack pre-fix Python source, freeze archive identities, choose side sample',
        'Prevent post-fix/source drift and reduce inode pressure; select side-study subjects without reading outcomes.',
        step_status('data'), f'All {n} prepared cases are available; source hashes are verified during execution. Side studies use {sample} report-blind repository-balanced subjects.',
        evidence('data/archives/')+'; '+evidence('data_reuse.json')+'; frozen `suite.py:selected_cases`')
    for index, model in enumerate(models):
        downloaded = s.get('downloaded', {}).get(str(index), {})
        pin_ok = all(downloaded.get(k) == model.get(k) for k in ('id', 'revision'))
        row('3', 'Pinned model assets', model['id'], 'Use the intended instruction checkpoint in BF16; avoid silent substitution or quantization.',
            'COMPLETE' if pin_ok else 'WAITING / unverified', 'Pinned model assets present.' if pin_ok else 'No matching model-asset receipt yet.', evidence(f'models/{index}.pin.json')+'; '+evidence(f'models/{index}/'))
        gate = s.get('preflights', {}).get(str(index), {})
        gate_ok = gate.get('complete') and gate.get('valid_hypotheses', 0) > 0 and gate.get('output_tokens', 0) > 0 and gate.get('budget') == 32000 and set(gate.get('workflows', {})) == set(CORE)
        row('4', 'Real-inference gates', model['id']+' — all six workflows',
            'Verify actual GPU inference and usable structured MORPH hypotheses under the common 32k protocol before allowing main comparisons.',
            'COMPLETE' if gate_ok else ('ATTENTION: invalid gate receipt' if gate else 'WAITING / unverified'),
            f"MORPH: {gate.get('valid_hypotheses', 0)} valid hypotheses, {gate.get('output_tokens', 0):,} output tokens; {len(gate.get('workflows', {}))}/6 workflow checks. Gate success is not full-benchmark accuracy.",
            evidence(f'models/{index}.preflight.json')+'; '+evidence(f'predictions/preflight__main__m{index}__s1__p0.jsonl'))
    row('4', 'Checkpoint reliability', 'Lossless packing/restart of retrieval checkpoint; extend scheduler limit',
        'Keep the growing result checkpoint within memory limits while preserving exact record identities and resumability.',
        'HISTORICAL COMPLETE', '315 records were packed and verified by before/after logical hashes; retrieval resumed. Later local v13 resume improvements are not silently part of active v12.',
        '[Maintenance evidence](../../hpc/logs/ufv-full-v12-20261020/checkpoint-maintenance/); [history](five_family_transition.md#verified-retrieval-recovery--october-20-094603-utc)')
    maintenance = s.get('runtime_maintenance')
    if maintenance:
        validation = s.get('maintenance_validation') or {}
        row('4', 'Runtime maintenance and recovery', maintenance['id'],
            'Handle deep benchmark ASTs without recursion overflow; stream checkpoint resume to avoid loading a 209 GB file; preserve completed records and restore primary dependencies.',
            'VALIDATED; recovery jobs governed by receipts' if validation.get('complete') else 'VALIDATION / RECOVERY IN PROGRESS',
            ('Replacement graph submitted: ' + str((s.get('maintenance_recovery') or {}).get('complete', False)) + '. ') + 'Scientific protocol remains byte-identical. New predictions record the runtime-maintenance manifest hash; original source backups and failed attempts are retained. '
            + (f"Failing case {validation.get('case')}: original crash reproduced and patched analysis completed; ordinary-source exact equivalence verified." if validation.get('complete') else 'Exact failing-case validation not established yet.'),
            '`L/maintenance/ast-recovery-20261020/`; frozen deployment `experiments/full/runtime_maintenance.json`; [repair report](runtime_recovery_20261020.md)')
    row('5', 'Retrieval controls (RQ1)', 'BM25 + graph, once per unique issue',
        'Provide deterministic non-LLM reference rankings without model/seed pseudo-replication.', status('retrieval'), f"{count('retrieval'):,}/{planned['retrieval']:,} progress records. "+metrics('retrieval'), evidence('predictions/retrieval__m0__s1__p0.jsonl')+'; '+evidence('receipts/retrieval__m0__s1__p0.json'))
    for variant in ('bm25', 'graph'):
        row('5', 'Retrieval controls (RQ1)', variant, 'Separate lexical relevance from structural retrieval as a localization control.', status('retrieval') if count('retrieval', variant) < n else 'Records written; track receipt governs completion', f"{count('retrieval', variant):,}/{n:,} records. "+metrics('retrieval', variant), evidence('progress/retrieval__m0__s1__p0.jsonl')+'; '+evidence('scores/retrieval__m0__s1__p0.csv'))
    row('6', 'Primary comparison (RQ1)', 'All five models × three seeds × six workflows × 707 issues',
        'Estimate file/function localization effectiveness and compare memory/search strategies on the same subjects.', status('main'), f"{count('main'):,}/{planned['main']:,} records. "+metrics('main'), evidence('predictions/main__*.jsonl')+'; '+evidence('scores/main__*.csv')+'; '+evidence('analysis/summary.csv'))
    reasons = ['Evaluate the complete evidence-preserving search/reset design.', 'Measure continuous-context behavior to isolate the effect of forgetting.', 'Compare adaptive forgetting with periodic reset scheduling.', 'Test compressed stateless memory against retained evidence/state.', 'Compare a restricted Agentless localization interface; not its entire repair pipeline.', 'Compare a restricted RGFL component interface; not the full upstream graph pipeline.']
    for variant, why in zip(CORE, reasons):
        row('6', 'Primary comparison (RQ1)', variant, why, status('main'), f"{count('main', variant):,}/{n*m*seeds:,} records. "+metrics('main', variant), evidence('predictions/main__m<model>__s<seed>__p<shard>.jsonl')+'; '+evidence('analysis/paired.json'))
    for index, model in enumerate(models):
        row('6', 'Primary comparison (RQ1)', model['id']+' — three seeds / 32 shards',
            'Expose family-specific behavior; do not treat a result from one model as universal.', step_status(f'main_m{index}') if count('main', model=index) == 0 else status('main'), f"{count('main', model=index):,}/{n*6*seeds:,} records. "+metrics('main', model=model['id']), evidence(f'predictions/main__m{index}__s*__p*.jsonl')+'; '+evidence(f'progress/main__m{index}__s*__p*.jsonl'))
    row('7', 'Component ablations (RQ2)', 'Eight controls on the fixed side sample',
        'Identify which search, evidence, probing and agent components account for changes relative to matched primary cases.', status('ablations'), f"{count('ablations'):,}/{planned['ablations']:,} records. "+metrics('ablations'), evidence('predictions/ablations__*.jsonl')+'; '+evidence('analysis/summary.csv'))
    ablation_reasons = ['Retain all models during context resets to isolate forgetting from explicit model-state pruning.', 'Remove competing hypotheses to test hypothesis diversity.', 'Disable explicit model memory to measure the contribution of persistent model-derived state.', 'Remove probes to test the contribution of additional observations.', 'Remove the skeptic to test explicit falsification.', 'Separate agents to test shared evidence/state.', 'Use one agent to test multi-role coordination.', 'Use reranking to test search versus ranking alone.']
    for variant, why in zip(ABLATIONS, ablation_reasons):
        row('7', 'Component ablations (RQ2)', variant, why, status('ablations'), f"{count('ablations', variant):,}/{sample*m*seeds:,} records. "+metrics('ablations', variant), evidence('predictions/ablations__*.jsonl')+'; '+evidence('scores/ablations__*.csv'))
    row('8', 'Token-budget study (RQ3)', '16k and 48k runs; reuse matched 32k primary point',
        'Measure quality/token trade-offs on identical subjects rather than extrapolating a cost curve.', status('budgets'), f"{count('budgets'):,}/{planned['budgets']:,} additional records. "+metrics('budgets'), evidence('predictions/budgets__*.jsonl')+'; '+evidence('analysis/budget_points.csv')+'; '+evidence('analysis/budget_curves.pdf'))
    for budget in (16000, 32000, 48000):
        overview = f"{count('budgets', budget=budget):,}/{sample*4*m*seeds:,} additional records." if budget != 32000 else 'Reuses matching primary records; no duplicate 32k budget runs are planned.'
        row('8', 'Token-budget study (RQ3)', f'{budget:,} tokens × four memory workflows', 'Separate sensitivity to resource ceilings from changes in evaluated subjects.', status('main' if budget == 32000 else 'budgets'), overview + (' '+metrics('budgets', budget=budget) if budget != 32000 else ''), evidence('analysis/budget_points.csv'))
    row('9', 'Misdirection / recovery (RQ2)', 'Disclosed BM25-rank-2 clue × four memory workflows',
        'Test recovery from a report-blind clue; count recovery only when the proxy-wrong clue actually became the first valid leader.', status('misdirection'), f"{count('misdirection'):,}/{planned['misdirection']:,} records. " + s.get('analysis_overviews', {}).get('recovery_summary.csv', 'Eligibility and recovery rates are not available until analysis.') + ' '+metrics('misdirection'), evidence('predictions/misdirection__*.jsonl')+'; '+evidence('analysis/recovery.json')+'; '+evidence('analysis/recovery_summary.csv'))
    for variant in CORE[:4]:
        row('9', 'Misdirection / recovery (RQ2)', variant, 'Compare memory policies on the same injected clue; retain unconditional and eligibility-conditioned outcomes.', status('misdirection'), f"{count('misdirection', variant):,}/{sample*m*seeds:,} records. "+metrics('misdirection', variant), evidence('analysis/recovery_summary.csv'))
    row('10', 'Reset-policy sensitivity (RQ2)', 'Windows 3/4/5; optional 15% original-budget gate',
        'Test whether outcomes depend on operational reset thresholds without selecting an optimum after observing results.', status('policy'), f"{count('policy'):,}/{planned['policy']:,} records. "+metrics('policy'), evidence('predictions/policy__*.jsonl')+'; '+evidence('analysis/summary.csv'))
    for window in (3, 4, 5):
        row('10', 'Reset-policy sensitivity (RQ2)', f'Window {window}', 'Measure sensitivity to the forgetting window on identical side subjects.', status('policy'), f"{count('policy', window=window):,}/{sample*m*seeds:,} records. "+metrics('policy', window=window), evidence('progress/policy__*.jsonl'))
    analysis_status = 'COMPLETE COVERAGE; review estimates' if complete else ('PARTIAL ANALYSIS' if s.get('analysis_files') else 'WAITING')
    analyses = [
        ('Exact-key completeness and scoring', 'Require the exact planned model/seed/subject/condition keys; missing cases remain missing.', 'completeness.json; summary.csv', f"Complete={complete}; observed progress {sum(count(t) for t in planned):,}/{sum(planned.values()):,}. Progress alone is not scientific completeness."),
        ('Per-benchmark File Top-1/5/10, MRR and exact-function metrics', 'Measure localization at multiple ranks; disclose eligible denominators and correlated benchmark overlap.', 'summary.csv; SWE-bench_*-topk.pdf', metrics('main')),
        ('Paired intervals and repository-cluster comparisons', 'Average seeds within cases and account for repository clusters; quantify uncertainty in paired differences.', 'paired.json', 'Estimates unavailable until generated; no superiority claim from the largest point estimate.'),
        ('Primary Holm-adjusted testing family', 'Control multiplicity across five comparators × five models × two benchmarks (50 comparisons).', 'primary_comparisons.json', 'Confirmatory interpretation requires complete non-smoke data and assumptions.'),
        ('Reset retention and process diagnostics', 'Check that actual reset events preserve observations; examine switches, duplicate probes, tokens and measured time.', 'reset_retention.json; summary.csv', 'Retention alone does not establish causal recovery or a forgetting benefit.'),
        ('Recovery eligibility and budget plots', 'Report clue outcomes, valid recovery denominators and measured matched-budget trade-offs.', 'recovery_summary.csv; budget_points.csv; budget_curves.pdf', 'No invented confidence/calibration scores or interpolated trajectories.'),
        ('RQ/evidence coverage audit', 'Separate supported proxy-localization claims from missing human, dynamic and calibration evidence.', 'rq_coverage.json', 'Confidence is null; human causal validity and executable reproduction remain unmeasured.'),
    ]
    for detailed, why, paths, overview in analyses:
        generated = [s.get('analysis_overviews', {}).get(p.strip()) for p in paths.split(';')]
        if any(generated):
            overview = ' '.join(v for v in generated if v) + ' ' + overview
        row('11', 'Analysis and validation', detailed, why, analysis_status, overview, '; '.join(evidence('analysis/'+p.strip()) for p in paths.split(';')))
    collection_jobs = [job for stage in stages if stage['name'] == 'collect' for job in stage.get('jobs', [])]
    collection_job = collection_jobs[-1] if collection_jobs else 'not yet submitted'
    row('12', 'Collect and preserve results', f'Run collection job {collection_job} after all required stages terminate',
        'Preserve tables, figures, raw prediction archives, step ledger and resource audit, including failed attempts.', step_status('collect'), 'Final collection is pending.' if not state.get('done') else ('Scheduler terminal; exact-key report determines success.'), '`L/results/`; `L/steps.tsv`; `L/gpu/`; '+evidence('analysis/report.md'))
    row('12', 'Collect and preserve results', 'Copy final compact artifacts locally; retain large graphs/evidence on UFV',
        'Make reviewable results available locally while keeping the full audit within available storage.', 'COMPLETE TRANSFER' if state.get('collected_locally') else 'MONITORING / WAITING', state.get('collected_locally', 'Automatic collector running; final result copy not available yet.'), f'`hpc/logs/ufv-full-v12-20261020/{run}/results/`; `status.json` inventories remote archive sizes')
    row('13', 'Scientific interpretation', 'Review outcomes, effect sizes, limitations and manuscript claims',
        'Completion is not evidence of a positive effect; conclusions must follow observed results and remaining validity gaps.', 'REQUIRES HUMAN REVIEW', 'Not automatically marked complete. Manuscript export/typesetting is not scheduled on UFV because docs/TSE is absent.', '[Study evidence](../../experiments/full/models.md); final `R/analysis/report.md`; manuscript review notes (to be written)')
    observed = sum(count(t) for t in planned)
    text = [
        '# MORPH-FL study phases, progress and results', '',
        f"**Active run:** `{run}`  |  **Remote snapshot:** {state.get('checked_utc', 'unknown')} (UTC)  |  **Document refreshed:** {state.get('publication', {}).get('utc', 'unknown')} (UTC)", '',
        f'**Current picture:** {observed:,}/{sum(planned.values()):,} study progress records; '
        f"{sum(bool(v.get('complete')) for v in s.get('preflights', {}).values())}/{m} model preflights passed. "
        f"Scientific completeness: **{completeness_label}**. "
        'The 30 separate preflight records and historical smoke are excluded from the study total.', '',
        ('This is the living execution plan. Cron on comp370 checks and refreshes it every 30 minutes, independently of an interactive login. ' if state.get('monitor_mode') == 'cron' else 'This is the living execution plan. It refreshes every 30 minutes while the continuous monitor is running; remote checks continue once per minute. A final collection triggers an additional refresh. ') +
        'Read the UTC timestamp to detect stale information. Completed experiment rows require receipts; record counts alone do not establish success. '
        'RECOVERY RUNNING means a replacement job is active after a failed attempt; it does not establish completion. Historical failures stay in the failure log. Outcome statistics appear when analysis generates them; no missing scores are filled in.', '',
        'Execution order: design/history → data/assets → five real-inference gates → retrieval → primary → ablations → budgets → misdirection → policy → analysis/collection → scientific review. '
        'Primary and side model groups run serially; small-model arrays can run two cells concurrently.', '',
        '## How to read result locations', '',
        f'- **R** = `{results}` on UFV (partial outputs exist here during execution).',
        f'- **L** = `{logs}` on UFV (frozen config, scheduler/step logs, final collected results).',
        '- Connect with `ssh babaei@slurm.soc.ufv.ca` to inspect these remote paths; code-formatted remote paths are not local file links.',
        '- Local live metadata: [status](../../hpc/logs/ufv-full-v12-20261020/status.json) and [tracker snapshot](../../hpc/logs/ufv-full-v12-20261020/study-progress.json).',
        '- Globs (`*`) describe multiple cells. A planned result path is not proof the artifact already exists.', '',
        '## Phase-by-phase table', '',
        '| Phase | Primary step | Detailed step / experiment | Why required / contribution to the study | Status | Results overview | Detailed results / evidence |',
        '|---|---|---|---|---|---|---|',
    ]
    rows.sort(key=lambda values: int(values[0]))
    overview = []
    for phase in sorted({r[0] for r in rows}, key=int):
        group = [r for r in rows if r[0] == phase]
        statuses = {r[4] for r in group}
        if any('ATTENTION' in value for value in statuses):
            phase_status = 'ATTENTION'
        elif any(value.startswith('RECOVERY RUNNING') for value in statuses):
            phase_status = 'RECOVERY RUNNING'
        elif any(value == 'RUNNING' for value in statuses):
            phase_status = 'RUNNING'
        elif phase == '4' and len(s.get('preflights', {})) == m and all(v.get('complete') for v in s.get('preflights', {}).values()):
            phase_status = 'COMPLETE (all model gates passed)'
        elif phase == '5' and status('retrieval') == 'COMPLETE (receipts verified)':
            phase_status = 'COMPLETE (receipts verified)'
        elif phase == '13':
            phase_status = 'Requires scientific review'
        elif phase == '1':
            phase_status = 'Completed runtime and archived validation history'
        elif all('COMPLETE' in value and 'INCOMPLETE' not in value for value in statuses):
            phase_status = 'COMPLETE'
        else:
            phase_status = 'Waiting / partially complete'
        overview.append(f'| {phase} | {group[0][1]} | {phase_status} |')
    insert = text.index('## Phase-by-phase table')
    text[insert:insert] = ['## At a glance', '', '| Phase | Primary phase | Current status |', '|---|---|---|', *overview, '']
    for values in rows:
        text.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', '<br>') for v in values) + ' |')
    text.extend(['', '## Evidence outside this scheduled study', '',
                 'Human-adjudicated root causes, independently rated causal explanations, dynamic benchmark reproductions, non-null confidence/calibration, full upstream Agentless/RGFL reproductions, and additional language ecosystems are **not scheduled or established by this graph**. '
                 'They are evidence gaps or separate future studies, not hidden completed phases. The present labels are static patch proxies, and prior pilot subjects mean this is not an untouched holdout.', '',
                 '## Refresh and provenance', '',
                 'Generated by `hpc/ufv/study_tracker.py` from the active remote config, model/data manifests, incremental progress files, workflow receipts, latest step ledger and available analysis tables. '
                 'It does not execute inference, run statistical analysis, change active source files, or modify Slurm jobs. '
                 'Edits to the table are overwritten on refresh; change the generator for durable plan edits. Historical narrative and repair evidence remain in [five_family_transition.md](five_family_transition.md).', '',
                 f"Metadata read errors: {len(s.get('errors', []))}. " + ('; '.join(s.get('errors', [])) or 'None reported.'), ''])
    publication = state.get('publication', {})
    def cell(value):
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', '<br>')
    text.extend(['## Failure and recovery log', '',
                 'Incidents persist after recovery. OPEN means unresolved by available evidence, not an inferred root cause. '
                 'Log excerpts are bounded tails captured when inspected; full logs and the ledger are authoritative. '
                 'A successful later step is recorded as recovery without erasing the failed attempt. Scheduler accounting failures are also captured; scheduler-only incidents remain OPEN until reviewed, even if another job succeeds.', '',
                 '| ID / state | First / last observed (UTC) | Run / stage / cell / step | Failure details and command | Evidence / investigation |',
                 '|---|---|---|---|---|'])
    incidents = publication.get('failures', {})
    for incident in incidents.values():
        identity = ' / '.join(str(incident.get(k, '—')) for k in ('run', 'stage', 'cell', 'step'))
        detail = '; '.join(f'{k}: {incident[k]}' for k in ('kind', 'time', 'job', 'task', 'restart', 'scheduler_state', 'rc', 'note', 'command', 'detail', 'tail') if incident.get(k) is not None)
        evidence = '; '.join(str(incident[k]) for k in ('log', 'ledger') if incident.get(k))
        evidence += '; Inspect the recorded attempt and surrounding log; establish cause before rerunning or changing the frozen study.'
        text.append('| ' + ' | '.join(cell(v) for v in (incident['id'] + ' / ' + incident['status'], incident['first_seen'] + ' / ' + incident['last_seen'], identity, detail, evidence)) + ' |')
    if not incidents:
        text.append('| — | — | Active monitored run | No failures observed in available metadata. Historical superseded attempts are linked in phase 1. | Not proof that every scheduler attempt succeeded. |')
    text.extend(['', '## Refresh change log', '',
                 'Every document publication is recorded below, including refreshes with no measured progress. '
                 'UTC publication time can differ from the last successful remote snapshot shown above. '
                 'History starts when logging was enabled; earlier refreshes cannot be reconstructed. '
                 'Persistent machine-readable history: `' + publication.get('history_path', 'hpc/logs/ufv-full-v12-20261020/tracker-history.json') + '`.', '',
                 '| Refreshed (UTC) | Run | Remote snapshot (UTC) | Trigger | Updates made |',
                 '|---|---|---|---|---|'])
    for entry in publication.get('refreshes', []):
        text.append('| ' + ' | '.join(cell(entry.get(k, '')) for k in ('utc', 'run', 'snapshot_utc', 'reason', 'changes')) + ' |')
    return '\n'.join(text) + '\n'


def update_document(state, output=DOCUMENT, history_path=None):
    if not state.get('tracker'):
        return
    try:
        from .tracker_history import refresh
    except ImportError:
        from tracker_history import refresh
    output = Path(output)
    return refresh(state, output, history_path or ROOT / 'hpc/logs/ufv-full-v12-20261020/tracker-history.json', force=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=DOCUMENT)
    options = parser.parse_args()
    update_document(json.loads(options.snapshot.read_text()), options.output)
