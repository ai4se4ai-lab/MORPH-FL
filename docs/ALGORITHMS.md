# Executable MORPH-FL algorithm specification

This is the canonical method description for the prototype. A portable manuscript fragment containing the same five algorithms is in [paper/algorithms.tex](paper/algorithms.tex). It reconciles the research proposal and the supplied Gemini explanation with the code. The Gemini transcript is a design discussion, not a record of implementation or experimental findings. Numbers below are exposed design parameters, not statistically calibrated or universally optimal constants.

## Version boundary and evidence

The external-baseline study measures frozen source `29ec0345852c…` (MORPH-FL core `c8084ee01c71…`). Its reset window is 3, minimum rounds 4, repetition threshold 0.5, diversity threshold 0.5, zero new observations over the window, and a 256-token reserve. It has no 15% exploration gate. The exact archives are under `experiments/baselines/source-versions/` and `experiments/local/source-versions/`.

The subsequent alignment version exposes those thresholds through `SearchConfig`, the CLI's `--reset-policy` JSON, and recorded run settings. It adds per-round reset-decision diagnostics and an **optional** original-budget exploration fraction. Defaults preserve the measured decision rule; equivalence is tested. The separate development experiment in `experiments/alignment/protocol.json` uses fraction 0.15 and windows 3, 4 and 5 with both models. Its results must not be substituted for the frozen short-run benchmark results. A 15% gate remains an experimental setting, not an empirically validated generalization claim.

## Representations and implementation scope

| Layer | Executable representation | Current scope |
|---|---|---|
| M1 | `BehavioralModel` | Report, proposed expected/observed behavior, trigger, invariants and ambiguity; extracted claims remain conjectured |
| M2 | `SystemModel`, `SourceLocation`, `Relation` | Python AST symbols, syntactic calls/imports, local approximate def-use, source digests and unresolved edges; no sound interprocedural/control-flow analysis |
| M3 | `FaultHypothesis`, `Prediction` | Candidate source elements, proposed mechanisms, predictions, assumptions and evidence references; generated causal chains remain conjectures |
| M4 | `Probe`, `Evidence`, `Assessment`, `Budget` | Static checks and registered sandbox procedure interfaces, scoped verdicts, immutable observation identities and cumulative costs |

T4/T5 materialize and validate jointly generated hypothesis/prediction/probe proposals; they do not provide a separately verified general compiler from causal explanations to executable tests.

These are Python dataclasses and validation routines, not EMF/OCL models or Pydantic schemas. Storage uses content-addressed files and a hash-linked append-only JSONL audit, not SQLite/SQLAlchemy. Dynamic execution uses registered Apptainer procedures, not Docker. No graph-edit distance, embedding distance, Bayesian confidence estimator or entropy estimator is implemented. The measured comparisons use source-only evidence. The registered dynamic interface has unit/boundary coverage but has not been validated by a real benchmark-container execution in this study.

Investigators are role-separated dialogues using one shared model backend, scheduled sequentially: behavioral, skeptical, structural, dynamic. They are not four simultaneously running model processes. In a two-round experiment only the first two roles are invoked. Independent-agent ablations isolate their model/evidence views. Source observations can be physically reused without importing another investigator's speculative explanation.

## Algorithm 1 — Budgeted localization and evidence update

```text
INPUT: public report B, pre-fix source R@v, model L, configuration θ, budget C
1. M1 ← report model with unestablished expectations marked ambiguous          [T1]
2. M2 ← conservative, source-versioned Python analysis(R@v)                    [T2]
3. r ← BM25(B, source); S ← dependency_neighborhood(M2, first 5 paths in r)    [T3]
4. candidates ← first 20 paths of stable_unique(seed paths, r∩S, r)
5. Initialize external evidence E, hypothesis pools H, role dialogues A,
   physical-probe cache Q, scoped evidence references and cumulative budget C.
6. For t = 0,…,round_limit−1, while token/probe/wall limits permit:
7.     role ← θ.roles[t mod |θ.roles|]
8.     Select a bounded live portfolio from the role's permitted pool.
9.     Construct a fresh model view; attach up to 4 retrieved/rotating source
       windows, their retrieval ranks, typed relation excerpts and procedures.
10.    Send this view plus that role's retained dialogue to L; charge actual
       input/output tokens even if the generated response is invalid.
11.    For an accepted structured response, refine the scoped M1 behavior fields;
       validate proposed mechanisms, predictions, locations and probe plans. [T4,T5]
       Reject nonexistent files, out-of-range lines and non-visible paths.
12.    Order accepted probes with Algorithm 3.
13.    For each affordable probe: reuse Q's physical observation if present,
       otherwise execute the permitted procedure and verify source/provenance.
14.    Preserve observation identity in E; assess only its explicit predicate,
       attach a scoped supports/contradicts/inconclusive verdict, update H.    [T6]
15.    Measure new accessible observations, duplicate ratio, diversity and cost.
16.    Evaluate Algorithm 2; perform Algorithm 4 if the policy requests a reset.
17.    Stop on a limit or conservative registered-dynamic-support criterion.
18. Rank files by maximum live hypothesis score, breaking ties with original
    retrieval order; otherwise return retrieval order. Rank symbols from live
    hypotheses independently. Return observations, assessments, audit and costs.
19. Leave confidence null. With only static evidence, abstain from a causal
    conclusion while still returning explicitly unverified location rankings.
```

