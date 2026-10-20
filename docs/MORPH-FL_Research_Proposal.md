# MORPH-FL: Model-Driven Hypothesis Evolution with Strategic Forgetting for Bug Localization

**Research concept note — October 2026**  
**Intended venues:** IEEE Transactions on Software Engineering (TSE), ACM Transactions on Software Engineering and Methodology (TOSEM), ICSE Research Track  
**Status:** Research proposal with an implemented Python prototype and exploratory local measurements; the central effectiveness, fixation-recovery and efficiency hypotheses remain unconfirmed.

**Implementation and evidence:** The executable five-algorithm specification is in [ALGORITHMS.md](ALGORITHMS.md), the design-claim audit is in [CLAIM_ALIGNMENT.md](CLAIM_ALIGNMENT.md), and measured answers to RQ1–RQ3 are in the [empirical discussion](../experiments/baselines/results/research_questions.md). These documents distinguish frozen benchmark code from later policy-configuration experiments. The conceptual examples below are illustrative, not measured causal diagnoses.

> **One-sentence idea:** Instead of asking AI agents to keep reading code until they guess the buggy file, represent their competing explanations as explicit *models*, transform those models into testable investigations, and strategically restart agents when reasoning stagnates—retaining verified evidence but forgetting unproductive conversational history.

## 1. Inspiration and the new research question

The supplied paper, **“Scaling Discovery Requires Forgetting”** by Shangyin Tan and colleagues, studies agents that repeatedly propose and evaluate solutions. Its principal finding is that continuing long agent sessions—even with multiple communicating agents—can make search increasingly conservative. The authors periodically discard the agents' sessions and candidate histories and restart a team from its best candidate. They report improved search performance in four *optimization and automated discovery* tasks.

**What the source establishes:** In those particular tasks, a useful candidate and a reliable score exist, allowing the system to preserve the best solution while forgetting search history. This is *not* evidence that the technique already improves bug localization.

**What MORPH-FL hypothesizes:** Bug localization has a related but harder phenomenon: an investigator can latch onto an early suspected file, then reinterpret every new clue to support that suspicion. Unlike optimization, however, there may be no trustworthy scalar score for a hypothesis. Therefore, localization needs a **structured, evidence-aware replacement for “keep the best candidate.”** Model-driven engineering (MDE) supplies this replacement.

### The proposed central research question

**Can model transformations and evidence-preserving strategic forgetting jointly improve the accuracy, efficiency, and robustness of AI-powered bug localization by making competing fault explanations executable and preventing long-horizon reasoning fixation?**

This paper would make a specific conceptual move:

> **The unit of AI search should be a *testable fault hypothesis model*, not an ever-growing chat history or an unstructured list of suspicious files.**

## 2. Three critical research problems

These are **research hypotheses about important limitations**, not a claim that every current method suffers from them. Their prevalence and severity must be checked empirically against recent peer-reviewed baselines.

| Problem | Typical failure mode | MORPH-FL response | What would demonstrate success? |
|---|---|---|---|
| **P1. Hypothesis fixation and loss of exploration diversity** | An agent initially suspects the API handler and keeps inspecting it after contrary evidence appears; several communicating agents converge on the same wrong file. | Independently represented hypotheses, measured diversity and progress, **selective model-preserving forgetting**, and relaunch from multiple credible alternatives. | Higher Top-k localization accuracy and recovery rate following an incorrect initial lead, at equal cost. |
| **P2. Semantic gap between symptoms and root causes** | A stack trace ends in a UI/controller file, while the fault lies in a persistence or configuration rule elsewhere. Retrieval by lexical or embedding similarity overweights the visible symptom. | **MDE transformations** from report → behavioral expectations → architectural/dependency model → causal fault model → testable investigation plan. | More precise root-cause localization, especially on multi-file, cross-layer and low-lexical-overlap bugs. |
| **P3. Expensive and weakly validated multi-step reasoning** | Agents repeatedly reread code or duplicate one another's work; confident narratives are not backed by tests or discriminating evidence. | A **budgeted, evidence-scored exploration process**, reusable model-level evidence, independent verifier, and stopping/abstention policies. | Better accuracy per token/dollar/time, higher evidence coverage, and better-calibrated rankings. |

### Why these problems belong together

They reinforce each other. A weak representation of the system makes early guesses more likely. Accumulating those guesses in a long conversation encourages fixation. Additional calls may then intensify the fixation instead of providing new evidence. MORPH-FL addresses the **representation**, **search dynamics**, and **verification/cost control** together—but should evaluate each component separately to show whether the combination is truly useful.

## 3. A simple running example

Imagine a web application with a checkout feature. A user reports:

> "I apply a 10% discount coupon to my shopping cart. The checkout screen shows the discounted total correctly, but after I pay, my order history shows the full price."

Suppose the simplified repository contains:

