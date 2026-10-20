# MORPH-FL implementation

The source implements the four conceptual algorithms and seven transformations from the proposal for **Python repositories**. The implementation is executable, but its accuracy and scientific claims still require benchmark experiments. Static analysis and information-utility estimates are conservative approximations. Adding packages does not establish empirical effectiveness.

## Package boundaries

```text
src/morph_fl/
  domain/              M1–M4 records, epistemic states, provenance, budgets
  program_analysis/    Python AST structure, call/import links, local def-use, BM25
  transformations/     T1/T3–T7 model transformations (T2 is program_analysis)
  investigation/       probe execution, container procedures, verified evidence ledger
  search/              policy configuration, utility, diversity, plateau, controller
  agents/              investigator roles and independent working contexts
  inference/           backend protocol and offline GPU Transformers adapter
  datasets/            public case contracts, SWE-bench, evaluator-only patch labels
  evaluation/          file/function/set metrics, uncertainty statistics, external imports
  infrastructure/      content-addressed artifacts and hash-linked audit log
  application.py       durable case runs, resume validation, evaluator services
  cli.py               argument parsing and service dispatch
```

The original `engine`, `backend`, `models`, `retrieval`, `benchmark`, `analysis` and `external` module paths remain small compatibility facades. Legacy source-quote types live in `domain/legacy.py`; the controller uses the new metamodels. `tests/unit/` checks algorithmic invariants; `tests/integration/` checks the full scoring/collection plumbing. Optional dependencies keep base imports independent of model libraries and GPUs. CI checks Python 3.11/3.12, formatting, lint, tests, Slurm configuration and package builds.

## Proposal-to-code traceability

| Proposal | Implementation | Operational semantics |
|---|---|---|
| M1 behavioral model / T1 | `domain.BehavioralModel`, `transformations.complaint_to_contract` | Separates report, expected/observed behavior, invariant and ambiguity. Extracted behavior remains conjectured until independently reproduced. |
| M2 structural model / T2 | `program_analysis.analyze_python` | Versioned source symbols, import/call/read/write/local def-use relations. Unresolved dispatch remains explicitly unresolved. |
| T3 composition/slicing | `transformations.compose_slice` | Bidirectional bounded dependency neighborhood expands lexical seeds toward possible upstream causes. This is a structural slice, not a sound interprocedural causal slice. |
| M3 hypotheses / T4 | `transformations.synthesize` | Source-bound mechanism, predictions, assumptions and conjectured causal chain. Invalid paths, predictions and source lines fail validation. |
| M4 investigations / T5 | `hypothesis_to_probe`, `search.rank_probes`, `investigation.ProbeExecutor` | Source quotes, AST predicates, tests, traces and counterfactual procedures. Probes are ranked by conservative discrimination/diversity/reliability per estimated cost. |
| T6 evidence update | `transformations.evidence_update` | Supporting, contradicting or inconclusive outcomes update hypotheses under recorded assumptions; static presence and runtime evidence have different scopes/weights. |
| T7 fresh context | `transformations.fresh_context`, `agents.InvestigatorSessions` | Rebuilds role briefs from versioned hypotheses, observations, unresolved questions and remaining budget. Old dialogues are excluded. |
| Algorithm 1 | AST analysis → contract → dependency slice → synthesis | Constructs linked behavioral/system/fault models with explicit provenance. |
| Algorithm 2 | Utility-ranked probes → executor → ledger → assessment | Independently checks observations; skips repeated probes and enforces probe/wall budgets. |
| Algorithm 3 | `PlateauMonitor`, `select_portfolio`, session `forget` | Plateau combines novel evidence, repetition, mechanism diversity, cost and minimum exploration; restart must remain affordable. Retains a support/diversity portfolio and every observed fact. |
| Algorithm 4 | `search.LocalizationController.run` | Coordinates investigators, contracts, evidence, budgets, stopping, abstention and file/function ranking. |