The candidate counts and source-window widths are configurable. The full-context, fixed-reset and summary ablations modify the loop's memory/policy settings. This implementation does not construct a complete, validated initial causal portfolio before the first model call. Final file and symbol rankings are independent; the measured Seaborn disagreement is documented in the results and has not been retrospectively repaired.

## Algorithm 2 — Observable plateau decision

Let `W` be the number of recent **completed valid investigation rounds**, not seconds, files or individual tool calls. For each round record `g_t` (new accessible non-blocked observations), `r_t` (proposed probes whose physical fingerprint was executed previously, divided by proposed-probe count), `d_t` (mean pairwise hypothesis distance), and `c_t` (actual input+output tokens). Duplicate probes proposed within a single new batch may be physically reused, but the recorded repetition metric checks the pre-round cache. Blocked probes do not count as evidence gain.

```text
INPUT: rolling history J, original token budget C0, remaining C,
       estimated restart cost ĉ, parameters W,n0,c0,ρ,τg,τr,τd
1. Wait until at least n0 rounds have completed and J contains W samples.
2. f ← (C0 − C) / C0                         // optional exploration fraction
3. ḡ ← Σ(g_t)/W; r̄ ← Σ(r_t)/W; d̄ ← Σ(d_t)/W; c ← Σ(c_t)
4. Record f,ḡ,r̄,d̄,c,c/max(1,Σg_t),ĉ for audit.
5. exploration_ready ← (f ≥ ρ)               // measured default ρ = 0
6. affordable ← C > ĉ + c0
7. reset ← exploration_ready AND affordable AND c ≥ c0
            AND ḡ ≤ τg AND (r̄ ≥ τr OR d̄ < τd)
8. Return reset and the measured diagnostics.
```

Defaults: `W=3`, `n0=4`, `c0=256`, `ρ=0`, `τg=0`, `τr=0.5`, `τd=0.5`; `ĉ=max(c0, latest_round_tokens//2)`. The reserve is a heuristic, not a prediction of exact restart cost. The optional fractional gate uses the **original** token budget even after resets; it does not replenish the budget. It is scale-normalized, but the complete policy includes absolute reserves and round counts and is not claimed to be globally scale-invariant. Tokens-per-new-observation is diagnostic; it is not currently an additional trigger term. Threshold calibration on disjoint repositories remains outstanding.

## Algorithm 3 — Probe and portfolio utility heuristics

For hypotheses `h_i,h_j`, tokenize their mechanism descriptions into lowercase alphabetic terms of length ≥3. Define

`D(i,j) = 0.6 × (1 − |terms_i ∩ terms_j| / max(1, |terms_i ∪ terms_j|)) + 0.4 × I[path_i ≠ path_j]`.

This is a bounded lexical/path heuristic. It is neither graph-edit distance nor a guarantee of semantically independent explanations.

```text
INPUT: proposed probes P, active hypotheses H, previously handled probe IDs V
1. Remove already handled probe IDs from P for a shared investigation.
2. For each p associated with h:
       a ← number of distinct recorded alternative hypothesis IDs
       d ← sum of D(h,h′) over other active hypotheses
       utility(p) ← reliability_weight(p) × (max(1,a)+d) / max(0.001,cost(p))
3. Order by descending utility with stable probe-ID ties.
4. At execution, independently check physical fingerprint(kind,path,parameters),
   source version, procedure permission and remaining probe/wall limits.
5. Reuse an existing observation without charging a second physical execution;
   assess that observation separately against each hypothesis's prediction.
```