```text
shop/
  ui/CheckoutPage.tsx
  api/CheckoutController.ts
  services/PricingService.ts
  services/OrderService.ts
  persistence/OrderRepository.ts
  models/Order.ts
  tests/checkout-discount.test.ts
```

The hypothetical bug is in `OrderService.ts`, which persists the undiscounted `subtotal` rather than the discounted `payableTotal`:

```ts
// Simplified example, deliberately buggy
const payableTotal = pricingService.applyCoupon(cart, coupon);
orderRepository.save({
  items: cart.items,
  total: cart.subtotal  // BUG: should be payableTotal
});
```

The user sees the right amount at checkout because `PricingService.ts` computes it correctly. `CheckoutPage.tsx` is the visible symptom site; `OrderService.ts` is the fault site. A retrieval-heavy agent might focus on the UI and pricing files because they share many words with the bug report.

### Step A — Transform the human report into a behavioral model

Instead of immediately guessing a file, MORPH-FL extracts **expected and observed behavior**:

```yaml
BugReportModel:
  trigger: customer applies a valid discount coupon and pays
  expected:
    payable_total: 90.00
    stored_order_total: 90.00
  observed:
    payable_total: 90.00
    stored_order_total: 100.00
  violated_invariant: stored_order_total == payable_total
  provenance: user bug report
  status: hypothesized_until_reproduced
```

The numerical values are illustrative; actual systems must extract them from evidence or generate them as an explicitly labeled example. The key output is not the YAML syntax: it is a **machine-processable behavioral contract** separating the symptom from the suspected cause.

### Step B — Transform repository code into an architectural model

A program-analysis pass (AST, call graph, data-flow, type information, and available runtime traces) produces a model such as:

```text
CheckoutPage
     | displays
     v
CheckoutController ----> PricingService
     |                         |
     v                         | computes payableTotal
OrderService <-----------------+
     |
     | passes total to save(...)
     v
OrderRepository ---> stored Order.total
```

In a real system, edges must be **typed and evidence-linked**: a call edge, a def-use/data-flow edge, and a conjectured causal edge are not interchangeable. The graph can be incomplete or imprecise; the system should record this uncertainty rather than present all edges as facts.

### Step C — Generate multiple fault hypothesis models

The agents receive *different explanatory models*, not copies of the same long conversation:

| Hypothesis | Candidate fault | Predicted observation | Discriminating investigation |
|---|---|---|---|
| **H1** | `CheckoutPage.tsx` displays the wrong value. | The displayed checkout value differs from the value sent by the API. | Compare rendered and API totals. |
| **H2** | `PricingService.ts` calculates the discount incorrectly. | The service output is 100 rather than 90. | Unit-test the coupon calculation. |
| **H3** | `OrderService.ts` passes the wrong value for persistence. | Pricing returns 90, but the argument to `save` is 100. | Trace the value flowing into `OrderRepository.save`. |
| **H4** | `OrderRepository.ts` overwrites a correct total. | `save` receives 90, but persisted data becomes 100. | Compare save input to stored row. |

These models are **falsifiable**. For example, if a test shows that `PricingService` returns 90 and the repository receives 100, H2 weakens and H3 strengthens. The investigation need not trust an agent's fluent explanation.

### Step D — The first investigation may go wrong

Suppose three agents initially concentrate on H1 and H2. They keep reading UI and pricing code, but their new investigations produce little information. A conventional agent may keep the entire preceding conversation and become increasingly attached to these leads.

MORPH-FL instead records what was *actually learned*:

```yaml
EvidenceSnapshot:
  confirmed:
    - id: E1
      observation: PricingService returns 90 for the reproduced input
      source: tests/pricing-coupon.test.ts::valid_coupon
    - id: E2
      observation: OrderRepository.save receives total 100
      source: captured test instrumentation
  still_open:
    - Does OrderService substitute cart.subtotal for payableTotal?
  hypotheses:
    H1: weakened
    H2: contradicted_under_this_reproduction
    H3: strengthened
    H4: weakened_under_this_reproduction
  best_next_probe: inspect value flow into OrderRepository.save
```

This snapshot is an example of the *target representation*, not evidence from a real execution.

### Step E — Strategically forget and restart

If exploration stagnates, the system starts fresh agents without their earlier dialogue, guesses, or redundant file-reading traces. New agents receive only:

1. The original report and reproducible setup.
2. The relevant repository/model references.
3. A compact snapshot of verified evidence and its provenance.
4. A **small portfolio of live competing hypotheses**, including the strongest one and a genuinely different alternative.
5. Remaining budget and permitted tool operations.

One fresh agent explores the data flow from `PricingService` into `OrderService`, while another tries to disprove H3 by checking the repository's input and behavior. Both work with the same invariant but pursue independent verification paths.