The portfolio uses token-set mechanism distance plus source diversity. This is a reproducible heuristic, not a semantic equivalence oracle. Probe reliability, costs and support weights are heuristic configuration choices requiring sensitivity studies. Repeated quotations cannot become independent evidence through agent agreement.

## Investigator and forgetting semantics

Behavioral, structural, dynamic and skeptical investigators have separate dialogues. Shared knowledge consists of typed hypotheses and verified observations. In `independent_agents`, each role receives only its own hypotheses and observations; the final rank aggregates independent results without treating agreement as new empirical evidence.

Forgetting clears working sessions, retains immutable observations/artifacts and incurred budgets, and selects a diverse portfolio. `context_only` retains all models while clearing contexts. `single_hypothesis` keeps one model. `no_forgetting`, `fixed_reset`, `no_mde`, `no_probes`, `no_skeptic`, `independent_agents`, `one_agent`, `stateless_summary`, `rerank`, `bm25` and `graph` are explicit policy conditions, not aliases for the full method. `no_mde` uses textual evidence memory instead of typed model context; the shared execution/output validation remains in place to keep tool permissions comparable.

## Dynamic investigations

Without `--sandbox`, dynamic proposals produce an explicit blocked/inconclusive observation; static probes still run. Dynamic procedures require a JSON configuration containing an absolute Apptainer image path, its SHA-256, a mapping from procedure IDs to argv lists, and a positive timeout. The model can select these IDs, not arbitrary host commands.

The executor checks the image hash, removes inherited environment, disables container networking, binds source read-only at `/workspace` and binds temporary probe output at `/results`. A trusted inner launcher records completion separately from Apptainer startup. A startup error or timeout is inconclusive, never a reproduced failure. Registered procedures may run supplied `test_code` from `/results/generated_probe.py`; generated code executes only inside the container. Tests and traces use the isolated procedure interface. Counterfactual probes require two registered procedures (baseline and intervention), run both independently and preserve both outcomes; the predicate compares their results. Every procedure captures command, output, source version, image digest and assumptions.

Apptainer images must contain Python 3 and the project's required test tools/dependencies. An operating-system container is not a proof of isolation against a hostile kernel exploit. The real cluster/container path has not yet been smoke-tested; tests check command construction, completion semantics, provenance and failure handling with simulated process boundaries.

## Evidence, stopping and uncertainty

Observations are content-addressed, source-versioned and independently checked against stored artifacts before entering the ledger. Overwriting an existing fact is rejected. A hash-linked append-only audit records proposals, findings, assessments, resets and costs. It is tamper-evident, not protected from filesystem administrators. Same procedure/source/result is one fact even when multiple hypotheses refer to it.

A source quote proves presence or absence at a specific line. An AST query proves a static structural predicate. Neither establishes runtime cause. Runtime outcomes support/contradict only their explicit predictions under the registered procedure assumptions. Generic failing tests alone do not validate an entire causal chain.

The controller stops on token/probe/wall limits, round limits, or multiple distinct registered dynamic procedures supporting a hypothesis with declared assumptions and no contradiction. Causal abstention remains true when only static evidence is available. Rankings are still returned with uncertainty. Confidence is null unless a separate calibrated estimator is introduced; internal support scores are not probabilities.

## Evaluation and reproducibility

SWE-bench preparation pins dataset revision and buggy source commit, uses shallow fetches and exports snapshots without Git history. Public case validation rejects gold patches, post-fix tests, hints and solution fields. The local backend has no repository browsing tool outside supplied source/probe views. Evaluator-only patch parsing maps old changed lines to production files and qualified Python functions, including deleted source files where recoverable. These remain **unreviewed change-location proxies**, not validated root-cause labels.

