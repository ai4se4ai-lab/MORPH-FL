# Comparison protocol and literature

Two upstream component adaptations have now been implemented and locally evaluated; other systems remain literature candidates. Checked against primary sources on 2026-10-19. Repair success rates must never be compared numerically with file-localization accuracy.

| System | Primary source | Relevant component | Integration status |
|---|---|---|---|
| Agentless | https://github.com/OpenAutoCoder/Agentless | Hierarchical file/function localization; SWE-bench artifacts | Pinned upstream prompts/compressor adapted to local 7B/30B; results and deviations in experiments/baselines. Published GPT-4o artifacts remain a separate unmatched reference |
| AutoFL | https://github.com/coinse/autofl | Explainable, tool-driven localization from failing tests | Requires its test/coverage setup and matched-tool experimental track; not run |
| AgentFL | https://arxiv.org/abs/2403.16362 | Project-level multi-agent localization | Candidate Java/Defects4J track; not implemented here |
| RGFL (2026) | https://arxiv.org/abs/2601.18044 | Reasoning-guided localization evaluated against Agentless/OpenHands | Pinned GitHub reasoning/ranking prompts adapted to local 7B/30B with constrained candidate coverage; full embedding pipeline not reproduced |

The internal `rerank`, `graph`, `stateless_summary` and reset variants are controlled prototype baselines. They are not reproductions of Agentless, AutoFL, AgentFL or RGFL. No exhaustive state-of-the-art ranking has been established.

## External predictions

Use one JSONL row per case, with `instance_id`, ordered `ranking` (repository-relative paths), `repo`, `revision`, `variant`, `seed`, `input_tokens`, `output_tokens`, `seconds`, `resets`, `duplicate_probes`, `abstained`. Unknown costs must be null, never zero. Store the upstream commit, model revision, original artifact checksum and run settings in a sidecar manifest. The scorer checks revision alignment before scoring.

`python -m morph_fl.cli import-agentless --input raw.jsonl --cases cases.jsonl --out predictions.jsonl`

Agentless `found_files` output is accepted. Published predictions form an **unmatched artifact comparison** unless the same model, source scope, tools, case subset, seeds and budgets are independently established. Do not include unmatched artifacts in the paired matched-budget result table. A model change or tool restriction is a reconfiguration, not an exact reproduction.

## Labels and selection

The default SWE-bench Lite labels are production Python files touched by the reference patch. They are explicitly unreviewed proxies. Deleted files and non-Python files need separate handling. Review each included fix for root cause, unrelated edits and refactoring; retain exclusions with reasons. Function labels require inspecting changed pre-fix AST ranges and manual review; current scoring includes file and function patch proxies. Never present patch-touch recall as validated causal localization.

No gold patch, post-fix tests, hints or solution discussions enter model context. Model pretraining contamination remains possible for these public benchmarks.

## Local measured controls and published reference

The DGXSpark protocol and all attempted development versions are in `experiments/local/`. Controlled rerank/stateless/no-forgetting comparisons use the same local model, token cap and tools as MORPH-FL. Published [Agentless v1.5.0 release artifacts](https://github.com/OpenAutoCoder/Agentless/releases/tag/v1.5.0) are also scored in `experiments/local/results/agentless_reference/`, with archive SHA-256, upstream GPT-4o settings and coverage. Both file-level and combined retrieval/localization predictions cover the three chosen test instances. These are supplementary unmatched artifact references, not same-model or same-budget reproductions; upstream source hashes have not been independently revalidated. They are never pooled into the matched local-model table.

## Executed same-model adaptations

See [protocol and exact deviations](../experiments/baselines/README.md), [measurements](../experiments/baselines/results/report.md), and [research-question discussion](../experiments/baselines/results/research_questions.md). Neither adaptation is a claim to reproduce the published system at its original model/context budget. Source revisions, licenses, truncations and failed/empty predictions are preserved.

Additional relevant structure-aware candidates are [LocAgent](https://github.com/gersteinlab/LocAgent) and [ARISE](https://github.com/FARD-Lab/ARISE); neither has been executed here. Their graph navigation/data-flow tooling is especially relevant to the structural part of MORPH-FL. This study is a targeted comparison, not an exhaustive state-of-the-art leaderboard.