**Crucially, “forget” does not delete source code, test results, or the externally auditable evidence store.** It deletes *agent working context and untrusted search baggage*. The distinction matters: discarding validated evidence would make fault localization less dependable.

### Step F — Produce a localized result with a causal explanation

An illustrative final report looks like:

```text
Top-ranked location: services/OrderService.ts
Likely fault: incorrect argument for persisted order total

Causal explanation:
  1. PricingService computes discounted payableTotal = 90.
  2. OrderService persists cart.subtotal = 100.
  3. OrderRepository stores 100, explaining order-history discrepancy.

Supporting evidence:
  - Reproducing checkout test
  - Captured argument to OrderRepository.save
  - Static def-use path connecting cart.subtotal to saved total

Confidence: supported by independent static and dynamic checks
Remaining uncertainty: whether other code paths have the same defect
```

The target output is the **root-cause location with an inspectable chain of evidence**, rather than merely a plausible ranked file list. If the system cannot distinguish hypotheses, it should return an uncertainty statement instead of fabricating confidence.

## 4. What MDE contributes beyond code graphs and RAG

Merely storing files in a knowledge graph or using an LLM to summarize code is **not yet a substantive MDE contribution**. MORPH-FL needs explicit *metamodels*, *typed relations*, *transformations*, and *well-defined consistency checks*.

### Four linked model layers

**M1 — Symptom and behavioral model.** Represents user-visible symptoms, triggers, preconditions, expected/observed outcomes, and violated invariants. Example: `stored_order_total = payable_total`.

**M2 — Structural and behavioral system model.** Represents components, methods, calls, data flow, state transitions, persistence actions, and execution traces, each attached to source locations and confidence/provenance.

**M3 — Fault hypothesis model.** Represents candidate faulty elements, proposed fault mechanisms, causal chains, predicted observations, contradictory evidence, and support level. A hypothesis is more than `(file, score)`.

**M4 — Investigation and evidence model.** Represents test/probe plans, generated assertions, observed results, model traceability, costs, and evidence quality. This layer is what supports budget-aware experiment choice.

### The essential transformations

| Transformation | Input → output | Its scientific role |
|---|---|---|
| **T1: Complaint-to-contract** | Natural-language bug report → symptom/behavioral model | Turns prose into explicit, falsifiable expectations, with ambiguity marked. |
| **T2: Code-to-system model** | Repository + optional traces → typed architecture and data-flow model | Provides cross-file relationships not available from surface similarity alone. |
| **T3: Model composition / slicing** | Behavioral model + system model → relevant causal slices | Narrows investigation while preserving possible nonlocal causes and traceability. |
| **T4: Explanation synthesis** | Causal slices → diverse fault hypothesis models | Generates alternative failure mechanisms, not just differently worded file guesses. |
| **T5: Hypothesis-to-probe** | Hypothesis model → test, instrumentation, static query, or counterfactual check | Forces predictions that can independently support or contradict an explanation. |
| **T6: Evidence-to-model update** | Probe results → revised hypothesis models and ranks | Makes learning persistent outside agent conversations. |
| **T7: Model-to-fresh-context** | Validated evidence + selected hypotheses → minimal new agent task | Implements **MDE-guided strategic forgetting**. |

For a strong research paper, T4–T7 should be the primary methodological focus. T1 and T2 may reuse established parsing, information extraction, graph and program-analysis machinery. Otherwise, the claimed research contribution could collapse into a large integration effort.

### A small illustrative fault metamodel

```text
BugReport 1 --- * Symptom
Symptom 1 --- * BehavioralInvariant
SystemElement * --- * SystemElement [typed: calls, reads, writes, data_flows_to]
Hypothesis 1 --- 1 ProposedFaultMechanism
Hypothesis 1 --- * CandidateElement
Hypothesis 1 --- * Prediction
Prediction 1 --- * Probe
Probe 1 --- * Observation
Observation * --- * EvidenceArtifact [provenance + reproducibility]
Observation * --- * Hypothesis [supports | contradicts | inconclusive]
Hypothesis * --- * Hypothesis [alternative_to | depends_on]
```

Candidate **metamodel constraints**: (a) every claim of confirmed support must reference an observation; (b) every observation must have provenance; (c) every causal edge is typed as derived, observed, or conjectured; (d) a hypothesis can be marked contradicted only under stated test assumptions; (e) source mapping must be versioned; (f) forgetting must not delete confirmed observations or their references.

These constraints make the approach more reproducible than a collection of chat prompts.

## 5. The new idea: evidence-preserving model-driven forgetting

The original forgetting paper restarts from **one best-performing candidate**, relying on a judge's score. Bug localization cannot simply copy this strategy. A candidate file may look convincing but be wrong; the evidence is incomplete; and one hard bug may have several plausible, independent causal paths.

MORPH-FL therefore introduces **Portfolio-Preserving Forgetting (PPF)**:

- **Forget:** full agent conversations; chain-of-thought-like narrative summaries; unsupported intuition; duplicated retrieval logs; speculative explanations that have not earned evidence; stale task decomposition.
- **Retain:** bug report; repository commit; reproducible environment; verified observations and their test/trace provenance; typed source/model links; explicit unresolved questions; a *small, diverse portfolio* of defensible hypotheses.
- **Reconstruct:** fresh agent instructions by transforming the retained models into different investigation views, rather than replaying old conversations.
- **Audit:** a separate immutable run log may preserve all activity for experimental reproducibility, while withholding it from the restarted agents. Thus **epistemic forgetting is not physical deletion**.

### How to decide when to forget

Use a monitored plateau signal rather than a fixed timer alone. A reset becomes a candidate when, across the latest investigation window:

- verified evidence gain is low;
- repeated probes or identical file inspections are common;
- the agents' active hypotheses have become unusually similar;
- the cost per new discriminating observation rises;
- a minimum exploration budget has been consumed.

A reset decision must also consider the **cost of restarting**. A short, productive agent should not be reset unnecessarily. Fixed-interval and no-reset strategies are essential baselines.

### Why preserve multiple hypotheses?

For ordinary optimization, one scored candidate may summarize progress. In localization, the top-scored candidate is often uncertain. Retaining only H1 can encode an early mistake into every new cycle. A bounded portfolio—say, **2–4 nonredundant explanations** as an experimental design choice—makes the search more robust while limiting memory.

Select hypotheses by a combination of evidential support, contradiction, novelty of causal mechanism, and estimated next-probe utility. Do not equate disagreement among LLM agents with independent empirical evidence.

## 6. Budgeted, independent investigation rather than agent debate

A tempting implementation is four agents discussing which file looks suspicious. This alone is not a strong scientific idea; agents may simply influence one another toward a shared wrong answer.

Instead, assign **epistemically different jobs**:

1. **Behavioral investigator:** derives and checks expected-versus-observed behavior.
2. **Structural investigator:** explores dependency, data-flow, and control-flow explanations.
3. **Dynamic investigator:** designs and runs discriminating tests or traces when safe and feasible.
4. **Skeptical investigator:** searches for counterexamples to the current leading hypothesis.

Their outputs must conform to the *same hypothesis and evidence metamodel*, allowing comparison and targeted information exchange. Agents share **verified findings and structured hypotheses**, not full conversational transcripts. If an environment cannot run tests, the framework falls back to static or manual verification and marks the reduction in evidence strength.

### Choosing the next probe

The system prioritizes a probe that is likely to **distinguish plausible hypotheses**, not merely confirm the favorite one.

In the checkout example:

- Reading `CheckoutPage.tsx` again has low information value after two uninformative passes.
- Capturing the argument passed to `OrderRepository.save` is highly discriminating: it separates an upstream wrong-value fault (H3) from a downstream persistence overwrite (H4).

A practical decision function can rank probes by:

> **Expected reduction in disagreement among plausible hypotheses × predicted reliability, divided by estimated cost.**

This is a design hypothesis, not a guaranteed optimal rule. Reliability and expected information value must be estimated from calibrated validation data or conservative heuristics, never assumed to be precise probabilities.

## 7. Four conceptual algorithms

The following algorithms deliberately describe the **scientific approach**, not API calls, framework-specific agent wiring, or deployment tools.

### Algorithm 1 — Construct model-based bug explanations

```text
INPUT: bug report B, repository R, optional test/trace data D
1. Extract expected and observed behavior from B.
2. Represent them as a behavioral model MB.
3. Recover typed structural/behavioral model MR from R and D.
4. Identify model elements relevant to the violated behavior.
5. Expand around symptom paths to include possible upstream causes.
6. Generate distinct causal mechanisms for the observed failure.
7. Bind each mechanism to candidate source elements in R.
8. Derive at least one observable prediction per mechanism.
9. Record provenance, uncertainty, and traceability.
OUTPUT: linked models MB, MR, and hypothesis portfolio H
```

**Interpretation:** This changes localization from text matching to a search over models of what could have caused the failure.

### Algorithm 2 — Transform hypotheses into investigations

```text
INPUT: hypothesis portfolio H, evidence ledger E, remaining budget C
1. Select plausible hypotheses with different causal mechanisms.
2. Find observations on which those hypotheses predict different results.
3. Transform the predictions into feasible probes or model queries.
4. Estimate each probe's discrimination value and resource cost.
5. Reject redundant, unsafe, or unaffordable probes.
6. Execute the most informative feasible probes independently.
7. Verify outputs and attach reproducible evidence references.
8. Mark each result as supporting, contradicting, or inconclusive.
9. Update hypotheses and remaining budget.
OUTPUT: updated H, E, and C
```