Reliability weights and estimated costs are hand-specified heuristics. They must not be presented as calibrated probabilities or expected entropy reduction. Alternative predictions use differences in declared predicates/expected outcomes; the system does not estimate joint outcome distributions or optimal experimental designs.

For portfolio selection, begin with hypotheses in descending score/stable-ID order and greedily maximize `score(h) + min D(h,selected)` until `k` are selected or candidates run out. The first candidate uses distance 1. Default `k=3` is an upper bound; the implementation may retain only one candidate. Two to four valid, orthogonal hypotheses are not guaranteed.

## Algorithm 4 — Evidence-preserving model/context reset

```text
INPUT: dialogues A, scoped live pools H, external observations E, budget C
1. Record the current observation-ID set O; prior prompts/responses already
   have content-addressed artifacts in the append-only audit.
2. For each permitted scope, select at most k live hypotheses with Algorithm 3;
   retain their predictions, versioned locations and support/contradiction links.
   A context-only ablation instead keeps all live models.
3. Clear role dialogues and advance their session generation.
4. Clear the rolling plateau window. Do not reset total budget or round count.
5. Assert that E's observation-ID set is still O; retain the physical-probe cache
   and evidence references. Log the retained portfolio and reset diagnostics.
6. On the next round, derive a role-specific brief from M1, selected hypotheses,
   available observations, open predictions and remaining C.                  [T7]
7. Mark static source facts separately from observed dynamic predictions;
   keep unsupported mechanisms explicitly unverified.
```

This invariant says that the reset operation does not delete recorded observations. It does not prove the observations are causally relevant, that every useful insight is represented, or that fresh contexts fit any arbitrary context budget. Audit files are tamper-evident under their hash checks; they are not a mathematical proof of zero semantic information loss. Unverified hypotheses are deliberately retained as hypotheses, not all purged as the Gemini summary suggests.

## Algorithm 5 — Conservative dependency-neighborhood composition

```text
INPUT: source-versioned typed model M2, report-derived seed paths S0, hops b
1. S ← S0
2. Repeat b times (default b=2):
3.     For each relation whose resolution is not unresolved:
4.         Let u,v be its endpoint file paths.
5.         If u∈S or v∈S, add u and v to an expansion set.
6.     S ← S ∪ expansion set
7. Return existing source paths, preserving seed order then sorted new paths.
```

This expansion can retain upstream/downstream candidates connected by known dependencies. It is not a minimal semantic slice, sound causal slice, program-dependence graph or bounded-depth proof of root-cause preservation. The Gemini sketch's intersection with already active hypothesis locations is intentionally **not adopted**: it could remove connector nodes and unexplored alternatives. New hypotheses continue to receive rotating source candidates outside the current leader.

## Experimental interpretation

The historical two-round comparison tests short-budget localization, not the benefits of long-horizon resetting or all four investigator roles. The eight-round one-case diagnostic tests reset execution, record retention and costs; it is not an incorrect-lead recovery study. Window sensitivity uses a known development issue and has no test-set generalization interpretation. No experiment here establishes calibrated confidence, causal-chain validity, Java/Defects4J performance or superiority over a complete state-of-the-art system. See the empirical report and claim-alignment matrix before drafting conclusions.

## Ablation semantics

`no_forgetting` keeps each role dialogue; `fixed_reset` clears it every three rounds by default; `context_only` clears dialogues but retains all live model hypotheses; `single_hypothesis` limits the retained portfolio to one; `no_skeptic` changes the role schedule; `independent_agents` isolates the role's model/evidence views; `one_agent` repeatedly invokes the structural role. These are sequential scheduling/memory conditions, not changes in the number of GPUs or model replicas.

`no_mde` removes explicit model/relations from **agent-visible memory** and supplies an evidence-text summary. `stateless_summary` additionally omits prior dialogue on every call. Both still reuse typed source validation, probe execution and internal scoring; they are not a complete deletion of every M1–M4 implementation object. Paper ablation names must state this boundary. A fully independent unstructured tool-using agent remains a separate required comparator.


The separate configurable-policy diagnostic has completed: [results and reset decisions](../experiments/alignment/results/report.md). Its six model/window conditions retain recorded observations, but none reaches the proxy target function first on the single development issue. These measurements support operational sensitivity and retention checks, not a benefit of frequent resets or a validated parameter optimum.