Metrics include Top-1/5/10, MRR, recall@10, multi-location set precision/recall/F1, function metrics, selective accuracy, Brier/ECE for supplied probabilities and measured accuracy-cost AUC. Raw findings include token/time/probe costs, duplication, hypothesis switching, diversity and reset traces. Cluster bootstrap intervals and cluster sign-flip/Holm helpers are available; a statistically defensible study still needs paired seeds, enough repositories and a declared comparison family. Human agreement on causal explanations requires actual annotators.

Each completed case is fsynced to a separate cell-owned JSONL file. Resume rejects changed settings/revision/report, repairs only a truncated final record and skips completed cases. Per-case inference seeds derive from seed plus case ID, so ordering/requeues do not change case randomness. An interrupted case restarts with a new budget; its previous failed attempt remains in the append-only audit and must be included when reporting total cluster expenditure. Exact within-case model state is not checkpointed.

## Scope and remaining validation

The algorithmic core and policy conditions above are implemented and locally tested. Sound interprocedural data flow, arbitrary-language analysis, automatic calibration, external baseline reproduction, validated benchmark labels and human causal ratings are not claimed. The Defects4J export adapter requires curated issue reports and a Java analyzer before localization; the built-in analyzer is Python. No real-model benchmark or completed dynamic-container run is implied by unit tests. The queued original Nibi smoke run uses the earlier source version and cannot validate this expanded source tree.

## DGXSpark corrections found through real-model runs

The local Ollama adapter supports the installed verified Qwen coder models through raw ChatML generation and structured outputs. It rejects cloud routes, pins model/tokenizer provenance and checks server-reported token use against preflight accounting. It is an optional backend; model libraries remain lazy imports.

Development traces exposed excessive repeated graph provenance in prompts, stale stack-trace line offsets, inability to revisit a prior hypothesis, duplicate physical probes counted under different hypothesis IDs, and static support incorrectly closing an unresolved causal question in the agent brief. The corrected controller uses compact typed relation views, resolves named trace functions against the pre-fix AST, reserves source slots for live explanations and caches physical probes independently of hypothesis wording. Reused observations remain one fact. Independent-agent conditions also isolate their extracted behavior models.

Fresh briefs explicitly distinguish `source_observations` from `verified_prediction_observations`; source-only evidence leaves the causal prediction unresolved. The skeptical investigator runs second so a short budget can still challenge an initial explanation. Full metamodel/evidence records remain in the external audit and store; compact presentation does not rewrite their epistemic status.

The source used for held-out evaluation is locked by SHA-256 in `experiments/local/protocol.json`. All development attempts, including regressions, remain in the local pilot results. Small two-round pilots measure plumbing, localization and context efficiency; they do not exercise adaptive forgetting or establish statistical improvement. Published Agentless release artifacts form a separately labeled unmatched reference. See the local report for actual measurements rather than assuming these corrections improve every metric.

## Upstream localization adapters

`baselines/local.py` contains optional local Agentless/RGFL component adaptations. The upstream-baseline study used the frozen `c8084ee0...` MORPH-FL core. `baselines/vendor/` preserves pinned upstream prompts, the Agentless source compressor, file hashes and MIT notices. The added adapter supports free-text decoding while reusing local model verification and token accounting; it never evaluates generated Python or accesses evaluator labels. Exact adaptation limits and fresh/diagnostic protocols are documented in `experiments/baselines/README.md`.


## Configurable reset policy and paper specification

The subsequent alignment extension exposes reset-window, minimum valid rounds, token reserve, optional original-budget exploration fraction, evidence-gain rate, repetition and diversity thresholds. The default decisions are tested against the historical rule. The controller records every adaptive decision and its measured rates, remaining-budget fraction and restart-affordability estimate. A reset clears the window/dialogues while preserving the original budget and external evidence. Parameters are serialized into configuration/audit records; CLI `--reset-policy` accepts a JSON object containing only the declared reset fields. See [the five executable algorithms](ALGORITHMS.md) and [paper claim alignment](CLAIM_ALIGNMENT.md). The separate `experiments/alignment/` sensitivity study does not retrospectively change old results.