**Interpretation:** A proposed fault earns credibility through tests, traces, or explicit program-analysis evidence—not rhetorical persuasiveness.

### Algorithm 3 — Evidence-preserving strategic forgetting

```text
INPUT: agent sessions S, hypotheses H, evidence E, search metrics M
1. Measure evidence gain, repetition, diversity, and recent costs.
2. If exploration remains productive, continue current sessions.
3. Otherwise identify evidence that passes provenance checks.
4. Keep a bounded, diverse set of viable hypotheses.
5. Preserve unresolved questions and versioned source links.
6. Create a concise, validated model snapshot K.
7. Retire agent sessions and exclude speculative history.
8. Transform K into fresh, distinct agent investigation briefs.
9. Relaunch exploration subject to the remaining budget.
OUTPUT: refreshed sessions and retained snapshot K
```

**Interpretation:** Forgetting occurs at the **search-context boundary**; it does not erase externally audited data or previously reproduced failures.

### Algorithm 4 — MORPH-FL localization loop

```text
INPUT: bug report B, repository R, total budget C
1. Construct behavioral, system, and fault hypothesis models.
2. Initialize a diverse team of model-guided investigators.
3. While budget remains and localization is unresolved:
4.     Select discriminating investigations from current models.
5.     Execute probes and independently validate observations.
6.     Update causal hypotheses and their source mappings.
7.     Evaluate stagnation and independence of evidence.
8.     If justified, perform model-preserving forgetting.
9.     Check stop/abstention criteria and minimum evidence quality.
10. Rank source elements with associated causal explanations.
11. Return evidence, contradictions, uncertainty, and costs.
OUTPUT: ranked locations and auditable localization report
```

**Interpretation:** The algorithms define an iterative scientific investigation, in which MDE transforms *what is known* into *what should be tested next*.

## 8. Where the innovation actually lies

For a competitive TSE or ICSE paper, the contributions should be framed as **testable methodological advances**, not as “LLM + graph + multi-agent + forgetting.”

**Contribution C1 — A model-based search space for fault localization.** Introduce typed fault hypothesis models with predicted observations, contradictions, and source traceability. This allows agents to explore *explanations* instead of simply revising file rankings.

**Contribution C2 — A semantics-aware, evidence-preserving forgetting operator.** Define exactly what is discarded, retained, and reconstructed. Unlike source-paper forgetting from one scored candidate, the operator retains an uncertainty-aware portfolio and independently verified evidence. The testable insight is that preserving *knowledge in a model* while deleting *search narrative* can prevent fixation without destroying progress.

**Contribution C3 — Model-to-investigation transformations with budgeted discrimination.** Automatically convert causal hypotheses into probes that distinguish explanations. The search objective is **information gain and fault localization quality per cost**, not conversation length, answer consensus, or raw number of inspected files.

**Contribution C4 — An empirical account of fixation, forgetting, and causal localization.** Characterize when and why long-running localization agents stall, when resets improve results, and when resetting harms results. Negative findings and tradeoffs would be scientifically valuable.

### A crucial novelty boundary

Existing ideas such as agent session reset, state summarization, graph-based retrieval, program slicing, test generation, causal debugging, and model transformations each have prior literature. The proposal **must not claim these individually as inventions**. Its potential novelty is the specific *composition and formal semantics* of (a) evidence-backed fault models, (b) executable model transformations, and (c) adaptive, evidence-preserving forgetting under uncertainty and fixed budgets.

A reviewer may reasonably ask whether a simple stateless agent plus a good evidence summary achieves the same results. MORPH-FL must answer that question experimentally, not merely argue that MDE seems preferable.

## 9. A possible formalization (kept intentionally lightweight)

A hypothesis can be represented as:

`H = (fault location(s), failure mechanism, predicted observations, supporting evidence, contradicting evidence, provenance)`

A research run maintains:

`State = (bug model, system model, hypothesis portfolio, evidence ledger, agent contexts, remaining budget)`

**Evidence-preserving forgetting** transforms this state into:

`Forget(State) = (bug model, system model, selected hypotheses, verified evidence, fresh contexts, remaining budget)`

The core safeguards are:

- **Evidence preservation:** verified observations remain available and source-versioned after a reset.
- **Hypothesis diversity:** selected retained hypotheses should not all describe the same causal explanation.
- **Epistemic status preservation:** “observed,” “inferred,” and “unverified” must never be silently conflated.
- **Budget preservation:** restarting does not reset or hide incurred costs.
- **Reproducibility:** results are traceable to a source revision and an observation procedure.

These are **proposed invariants**, not currently proven theorems. A later formal section can express the operator as a typed graph transformation with preconditions and postconditions, perhaps using an EMF/Ecore-style metamodel, graph transformation rules, and OCL-like constraints.

## 10. Evaluation plan for a top software engineering venue

