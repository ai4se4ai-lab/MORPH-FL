# Independent reader log, round 1

Reader perspective: software-engineering PhD student familiar with debugging, testing, basic fault localization, and empirical methods; unfamiliar with LLM-agent memory and this paper's notation. Read Sections 1–4 in source order, without prior review or support documents. Difficulty: 1 immediately clear, 2 modest attention, 3 rereading needed, 4 substantial reconstruction, 5 unable to understand. Locations refer to `docs/TSE/main.tex`. This is a comprehension assessment, not source-code verification.

## Every prose paragraph, in reading order

| Source line | Main point in my words | Confusion | Difficulty | Suggested fix |
|---|---|---|---:|---|
| 55 | Symptoms can lead to the wrong file; localization chooses inspection locations. | None. | 1 | None. |
| 57 | Existing model-based workflows help search but leave restart retention unresolved. | None; restarting conversational context is understandable from context. | 2 | None. |
| 59 | Explanations may survive weak checks, repetition is not new evidence, and restarts can lose conditions. | None. | 2 | None. |
| 61 | Separate observations from explanations and dialogue, preserving observations at restart. | None; the incomplete recovery warning is clear. | 2 | None. |
| 63 | Compare the full system against a specific observation-text handoff, while acknowledging confounded information and timing. | The exact simple control arrives before I understand behavior fields or relation excerpts. | 3 | Start with a short example of the text handoff; defer its omitted-field inventory to the variant section. |
| 66 | The prototype combines typed state, sequential roles, checks, and restart heuristics; benchmark evidence is static Python evidence. | “Typed investigation state” and AST are technical but interpretable. | 2 | Briefly gloss typed as explicit structured records. |
| 68 | Three questions concern ranking, continuation behavior, and cost, with restricted interpretations. | “Patch-proxy” is not yet defined; too many hypotheses and inference limits intervene between the questions. | 3 | Give each RQ its own paragraph; explain patch locations as imperfect reference answers on first use. |
| 70 | The package is the study object; controls cannot isolate typed representation. | The named variants are introduced before their actual changes. | 2 | Add a short parenthetic gloss or point to the variant table. |
| 72 | Contributions are a protocol, prototype, and auditable retention specification; results remain unfinished. | What concrete object constitutes the “contract” is unclear here; claim slots are unmistakably unfinished. | 3 | Say whether contract means the documented state/update rules; keep the draft status explicit. |
| 76 | Ranked locations differ from causal explanations; patch locations are imperfect reference labels. | None. | 1 | Move the patch-label explanation earlier too. |
| 79 | A hypothesis predicts; an observation records a check; an assessment connects them. | None. | 1 | None. |
| 82 | Source, AST, and dynamic evidence support different claims, each only within its checked scope. | None. | 2 | None. |
| 85 | Reset removes model dialogues, preserving observation records; record equality does not prove useful continuation. | None; the three-property distinction is helpful. | 2 | None. |
| 89 | The example is synthetic and concerns a false configuration flag. | None. | 1 | None. |
| 101 | Competing renderer/default hypotheses can receive quote or AST checks, neither of which executes the failure. | None. | 1 | None. |
| 103 | Python semantics explain the example, but the implemented static checks cannot establish the runtime cause. | None. | 1 | None. |
| 105 | Repeated checks can trigger reset while facts survive and selected explanations continue. | “Plateau” is sufficiently understandable as stalled progress. | 2 | None. |
| 108 | Public investigation inputs exclude evaluation answers, though pretraining leakage remains possible. | None. | 1 | None. |
| 111 | Outputs include rankings and audit state; scoring must distinguish classes, functions, and missing reference labels. | “Explicit denominator” does not yet say which cases actually count. It reads as a study obligation. | 2 | Point to the study-design denominator rule. |
| 114 | This is limited-budget ranking, not repair or causal proof; confidence is unavailable. | None. | 1 | None. |
| 134 | Records, scoped assessments, and multiple explanations address restart needs, but the particular heuristics are choices. | None. | 2 | None. |
| 136 | Checks populate facts, reasoning populates hypotheses, and sequential roles share a backend. | None. | 1 | None. |
| 163 | M1 stores report interpretations and M2 approximate Python structure. | M1/M2 are new labels with little mnemonic value. | 2 | Prefer Behavior/System labels alongside every M-number. |
| 166 | M3 holds hypotheses and M4 checks/results/budgets; assessment records cannot uniquely identify every prediction. | Dense schema inventory plus a consequential missing-link exception requires rereading. | 3 | Separate the record inventory from a concrete two-prediction example of the missing linkage. |
| 169 | Seven transformations extract, analyze, propose, assess, and rebuild; no_mde only hides models from agent views. | T-number inventory is hard to retain without a mapping table. | 2 | Provide a compact T1–T7 table or use descriptive names. |
| 173 | Lexical retrieval and two-hop structure produce bounded investigation candidates, possibly excluding the fault. | “Stable concatenation” needs a moment to parse as order-preserving combination. | 2 | Say “combine in this order, keeping first occurrences” if that is intended. |
| 176 | Requests rotate limited source excerpts, but line validation does not ensure the model saw that line. | None. | 2 | None. |
| 211 | Attempted calls differ from valid rounds; invalid calls cost resources without monitoring, and context overflow stops. | None after rereading the algorithm. | 2 | None. |
| 214 | The example could produce and reuse a quote observation without promising the model will choose it. | None. | 1 | None. |
| 217 | Proposal validation, hypothesis identity, probe identity, and predicate dispatch impose imperfect matching rules. | Several kinds of identity and exceptions are introduced together; “source-presence dispatch” is implementation jargon. | 3 | Split identity rules from predicate checking; illustrate one unsupported kind/predicate pair. |
| 220 | Quote checks one line; AST checks the file; dynamic checks require registered contained procedures. | None; Apptainer details are secondary but clear. | 2 | None. |
| 223 | Physical cache reuse saves checks, but repeat assessment can be skipped even for a changed prediction. | Why an observation already supports a hypothesis suppresses another prediction takes rereading. | 3 | Add a two-prediction micro-example and name the consequence first. |
| 226 | Logical suppression can prevent restoring a recreated hypothesis's old score/links, despite retaining its observations. | The prune/recreate/cache/filter lifecycle and planned audit are too much for one paragraph. | 3 | Give an ordered before/reset/recreate example; move audit requirements to the audit subsection. |
| 229 | Explicit predicates cause fixed signed score increments, not probabilistic confidence. | None. | 2 | None. |
| 232 | Duplicate-looking evidence may inflate scores and overwhelm diversity preferences. | None. | 2 | None. |
| 236 | Define mechanism terms and first file path to compute cheap dissimilarity. | None. | 2 | None. |
| 243 | Distance is lexical/file difference, and even empty term sets look different; pool diversity averages it. | The empty-set behavior is surprising but explicitly explained. | 2 | None. |
| 269 | Utility orders checks using chosen weights; portfolio selects at most k hypotheses; isolated roles skip logical suppression. | “Declared alternatives” requires connecting predicates back to earlier prediction definitions. | 2 | Give one expected-value alternative example. |
| 272 | File difference contributes to distance; high-score/diverse selection need not retain a good alternative. | None. | 1 | None. |
| 275 | Monitor stalled evidence gain, cached repetition, diversity, and tokens on valid rounds. | None; within-batch repetition exclusion is precise. | 2 | None. |
| 291 | Restart requires all gates; history resets but cumulative valid rounds do not. | Numerous gates and symbol meanings require consulting algorithm/table. | 3 | Give a plain-language gate list before the symbols. |
| 313 | Scopes determine shared/isolated retention; reconstructed views can hide untested predictions and grow too large. | Scope is defined late; three distinct caveats compete in one paragraph. | 3 | Define scope before the notation table and split retention, unresolved-list logic, and request size. |
| 316 | Reset preserves observation IDs but does not guarantee deep immutability or useful reconstructed meaning. | None; API terminology is familiar. | 2 | None. |
| 319 | The example's fact survives pruning and dialogue clearing; effective continuation is unproven. | It mentions h_A pruning although the quote was motivated by h_B; I can infer the general point but the example connection is slightly awkward. | 2 | Say “even if its originating hypothesis is pruned,” or consistently identify h_B. |
| 322 | A fully numeric synthetic state passes the reset gates while retaining both alternatives. | Computation is understandable but dense; defaults must be looked up ahead. | 3 | Put numeric inputs and gate outcomes in a small trace table. |
| 324 | The reset rebuilds a rich request while preserving facts, but demonstrates no model success or information sufficiency. | None. | 2 | None. |
| 328 | File ranking uses maximum live scores; symbol ranking follows a separate ordering and may disagree. | None. | 2 | None. |
| 331 | Dynamic early stopping uses a particular support rule that may reference a pre-pruning pool. | The significance of holding a reference to the old pool is not immediately evident. | 3 | Explain directly that the stop may concern a hypothesis absent from the retained pool. |
| 334 | Causal abstention depends on any historical causal dynamic support, not the final leader. | None. | 2 | None. |
| 354 | Neighborhood expansion is bounded and bidirectional, and misses unresolved links. | None. | 1 | None. |
| 379 | Fourteen configurations change one system; observation-text controls omit multiple fields and differ in dialogue timing. | Too many similarly named controls and interacting changes to retain in prose. | 3 | Use a feature matrix with dialogue, hypothesis visibility, reset timing, and cache sharing columns. |
| 405 | Paired rankings and component contrasts use common subjects, while conditional recovery rates have workflow-specific denominators. | “Proxy-wrong clues followed by its first valid-round leader” is difficult phrasing. | 3 | Say the reference labels mark the clue wrong and the workflow initially ranks it first. |
| 407 | Planned audit counts recreated hypotheses, lost links, suppressed probes, and changed predictions under explicit eligibility rules. | Unit, denominator, artifacts, scope reconstruction, and interpretation restrictions are packed together. | 3 | Provide a table with event, eligible unit, numerator, denominator, and missing-data rule. |
| 410 | A first-call unverified clue tests an operational wrong-lead proxy without changing retrieval. | None after the previous paragraph; BM25 rank two clue selection is concrete. | 2 | None. |
| 413 | Hash-linked artifacts support provenance, with explicit cost-accounting and timing limits. | None. | 2 | None. |
| 417 | Retrieval and learned localization use different information; their reused components are not new here. | None. | 1 | None. |
| 419 | Related agents navigate or reason about candidates; this study focuses on reset evidence boundaries. | Many system names, but purpose is clear. | 2 | None. |
| 421 | Prior systems already use memory/restarts; this proposal combines within-run observations and a portfolio for uncertain localization. | Dense literature inventory but no unresolved concept. | 2 | Split project/task memory from general restart work if space permits. |
| 423 | Ledger is the closest state-recording predecessor, but lacks this particular reset policy; internal control is not its reproduction. | None. | 2 | None. |
| 425 | Formal diagnosis, runtime evidence, and provenance each differ from this approximate implementation. | None. | 2 | None. |
| 427 | Practical significance requires empirical findings beyond a retention invariant. | None. | 1 | None. |
| 429 | Only restricted Agentless/RGFL adaptations run as external comparisons; related systems and repair metrics are not equivalent baselines. | None. | 1 | None. |

