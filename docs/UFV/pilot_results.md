# Completed fast pilot: results and interpretation

Verified October 25, 2026, 01:58 UTC. **400/400 primary predictions and
100/100 retrieval-control predictions are complete.** There are no missing
planned primary keys. This establishes pilot execution completeness, not
scientific superiority or completion of the extended study.

The pilot uses the same 50 repository-balanced issues across Qwen2.5-Coder 7B
and DeepSeek-Coder 6.7B, seed 1, four workflows, BF16, a 32k token ceiling and
16 rounds. Selection excluded the recorded previously inspected IDs before
outcomes were read. It reused 132 validated primary predictions and generated
268 more across 33 successful cells. The frozen inference sources, protocol,
case provenance and prediction signatures passed independent validation in
scheduled CPU job **18143**. Earlier collection job **18107** also completed
without reported errors.

| Model | Workflow | File Top1 (50 eligible issues) | File Top5 | Function Top1 (48 eligible issues) | Mean tokens | Mean seconds | Mean resets |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen | MORPH | 42% | 72% | 16.7% | 28,257 | 93.6 | 0.2 |
| Qwen | No-forgetting | 42% | 74% | 16.7% | 27,574 | 89.5 | 0.0 |
| Qwen | Fixed-reset | 42% | 76% | 14.6% | 29,114 | 94.7 | 1.0 |
| Qwen | Stateless-summary | 50% | 78% | 22.9% | 29,325 | 140.3 | 0.0 |
| DeepSeek | MORPH | 40% | 70% | 0% | 29,197 | 55.0 | 0.6 |
| DeepSeek | No-forgetting | 40% | 70% | 0% | 27,912 | 48.3 | 0.0 |
| DeepSeek | Fixed-reset | 40% | 70% | 0% | 29,553 | 53.8 | 1.4 |
| DeepSeek | Stateless-summary | 40% | 72% | 12.5% | 29,920 | 111.5 | 0.0 |

Both deterministic controls, BM25 and graph retrieval, achieve **40% file
Top1, 70% Top5 and 86% Top10** on these same 50 issues. They are run once per
issue rather than duplicated across models. They do not supply function rankings.

MORPH shows no file Top1 advantage over no-forgetting or fixed-reset in either
model. Against stateless-summary, its difference is -8 percentage points on
Qwen and zero on DeepSeek. Descriptive 95% repository-cluster bootstrap intervals
are [-16, 0] and [-9.8, +12.0] percentage points respectively, across 12
repositories. These exploratory, unadjusted intervals are not evidence of
equivalence or a confirmatory significance test.

Summary has better observed function Top1 on both models and better file
Top1 on Qwen, at higher completed-case time. MORPH does not show a token or
runtime benefit over no-forgetting in this sample. Cost figures cover completed
cases; interrupted-attempt overhead and an end-to-end cost accounting are
separate concerns.

## Output quality limits interpretation

| DeepSeek workflow | Cases with final hypotheses / 50 | Invalid-response events |
|---|---:|---:|
| MORPH | 6 | 68 |
| No-forgetting | 6 | 63 |
| Fixed-reset | 7 | 69 |
| Stateless-summary | 47 | 50 |

All invalid-response events above report missing usable localization JSON with
a hypothesis list. Event counts can exceed case counts. Qwen retains final
hypotheses on 49/50 cases for each of the first three workflows and 50/50 for
summary. Empty final pools can also arise from valid-empty responses or
retention decisions; malformed JSON alone has not been established as the
cause of every empty pool.

When the final hypothesis pool is empty, the implementation retains the
retrieval ranking and derives no function ranking from hypotheses. DeepSeek's
file accuracy therefore cannot by itself establish that the intended
hypothesis-based mechanism is working. MORPH performs few resets on average
(0.2 Qwen, 0.6 DeepSeek); this pilot also gives limited evidence about repeated
forgetting/recovery behavior.

## Decision and next work

**Keep the extended study deferred.** These results do not justify spending
the remaining full-study compute on the unchanged method yet.

First inspect saved malformed and valid-empty responses, the context/token
allocation, and hypothesis creation/retention on separate development cases.
Then validate a versioned correction, if one is warranted, under matched
settings across workflows. Preserve this pilot's results and use previously
untouched cases for confirmation after any outcome-informed changes. A
favorable rerun of these same 50 issues would be development evidence.

This is a small, one-seed exploratory study against unreviewed reference-patch
localization proxies. It does not measure repair success or human-adjudicated
root causes. Repository balancing changes the benchmark mixture, and these
results must remain separate from the earlier full-run report with its different
cohorts, workflows and seed averaging.

Evidence: [final comparison](../../experiments/pilot/results/analysis/report.md),
[per-case scores](../../experiments/pilot/results/analysis/scores.csv),
[coverage](../../experiments/pilot/results/analysis/completeness.json),
[independent verification](../../experiments/pilot/results/analysis/final-verification.json),
[retrieval controls](../../experiments/pilot/results/analysis/controls.json),
[final DeepSeek diagnostics](../../experiments/pilot/results/analysis/quality.json),
[frozen selection](../../experiments/pilot/results/pilot.json).