### Three primary research questions

**RQ1 — Effectiveness:** Does MORPH-FL localize faults more accurately than strong retrieval-based, agentic, and structure-aware localization baselines, especially for cross-file and low-similarity bugs?

**RQ2 — Mechanism:** Do model-guided hypotheses and evidence-preserving forgetting reduce fixation and improve recovery from incorrect early hypotheses? Which component causes the improvement?

**RQ3 — Efficiency and reliability:** At equal model, tool, token, and dollar budgets, does MORPH-FL provide better localization quality, stronger evidence, and more reliable uncertainty estimates?

### Datasets and problem selection

Use at least two complementary groups:

- **Historical repository-level localization cases:** issues linked to validated fault-fixing commits, with carefully inspected ground truth at file/function level. Examples of benchmark families to assess include Defects4J (Java) and BugsInPy (Python), subject to whether a valid issue description and pre-fix snapshot are available.
- **Modern, realistic issue-driven repository tasks:** curated subsets of SWE-bench-style instances, evaluated strictly as *pre-fix fault localization*, not automatically equated with end-to-end patch success. Ensure that the change set actually identifies the cause and is not inflated by refactoring, tests, or unrelated edits.

Stratify by single-file versus multi-file, within-component versus cross-layer, presence/absence of stack traces, lexical similarity of report to ground-truth file, and availability of executable tests. Include hard cases where reports mention symptoms distant from causes.

**Important:** SWE-bench and end-to-end repair benchmarks are not bug-localization datasets by definition. Deriving ground truth and preventing future-information leakage require separate, documented validation.

### Baseline families

Compare against representative, actually available implementations of:

1. Lexical and learned retrieval/ranking (BM25 and strong code/text embedding retrievers).
2. LLM reranking of identical retrieved candidates.
3. An agentic localization workflow using repository browsing/search and tests, with **the same tools and model**.
4. Structural or graph-aware localization using slicing/dependency evidence without the proposed transformations.
5. A team of collaborating agents with continuous context but no forgetting.
6. A fixed-interval reset team seeded by the best ranked file or by a plain-language summary.
7. A **stateless agent with an evidence summary but no explicit MDE metamodel**—an especially important conceptual competitor.

Named systems/papers that warrant literature investigation include **Agentless**, **SWE-agent**, and **SWE-bench**. These have different primary goals; their *localization components* or comparable configurations—not their repair success numbers—would be the fair comparison. Research on classic information-retrieval localization (e.g., BugLocator/BLUiR), coverage-based fault localization, and graph/causal localization should also inform baselines. **Their publication venues, latest versions, direct comparability, and post-2024 improvements have not been verified here.**

### Essential ablations

| Variant | Question answered |
|---|---|
| Full MORPH-FL | Overall result. |
| No forgetting | Does resetting really help? |
| Fixed forgetting interval | Is adaptive triggering necessary? |
| Context-only forgetting + full model retention | Is discarding speculative model history useful? |
| Keep only one top hypothesis | Does a diversified portfolio prevent lock-in? |
| No MDE transformations (text evidence summaries) | Does MDE add value beyond competent summarization? |
| MDE + no tests/probes | How much comes from executable verification? |
| No skeptical agent | Does explicit counterexample search matter? |
| Independent agents without communication | Does evidence sharing outperform isolated exploration? |
| Same budget, 1 agent versus 4 agents | Are gains due to additional parallelism? |

### Metrics

**Primary:** Top-1, Top-5, Top-10 localization accuracy; mean reciprocal rank (MRR); recall at file and function level; multi-location set precision/recall where relevant.

**Efficiency:** input/output tokens; dollars at recorded model prices; wall-clock latency; test/probe count; duplicate inspections; accuracy-versus-cost area or performance across fixed budget levels.

**Evidence quality:** fraction of claimed causes backed by independently reproducible observations; frequency of contradictory evidence ignored; evaluator-agreement on causal chain validity; selective accuracy when abstaining; calibration metrics where probabilities are reported.

**Fixation mechanism:** diversity of fault mechanisms over time, frequency of hypothesis switches, incorrect-lead recovery, novel evidence produced per budget, and plateau onset versus reset timing.

**Statistical practice:** use the same cases and cost limits across variants; repeat stochastic runs; report uncertainty intervals and paired comparisons; control for repository/language clustering and multiple comparisons; publish the exact prompt/tool configurations. Do not claim significance on a handful of examples.

### A particularly revealing experiment: planted early misdirection

Introduce an **incorrect but plausible initial clue** in a controlled, clearly disclosed experiment (for example, a stack-trace-framed description that points at a caller while the bug is in a downstream persistence service). Ask whether the method can recover after initially selecting the wrong culprit. Evaluate both natural and controlled cases to avoid confusing an artificial stress test with real-world prevalence.