## Definitions and technical/displayed objects

The paragraphs above cover prose definitions individually. The following inventory makes their purpose, inputs, outputs, and need explicit.

| Location/object | Plain-language purpose; inputs; outputs; why needed | Difficulty / fix |
|---|---|---|
| 76 localization/explanation | Distinguish ranking source elements from explaining failure. Inputs: report/repository; outputs: ordered paths/symbols versus causal story. Needed so evaluation hits do not imply causality. | 1; none. |
| 79 hypothesis/observation/assessment | Separate a proposed explanation, returned check, and interpretation. Inputs: proposed locations/predictions and procedure results; outputs: records and support labels. Needed to avoid counting consensus as evidence. | 1; none. |
| 82 evidence scopes | Classify what a check can establish. Inputs: quote, AST, or registered execution; output: bounded scope of support. Needed to avoid static-to-causal inference. | 2; none. |
| 85 context/reset/three properties | Define what is forgotten and three different success claims. Inputs: dialogue/ledger; outputs: cleared dialogue, retained records, measurable outcomes. Needed to distinguish retention from usefulness. | 2; none. |
| 90–100 listing | Show how a false flag becomes true before rendering. Inputs: options; output: normalized flag and render call. Needed for the symptom/cause file distinction and static-evidence example. | 1; none. |
| 117–130 notation table | Decode algorithm variables. Inputs/outputs: no computation; maps symbols to types/meanings. Needed to read the formal procedures. | 3: access scope s is not explained until l313; define there or earlier. |
| 139–160 flow figure | Show report-to-request-to-check feedback and restart boundary. Inputs: report/source and role proposals; outputs: retained observations/reconstructed requests. Needed to visualize dialogue clearing separately from factual retention. | 2; diagram's two reset feedback edges need caption to interpret, which it supplies. |
| 163–169 M1–M4/T1–T7 definitions | Inventory state containers and update stages. Inputs: report, source, proposals, observations; outputs: typed records and fresh requests. Needed to connect implementation and method. | 3 overall; use a compact mapping table. |
| 179–209 controller algorithm | Coordinate investigation under budgets. Inputs: report, source/revision, backend/configuration; outputs: ranking, evidence, audit, costs, abstention. Needed to define call order, validation, cache, reset, and stopping. | 2; surrounding paragraphs explain tricky valid-round semantics. |
| 237–242 distance equation | Approximate how different two hypotheses are using wording and file. Inputs: mechanism term sets and first paths; output: number in [0,1]. Needed for diversity and utility heuristics. | 2; none. |
| 246–267 ordering/selection algorithm | Prefer apparently useful cheap checks and select score-plus-diversity hypotheses. Inputs: probes, live hypotheses, handled IDs, k; outputs: ordered probes and bounded portfolio. Needed to specify continuation choices. | 3: reliability/cost constants are explained only afterward; introduce these as heuristic fields first. |
| 275 gain/repetition/diversity sample | Measure recent progress. Inputs: valid-round observations, proposals/cache, hypotheses/tokens; outputs: monitor sample. Needed to trigger observable rather than intuitive stagnation. | 2; none. |
| 278–289 plateau algorithm | Decide whether stalled investigation can afford a restart. Inputs: history, budgets, counts, thresholds; outputs: Boolean and diagnostics. Needed to make reset timing reproducible. | 3; precede with plain-language gates and use trace table. |
| 295–311 reset algorithm | Clear conversation/prune hypotheses while preserving ledger. Inputs: scoped pools/dialogues/ledger/monitor; outputs: reduced pools, cleared dialogue/window, rebuilt next view. Needed to specify the forgetting boundary. | 2; define scope before first use. |
| 313 access scope | Specify which roles can see which records. Inputs: sharing configuration and role; output: shared or role-specific state view. Needed to explain isolation and per-scope portfolio bounds. | 2 locally, but definition is late. |
| 316 retention property | State that reset does not change observation-ID membership. Inputs: ledger immediately before/after reset; output: equality assertion. Needed for narrow auditable retention claim, not semantic sufficiency. | 2; none. |
| 322–324 constructed numerical reset | Demonstrate a complete gate evaluation and next request. Inputs: synthetic hypotheses/window/budgets/defaults; outputs: reset decision and retained/rebuilt state. Needed to make abstract algorithms concrete. | 3; tabulate inputs and gates. |
| 337–352 neighborhood algorithm | Expand seed files across resolved relations for fixed hops. Inputs: graph/seeds/hop bound; output: ordered seeds plus new source paths. Needed to connect lexical symptoms to related files. | 2; move beside its first explanation at l173 if layout permits. |
| 357–376 defaults table | Expose chosen constants and implementation locations. Inputs/outputs: configuration reference, no computational result. Needed to reproduce policy and numeric example. | 2; placing near plateau example would reduce lookup. |
| 382–402 variants table | List changed policies and comparison questions. Inputs: configuration choices; outputs: conceptual comparison map. Needed to understand empirical contrasts. | 2 alone, 3 with prose interactions; add feature columns. |
| 432–448 related-systems table | Compare state, evidence, memory study, and output granularity. Inputs: examined primary methods; output: qualified comparison. Needed to locate claimed contribution without assuming absent capabilities. | 2; clear caption limits. |

## Five-sentence comprehension summary

The problem is how a limited-budget language-model fault-localization workflow can restart its conversations without losing checked facts or treating repeated explanations as new evidence. The idea is to retain provenance-bearing observations separately from explanations, while choosing a small score-and-diversity portfolio for the next investigation. The approach retrieves Python files, runs sequential roles that propose hypotheses and permitted checks, assesses explicit predictions, monitors stalled progress, resets dialogue and selected hypothesis state, and finally ranks files and symbols. The research questions ask whether this complete policy improves patch-location ranking, how component changes and wrong-lead trajectories characterize continuation, and whether localization gains justify token, probe, and time costs. Its limits include uncompleted empirical results, source-only benchmark evidence, approximate structure, heuristic accumulating scores, potential interpretation loss and reassessment suppression, unbounded reconstructed observation views, and controls that cannot isolate typed representation itself.
