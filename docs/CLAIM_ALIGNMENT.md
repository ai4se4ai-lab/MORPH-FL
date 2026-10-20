# Paper–implementation–evidence alignment

The Gemini transcript is useful for explaining the intended architecture. Its confident statements are not independent scientific evidence. Use [ALGORITHMS.md](ALGORITHMS.md) for executable definitions and the [empirical discussion](../experiments/baselines/results/research_questions.md) for measured findings. The proposal's central hypothesis remains open.

| Design wording or claim | Code and experimental reality | Defensible paper wording |
|---|---|---|
| “PPF solves reasoning fixation” | Reset/retention mechanics exist; no controlled wrong-lead recovery study | PPF is intended to address fixation; effectiveness remains to be tested |
| “Mathematically guarantees zero fact loss” | Tests/assertions and measured observation-ID retention; no proof of semantic sufficiency | Reset preserves recorded, provenance-checked observations under the implemented invariant |
| “Verified observations are verified causes” | Source/AST observations have limited predicate scope; static-only runs abstain causally | Observations support stated predicates, not whole causal explanations |
| “Strictly nonredundant, orthogonal hypotheses” | Greedy lexical/path distance; up to three retained, sometimes only one | Heuristic bounded portfolio encouraging diversity |
| “Graph edit distance / semantic embeddings” | 0.6 mechanism-term Jaccard distance + 0.4 path difference | Lexical/path distance; no graph-edit or learned semantic metric |
| “Expected entropy/information gain” | Alternative-ID count and hypothesis distance divided by heuristic cost | Cost-aware probe utility proxy; no calibrated expected-information objective |
| “Minimal causal slice preserving root cause” | Two-hop bidirectional neighborhood over resolved syntactic relations | Conservative dependency neighborhood; no sound causal/minimal slice guarantee |
| “Intersect with active hypotheses” | Not implemented; could remove connectors and alternatives | Expand around seeds and preserve independently rotating candidates |
| “Four independent agents run together” | One backend; four separate role dialogues scheduled sequentially | Four investigator roles; short runs invoke only behavioral and skeptical roles |
| “Calibrated confidence / knows when correct” | Confidence null; causal abstention on static-only evidence | Explicit uncertainty and evidence scope; calibration not evaluated |
| “Docker / SQLite / NetworkX / Pydantic / tree-sitter” | Apptainer registered procedures; files/JSONL; dataclasses; Python AST | Describe the actual stack; alternatives are optional future engineering choices |
| “Defects4J evaluation” | Export adapter exists; Java analyzer and curated issue inputs missing | Evaluation currently limited to selected Python SWE-bench Lite instances |
| “Thresholds validated across repositories” | Historical settings are design choices; optional normalized fraction and window sensitivity added later | Declare parameters, provenance, sensitivity and remaining calibration work |
| “Scale-invariant generalization” | Fractional metrics help normalization; reserves and round windows remain absolute | Budget-relative exploration is configurable; generalization is unestablished |
| “Significantly better accuracy/cost” | Small single-seed results mixed or unfavorable; no significance test claim | Report counts/costs and negative results; do not assert broad superiority |
| “Patch locations are validated root causes” | Production patch-change proxies, no independent human causal review | Patch-location proxy localization with explicit validity limitations |
| “Slurm COMPLETED proves successful method validation” | Nibi jobs completed but one step lacks a completion and one case lacks a valid hypothesis | Distinguish scheduler completion, step completeness and semantic inference validation |
| “All existing experiments test the revised policy” | Historical source frozen; alignment extension is separate | Attribute every result to its archived source and exact policy |

## Paper-ready method paragraph

MORPH-FL represents issue symptoms, repository structure, fault hypotheses and observations using linked typed records. A sequential role-based controller constructs bounded source/model views, requests hypotheses with explicit predictions, and evaluates permitted static or registered dynamic probes under a cumulative token/probe/time budget. A rolling-window policy monitors new observations, repeated investigations and a lexical/path diversity proxy. When its configured plateau and restart-affordability conditions hold, it clears role dialogues while retaining the external evidence store and a bounded hypothesis portfolio. The next role receives a newly constructed brief that preserves the distinction between source observations and unverified causal claims. The prototype does not estimate calibrated causal probabilities or optimize expected entropy reduction.

## Paper-ready experimental scope paragraph

We conducted a local exploratory study using quantized Qwen2.5-Coder 7B and Qwen3-Coder 30B through Ollama. Pinned Agentless and RGFL localization components were adapted to the same source snapshots and 16,000-token ceiling, with explicit stage/output/context restrictions. We report three original development issues, three reused pilot-test issues, and six additional prospectively selected issues from different repositories separately. A post-hoc context-sensitivity control increased the external baselines' tree allowance without changing the total budget. Ground truth comprises unreviewed production-file/function patch-change proxies. A separate eight-round, 48,000-token, one-development-issue diagnostic measures reset execution, retained observation IDs and resource use. Neither this design nor the two-round comparisons establish population-level superiority, calibrated uncertainty or causal recovery from fixation.

## Results and conclusions that the evidence supports

On the six fresh cases, MORPH-FL file Top-1 is 4/6 with 7B and 2/6 with 30B; strict function Top-1 is 2/6 for either model. Stateless summaries obtain 4/6 and 3/6 file hits, respectively, using fewer mean tokens. The larger-tree Agentless control obtains 3/6 and 5/6, and larger-tree RGFL obtains 4/6 with either model. The context controls are post-hoc results on reused cases, not a new independent validation set. All observations remain in the retention checks at measured reset events, but this does not establish better causal localization. The central accuracy/efficiency/fixation hypotheses remain unconfirmed.

A positive finding is implementation feasibility and auditability of the distinction between evidence memory and conversation memory. Negative findings include lower accuracy in some conditions, repeated probes after resets, higher token costs than a summary baseline, output-ranking inconsistencies and run variability despite nominal fixed seeds. These are research results, not reasons to omit conditions.

## Required evidence before stronger claims

| Research question | Evidence available | Evidence still needed |
|---|---|---|
| RQ1 accuracy/generalization | File/function Top-k, MRR, paired case counts, two local models, selected repositories | Larger repeated samples, reviewed causal labels, cross-layer/overlap strata, complete graph/embedding/agentic baselines, second ecosystem |
| RQ2 fixation/PPF mechanism | Actual reset events, retained IDs, probe/repetition logs, fixed/no-reset/summary diagnostic, later window sensitivity | Paired wrong-lead recovery, all component ablations, validated diversity/fixation measures, multiple cases and seeds |
| RQ3 efficiency/reliability | Actual tokens, static evidence scope, abstention behavior, recorded timings with differing boundaries | Matched end-to-end timing/tool costs, multiple budgets, dynamic discriminating evidence, calibration data and human causal judgments |

Do not describe the window-sensitivity experiment as hyperparameter calibration: it uses a previously studied development issue, does not select an optimum on a disjoint validation set, and is not a benchmark generalization test.


## Completed configurable-policy diagnostic

The subsequent six-cell study (two models × windows 3/4/5) is complete in [the policy report](../experiments/alignment/results/report.md). All runs obtain the patch-proxy file hit but none obtains a function Top-1 hit on this one development issue. All six recorded reset events preserve their observation IDs. The 7B runs reset once under each window; 30B resets twice, once and zero times for windows 3, 4, and 5. The 30B no-reset trajectory uses fewer tokens and produces more distinct probes than its window 3 trajectory. This establishes parameter sensitivity and operational record retention, not optimal thresholds, reduced fixation or a general accuracy benefit. Run variability and one seed prevent causal attribution of all trajectory differences to the window alone.