Expected empirical signature *if the hypothesis is right*: continuous-context agents keep revisiting the same incorrect location; fresh model-guided agents use retained disconfirming evidence to investigate a new mechanism; ordinary resets without structured evidence either repeat the old mistake or lose useful work. These are **predictions to test, not observed results**.

## 11. Practical feasibility and staged implementation

**Phase 1 — Minimal falsifiable prototype.** Support one language/ecosystem and one issue benchmark. Parse reports into behavior contracts, extract a call/data-flow graph, maintain structured hypotheses, run basic tests, and implement manual/fixed strategic resets. Compare to a strong stateless summarization baseline before building any elaborate framework.

**Phase 2 — Model transformations.** Define metamodels and transformations with explicit source mappings, validity rules, and provenance. Implement the hypothesis-to-probe transformation for a limited class of reproducible bugs. Distinguish deterministic static analysis from LLM-proposed relations.

**Phase 3 — Adaptive forgetting and portfolios.** Add diversity-constrained hypothesis selection, stagnation detection, counterexample-oriented agents, and model-to-fresh-context generation. Record full research logs separately from agent-visible working memory.

**Phase 4 — Broader evaluation.** Expand languages/architectures and measure generality under matched costs, missing tests, incomplete graphs, noisy bug reports, and multi-fault cases. Release dataset manifests, traces, exact source revisions, and code where licensing allows.

A reasonable implementation might use tree-sitter or language-specific parsers, static analyses for call/data flow, a typed graph store, simple YAML/JSON metamodel instances, and an isolated test runner. **Specific frameworks (EMF, ATL, QVT, Henshin, etc.) are optional engineering choices, not requirements for conceptual novelty.** If the paper invokes MDE, it must genuinely deliver typed transformations and their semantics rather than merely decorating an agent system with an architecture diagram.

## 12. Risks, counterarguments, and how to make the research credible

**Risk: Forgetting removes useful insights.** Mitigation: preserve verified evidence and meaningful open questions. Test how often structured snapshots lose important knowledge; compare to full-context and high-quality summaries.

**Risk: The best hypothesis is wrong.** Mitigation: retain a diverse portfolio and explicit contradiction records; investigate alternatives instead of restarting every agent from one winner.

**Risk: Model construction costs more than it saves.** Mitigation: measure end-to-end costs including parsing, graph extraction, tests, model updates, and failed probes; amortize repository models only where multiple issue investigations justify reuse.

**Risk: Causal conclusions are overstated.** Mitigation: use precise distinctions among association, data-flow reachability, and causal verification. A dependence edge or failed test alone may not demonstrate that a particular statement causes the symptom. Require counterfactual or discriminating evidence when feasible.

**Risk: Incorrect or incomplete reports lead to invalid contracts.** Mitigation: represent ambiguity explicitly, permit several candidate expected behaviors, and abstain when the behavior cannot be reproduced or reliably inferred.

**Risk: Baseline unfairness and leakage.** Mitigation: freeze pre-fix commits; avoid accessing patches, post-fix tests, solution discussions, or commit messages unavailable at issue time; enforce equal resources and tool permissions.

**Risk: Too many ingredients obscure the central cause.** Mitigation: make the primary research hypothesis precise: *validated hypothesis models act as a sufficient practical memory for fresh agents*. Use targeted ablations to test that claim. Do not assert mathematical sufficiency without proof and assumptions.

**Risk: The contribution already exists in contemporary work.** Mitigation: conduct a rigorous, up-to-date systematic positioning review across recent ICSE, FSE, ASE, ISSTA, TSE, TOSEM, and EMSE work, especially on hypothesis-driven agents, state compression/reset, model-based diagnosis, graph-guided localization, automated experiment design, and causal program analysis.

## 13. Suggested paper framing

### Candidate title

**MORPH-FL: Model-Driven Hypothesis Evolution and Strategic Forgetting for Agentic Bug Localization**

Alternative, more scientific (less acronym-led) title:

**Forgetting the Search, Preserving the Evidence: Model-Driven Fault Hypothesis Exploration for Bug Localization**

### Abstract draft (proposal language—not experimental claims)

> AI-powered bug localization increasingly relies on language models that inspect repositories, retrieve code, and iteratively refine suspected fault locations. Despite their promise, these workflows may become anchored to early hypotheses, struggle to connect externally observed failures to nonlocal root causes, and spend substantial computation revisiting unverified explanations. We propose MORPH-FL, a model-driven framework for evidence-based fault hypothesis exploration with strategic forgetting. MORPH-FL transforms bug reports and repository artifacts into linked behavioral, structural, and causal hypothesis models; converts competing explanations into discriminating investigations; and updates a versioned ledger of independently verifiable observations. When exploration stagnates, an evidence-preserving forgetting operator discards agents' accumulated search contexts while retaining a diverse portfolio of plausible fault models and validated findings, from which fresh investigations are generated. Unlike reset strategies that retain only a single best candidate, MORPH-FL explicitly manages uncertainty and contradictory evidence during fault localization. We outline research questions and an empirical design to examine whether this combination improves localization effectiveness, recovery from early misdiagnosis, and evidence quality under controlled computation budgets.

