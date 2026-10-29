# Revision around the completed two-model study

Date: 28 October 2026.

## Scope decision

The user identified the unfinished larger experiment as a central credibility problem. The revision changes the evidence base, rather than relabeling that experiment. The manuscript now reports only the fixed 50-issue/12-repository study with two checkpoints, four workflows and one seed: all 400 investigation keys and 100 retrieval-control records.

The 139/219-issue rates, three-seed tables, 7–9pp effects, restricted adapter results, incomplete-track inventories, ten-cluster statistics and 50-contrast confirmatory plan have left the manuscript. Their original sources and the pre-revision manuscript are preserved. No missing runs were manufactured and no known defect was hidden.

The study's original directory name remains `pilot` for provenance. Reader-facing prose describes its actual fixed design and completed collection. Its exploratory interpretation, 132 reused Qwen predictions, single seed, patch proxies and bundled/defective prompt contrast are retained because they materially affect the conclusions.

## Three independent critical reviews

Each agent produced an initial plan review and a rewritten-draft review:

- [Methods initial](reviews/bounded-methods-initial.md) / [final](reviews/bounded-methods-final.md).
- [Empirical initial](reviews/bounded-empirical-initial.md) / [final](reviews/bounded-empirical-final.md).
- [Editorial initial](reviews/bounded-editorial-initial.md) / [final](reviews/bounded-editorial-final.md).

These are AI-generated assessments, not journal peer review. Reviewers found the completed-only framing coherent and materially stronger, while retaining causal, generalization and release limitations.

## Feedback integrated

| Finding | Implemented change |
|---|---|
| Completeness must refer to an actual bounded design | Abstract, introduction, methods, results and conclusion consistently use 50 issues, two models, four workflows, one seed and 400+100 records. |
| Old snapshot effects cannot be carried into the new sample | Removed historical metrics and rebuilt all six numerical tables from the completed study inputs. |
| “Resets are rare” is wrong for DeepSeek | Added exact exposure: 8/50 Qwen and 29/50 DeepSeek adaptive runs, versus 50/50 and 45/50 fixed-reset runs. |
| Equal means can hide different paired outcomes | Added exact discordant Top-1 counts; full/continuous/fixed have zero discordance, while observation-only gains/loses 5/1 Qwen and 4/4 DeepSeek hits. Rankings are not declared identical. |
| File accuracy hides output collapse | Added final pools, paired pool changes and DeepSeek response/hypothesis event table. Availability is not causal correctness. |
| Continuous Qwen tokens rounded incorrectly in prose | Corrected to 27,573 from the actual 27,573.48 mean. |
| Bootstrap bounds lacked source binding | Parse both bounds and effect from saved report; add report.md to input digests. Explain [0,0] is fixed-sample zero discordance, not population precision/equivalence. |
| Runtime detail missing | Added 1,536-token per-generation ceiling. |
| Shared excerpts could imply identical source exposure | Specify common construction rules and acknowledge hypothesis-dependent downstream source visibility. |
| Known defect and reused data remain material | Retain explicit defect, post hoc/reuse, single-seed and proxy-label disclosures in relevant scientific sections. |
| Historical truncated export is no longer an input | Keep that failure in historical records, outside the current study audit; do not claim it has been repaired. |
| Main file was too tightly coupled to pasted figures | Split current evaluation into sections and deterministic generated tables; archive includes both directories. |

## Analysis and validation

`scripts/analyze_completed_study.mjs` checks complete keys, selection, eligibility, saved aggregates, controls, resource means, reset exposure, paired hits/pools and table reconstruction. It generates six LaTeX inputs under `generated/` only when requested with `--write`, and writes `validation/completed-study-audit.json`. The original experiment files are unchanged.

Added reset-exposure and paired-pool analyses are descriptive reanalyses of existing scores, explicitly identified as such. No new model inference, corrected-runtime accuracy, raw signature revalidation, confirmatory test or acceptance decision is claimed.

Current unresolved work is in [AUTHOR_ACTIONS.md](AUTHOR_ACTIONS.md). The earlier five-phase record and reviewer reports remain historical records of the previous manuscript, superseded in scope by this document.