### Expected paper structure

1. Introduction: the intertwined fixation, causality and cost problems; motivating example.
2. Background and related work: bug localization, MDE, model-based diagnosis, LLM agents, strategic forgetting.
3. Definitions and running example: behavioral model, typed repository model, hypothesis, observation, evidence and reset semantics.
4. Approach: model transformations, discriminatory exploration, evidence ledger, adaptive forgetting.
5. Implementation choices and validity constraints (brief; research paper, not tool paper).
6. Experimental design and results: main comparisons, ablations, cost, mechanism, negative cases.
7. Discussion and threats to validity.
8. Related work positioning and conclusions.

## 14. What should be established *before* making a novelty claim

This is a proposal, not a completed literature review. Web verification was unavailable when preparing it, so **the following points remain unverified**:

- Which of the most recent top-venue agentic bug localization papers already formalize and verify competing hypotheses, reset contexts, or use typed architectural models.
- Which public datasets provide genuinely validated root-cause locations and executable reproductions suitable for cross-layer experiments.
- Whether model-driven fault diagnosis and evidence-aware search-reset combinations have already been reported under other names.
- Which baselines are currently strongest at comparable localization-only budgets.

Before writing a TSE/ICSE novelty claim, produce a **prior-art comparison matrix** with rows for each peer-reviewed system and columns for: typed hypothesis metamodel; explicit causal predictions; automatic probe transformation; evidence provenance; context reset; portfolio selection; adaptive reset; matched-cost localization evaluation. The main claim should be narrowed to what this comparison and the experimental results can truly support.

## 15. The most important scientific insight

The source paper suggests that an agent's accumulated search history can become a liability. For bug localization, the solution is **not simply to forget more often**. A debugger must remember the *right kind of information*: confirmed facts, the conditions under which those facts were observed, and the explanations they support or contradict.

MORPH-FL makes that distinction the core of the research:

> **Forget the investigator's journey; preserve the verified model of the problem. Then use model transformations to choose a better next experiment.**

If this mechanism improves localization under fair, controlled comparisons—and the gain cannot be matched by cheaper summaries or ordinary stateless agents—it could support a substantive software-engineering research contribution.

---

## Source and positioning notes

**Primary supplied source:** Tan, S., Zhou, B., Agrawal, L. A., et al., *Scaling Discovery Requires Forgetting* (user-provided manuscript, 2026). In the manuscript, the authors describe session and search-state reset, team communication, and empirical gains on heuristic programming, kernel optimization, and small-model training. These results motivate the research question; they **do not validate MORPH-FL**.

**Literature starting points to verify before citation in a submitted paper:** classic IR-based bug localization (BugLocator, BLUiR); coverage-based fault localization; model-based diagnosis; modern LLM-based repository localization and repair including Agentless and SWE-agent; benchmark methodology including SWE-bench, Defects4J and BugsInPy; recent papers on agent forgetting and stateless agents cited in the supplied manuscript. This is a scoping list, **not a verified or exhaustive state-of-the-art review**.


## 16. Exploratory implementation and empirical status

The prototype implements typed M1–M4 records, transformations, scoped observation checks, a budgeted sequential role controller and portfolio-preserving context resets. It currently uses Python AST analysis and conservative dependency neighborhoods, lexical/path hypothesis distance, and a probe-utility heuristic. It does not implement sound semantic/control-flow slicing, graph-edit distance, calibrated entropy reduction or an independently validated causal-confidence estimator. The supplied Gemini explanation should be read as a design sketch; the executable algorithms and supported claims are defined in the linked specifications above.

Pinned Agentless and RGFL components have been adapted to the installed 7B/30B local models. On six additional SWE-bench Lite cases, MORPH-FL reaches 4/6 file Top-1 with 7B and 2/6 with 30B. A stateless summary reaches 4/6 and 3/6; post-hoc larger-tree Agentless reaches 3/6 and 5/6, while larger-tree RGFL reaches 4/6 with either model. These are small single-seed, source-only studies with unreviewed patch-change labels and documented adaptation differences. They do not establish superiority over the full upstream systems.

Actual resets and observation retention have been observed in longer one-case development diagnostics, but a causal benefit of forgetting, recovery from planted wrong leads, calibration and cross-language generalization are not established. The subsequent configurable-policy/window-sensitivity study is separately versioned and must not be retrospectively attributed to the historical benchmark runs. Full tables, provenance, limitations and negative cases are preserved in `experiments/baselines/` and `experiments/alignment/`.
