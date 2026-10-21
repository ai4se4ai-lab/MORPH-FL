# Independent readability log — round 3

Reader stance: PhD reader with software engineering, testing, and basic fault-localization background; no specialist LLM-memory knowledge. Read only `docs/TSE/main.tex`, Sections 1–4. No support documents, earlier reader notes, implementation, or cited papers were consulted. No manuscript edits.

Scale: 1 = immediate; 2 = ordinary technical attention; 3 = needed rereading; 4 = substantial unresolved difficulty; 5 = could not recover the point. Scores describe readability, not scientific merit. Paragraph anchors below follow source order; contribution and reconstruction item lists are logged as grouped prose units. Tables, equations, listings, figure, and algorithms are additionally covered in the technical-object inventory.

Overall: the motivation and retained-fact/reset distinction are clear. Most technical prose needs normal attention (2), not rereading. Four paragraphs genuinely required rereading (P52, P53, P81, P94); P94 leaves a small counting-unit ambiguity. There are no 4–5 passages.

## Every prose paragraph

| ID | Opening anchor | Main point | Difficulty | Confusion / suggested fix |
|---|---|---|---|---|
| P01 | A report that a disabled feature still appears on screen can point an… | Symptom and faulty operation can be in different files. | 1 | No confusion; no change needed. |
| P02 | Language-model workflows address this problem in several ways. Agentl… | Prior localization workflows leave restart retention as a separate question. | 1 | No confusion; no change needed. |
| P03 | The distinction matters because an explanation can outlive the check … | Explanations, agreement, and context loss create risks rather than proven universal defects. | 2 | No confusion; no change needed. |
| P04 | We keep checked observations separately from explanations and from th… | Reset discards dialogue while preserving facts and selected explanations, possibly losing their links. | 2 | No confusion; no change needed. |
| P05 | A text summary is an important alternative. Prior work already uses e… | External summaries and execution memory are established alternatives. | 1 | No confusion; no change needed. |
| P06 | The simple control passes each check as a file/line label followed by… | The control hands over mechanically rendered check results. | 1 | No confusion; no change needed. |
| P07 | The control omits stored explanations, proposed expectations, and sou… | The control differs in information and timing, limiting attribution. | 2 | No confusion; no change needed. |
| P08 | instantiates this idea with explicit structured investigation records… | Prototype combines structured state, sequential roles, cached checks, and heuristic restarts. | 2 | No confusion; no change needed. |
| P09 | We ask three research questions (RQs) without presupposing favorable … | RQs use patch changes as imperfect localization labels. | 1 | No confusion; no change needed. |
| P10 | RQ1: How do file and function patch-proxy rankings compare with the c… | RQ1 compares paired rankings under equal budgets. | 2 | No confusion; no change needed. |
| P11 | RQ2: What do component contrasts and trajectories following disclosed… | RQ2 describes continuation behavior without proving a cognitive mechanism. | 2 | Shorten the operational-hypothesis sentence; keep the qualitative inference limit as a separate sentence. |
| P12 | RQ3: What localization--cost tradeoffs and evidence-handling failures… | RQ3 compares ranking gains against actual costs and cannot assess calibration. | 2 | No confusion; no change needed. |
| P13 | The primary object of study is this complete prototype policy, includ… | The unit of comparison is a complete policy package, not representation alone. | 2 | No confusion; no change needed. |
| P14 | The contribution is an executable instrument for studying restart pol… | Contribution is an executable study instrument. | 1 | No confusion; no change needed. |
| P15 | a controlled comparison protocol for the complete package, continuous… | Instrument includes comparisons, specified state operations, and retention audit. | 2 | No confusion; no change needed. |
| P16 | The retention invariant supports the study; it is not a standalone al… | Retention is supporting infrastructure; results remain unavailable. | 1 | No confusion; no change needed. |
| P17 | Localization returns an ordered set of candidate source elements. A f… | Localization rankings differ from causal explanations. | 1 | No confusion; no change needed. |
| P18 | A hypothesis contains candidate locations, a proposed mechanism, expl… | Hypotheses predict, observations record, and assessments relate the two. | 2 | No confusion; no change needed. |
| P19 | The evidence scope states what was checked. Source presence concerns … | Evidence scope bounds what a check establishes. | 2 | No confusion; no change needed. |
| P20 | An agent's context is the messages supplied on a model call. Each rol… | Record retention, sufficient context, and ranking benefit are distinct properties. | 2 | Keep the three-property distinction; a short labelled three-row table is optional. |
| P21 | An access scope determines which role can read a hypothesis or observ… | Access scope controls who sees data, unlike evidence scope. | 1 | No confusion; no change needed. |
| P22 | Consider the following synthetic Python repository. The report says: … | A synthetic false-setting bug introduces the example. | 1 | No confusion; no change needed. |
| P23 | The handler is the visible symptom site. One hypothesis, $h_A$, suspe… | Quote and AST checks support static facts without executing the failure. | 2 | No confusion; no change needed. |
| P24 | In this constructed expression, ordinary Python evaluation converts e… | Python semantics explain the example, but static probes do not validate runtime causality. | 1 | No confusion; no change needed. |
| P25 | Suppose subsequent valid rounds only propose previously executed quot… | Repeated checks can trigger a reset retaining facts and alternatives. | 2 | No confusion; no change needed. |
| P26 | The inputs are a public report, a pre-fix Python repository at a reco… | Inputs include public case, repository, permitted tools, backend, and budgets. | 1 | No confusion; no change needed. |
| P27 | The outputs are file and symbol rankings, live hypotheses, all record… | Outputs include rankings, state, costs, audit, and abstention. | 1 | No confusion; no change needed. |
| P28 | The implementation's symbol list can contain a class name when the se… | Class symbols must not count as exact function hits. | 1 | No confusion; no change needed. |
| P29 | File Top-$k$ asks whether the first $k$ paths intersect the reference… | Ranking metrics use eligible patch-proxy labels and explicit denominators. | 2 | No confusion; no change needed. |
| P30 | The task is budgeted ranking with auditable evidence, not repair, pro… | Task scope, approximate analysis, execution authorization, and absent confidence bound claims. | 2 | No confusion; no change needed. |
| P31 | The design addresses three needs. Versioned observations make a check… | Three needs motivate separate facts, assessments, and alternatives but not unique heuristics. | 2 | No confusion; no change needed. |
| P32 | Figure~ shows the boundary: execution populates the ledger, while int… | Figure separates execution and interpretation; sequential roles have independent dialogues. | 2 | No confusion; no change needed. |
| P33 | Four groups of dataclasses hold the state. M1, BehavioralModel, store… | M1 describes reported behavior; M2 describes approximate source structure. | 2 | No confusion; no change needed. |
| P34 | M3, FaultHypothesis and Prediction, holds locations, mechanism, predi… | M3 records proposed explanations and scoring links. | 2 | No confusion; no change needed. |
| P35 | M4, the investigation records, contains Probe, Evidence, Assessment, … | M4 separates requested checks, results, interpretations, and budgets. | 1 | No confusion; no change needed. |
| P36 | There is an important limit to that link. A stored assessment names t… | Assessment records omit prediction identity, requiring ordered artifacts for reconstruction. | 2 | No confusion; no change needed. |
| P37 | Table~ maps the labels to their inputs and outputs. The sequence prep… | T1–T7 prepare inputs, validate joint proposals, assess, and rebuild context. | 2 | No confusion; no change needed. |
| P38 | BM25, a lexical report-to-source ranking method, scores files using r… | Lexical seeds and a bounded structural neighborhood determine investigated candidates. | 2 | No confusion; no change needed. |
| P39 | The first request shows the first configured number of candidates. La… | Rotating source windows constrain display, while validation can accept undisplayed lines. | 2 | No confusion; no change needed. |
| P40 | A round limit bounds attempted model calls. A valid round is an accep… | Valid rounds and attempted calls are different counting units. | 1 | No confusion; no change needed. |
| P41 | Invalid responses consume their actual tokens and an attempt, but ski… | Invalid responses spend tokens but do not update the monitor. | 1 | No confusion; no change needed. |
| P42 | A backend context-limit exception stops the run; the controller does … | Context exceptions stop execution and dynamic stopping follows reset handling. | 2 | No confusion; no change needed. |
| P43 | Removing a role or using only the structural role changes which instr… | Role ablations alter the schedule rather than worker count. | 1 | No confusion; no change needed. |
| P44 | For the running example, Algorithm~ can accept a visible config.py pr… | The example shows possible cached static evidence, not guaranteed model behavior. | 1 | No confusion; no change needed. |
| P45 | Synthesis requires a nonempty mechanism, an existing source path, an … | Proposal validation grounds a mechanism, prediction, and check at a real location. | 2 | No confusion; no change needed. |
| P46 | Hypothesis identity uses path, case-folded mechanism, and probe kind;… | Hypothesis and probe identities merge repeated proposals using selected fields. | 2 | Add a small identity-field table before the suppression examples. |
| P47 | An AST check paired with a substring-presence prediction can receive … | Prediction-rule precedence can give an AST result only source-presence support. | 2 | No confusion; no change needed. |
| P48 | Validation does not enforce every predicate/kind pairing. Unsupported… | Accepted combinations can still be inconclusive or uninformative. | 1 | No confusion; no change needed. |
| P49 | A source-quote probe checks substring membership at its specified lin… | Static checks and registered dynamic procedures have different execution scopes. | 2 | No confusion; no change needed. |
| P50 | The physical cache key contains kind, path, and parameters within a r… | Physical cache keys and observation IDs differ; insertion validates provenance. | 2 | No confusion; no change needed. |
| P51 | Reusing a result does not guarantee that every prediction is assessed… | An existing evidence link blocks reassessment of another prediction against that observation. | 2 | No confusion; no change needed. |
| P52 | A retained observation may become disconnected from a recreated hypot… | Pruning and handled IDs can prevent a recreated hypothesis recovering old evidence links. | 3 | Add a before/reset/recreate row showing h, e, handled ID, and absent link. I needed a reread to follow which records survive. |
| P53 | The same skipping rule can affect a changed expectation. If a proposa… | Changing an expected result can leave logical identity unchanged and suppress assessment. | 3 | State directly that prediction fields are excluded from logical probe identity, then show true→false beside an unchanged ID. I reread the previous identity definition. |
| P54 | Raw observation payloads remain available to the model; their former … | Facts remain visible even when scores and interpretation links disappear. | 2 | No confusion; no change needed. |
| P55 | T6 evaluates only the explicit predicate. Its weighting rules have a … | Ordered scope-dependent weights change scores without representing probabilities. | 2 | No confusion; no change needed. |
| P56 | Distinct observation IDs do not guarantee independent information. Di… | Related observations can accumulate scores that overwhelm the diversity bonus. | 2 | No confusion; no change needed. |
| P57 | Probe ordering favors cheap checks that appear to distinguish alterna… | Lexical terms and first paths define the distance inputs. | 2 | No confusion; no change needed. |
| P58 | The formula combines lexical difference with a different-file indicat… | Distance combines vocabulary and file differences, including an empty-set edge case. | 2 | No confusion; no change needed. |
| P59 | Each probe carries a chosen reliability weight and estimated cost, us… | Reliability and cost are ordering heuristics, not empirical probabilities or costs. | 1 | No confusion; no change needed. |
| P60 | Algorithm~'s first procedure returns a probe list; its second returns… | The two procedures return ordered checks and selected hypotheses; alternatives are declared conflicts. | 2 | No confusion; no change needed. |
| P61 | Source-quote reliability is 0.9, other kinds 0.7; estimated cost is 1… | Constants prioritize static quotes over expensive dynamic checks. | 1 | No confusion; no change needed. |
| P62 | Shared investigations filter handled logical probe IDs; isolated inve… | Shared and isolated roles apply different logical-ID filtering while sharing physical cache. | 2 | No confusion; no change needed. |
| P63 | In the illustration, the different paths of $h_A$ and $h_B$ contribut… | The example shows score–distance tradeoffs without guaranteeing useful alternatives. | 2 | No confusion; no change needed. |
| P64 | The monitor asks whether recent valid rounds produced little accessib… | Monitor samples availability gain, cached repetition, diversity, and actual token use. | 2 | No confusion; no change needed. |
| P65 | A reset requires enough valid rounds and a full recent window, enough… | A reset requires every readiness and affordability gate. | 1 | No confusion; no change needed. |
| P66 | Here $n_0$ is a positive minimum valid-round count, $ and $ Algorithm… | Threshold domains and diagnostics explain the plateau algorithm interface. | 2 | No confusion; no change needed. |
| P67 | The restart estimate uses the latest valid round, not the window's me… | Restart cost uses the latest valid round; efficiency logging is not a trigger. | 1 | No confusion; no change needed. |
| P68 | A reset clears the history window while retaining $n$ and incurred ex… | Reset clears the window but retains cumulative rounds and expenditure. | 2 | No confusion; no change needed. |
| P69 | As defined in Section~, roles share an access scope by default and us… | Portfolio limits apply per access scope; all dialogues reset together. | 1 | No confusion; no change needed. |
| P70 | T7 classifies support by observation kind at the hypothesis level. If… | Any dynamic support can remove all a hypothesis's predictions from the unresolved list. | 2 | An explicit two-prediction example would make the hypothesis-level unresolved rule faster to absorb. |
| P71 | The rebuilt view includes every observation accessible to that scope,… | All accessible observations enter reconstruction, so context remains unbounded. | 1 | No confusion; no change needed. |
| P72 | Retention property. For the reset operation in isolation, the observa… | Reset preserves the observation-ID set by avoiding ledger writes. | 1 | No confusion; no change needed. |
| P73 | The ledger's insertion API rejects a changed payload under an existin… | Insertion protects payload identity but nested records remain directly mutable. | 2 | No confusion; no change needed. |
| P74 | For the illustration, the quote fact survives even if its originating… | Retained facts can be reused without their earlier interpretation. | 1 | No confusion; no change needed. |
| P75 | For a concrete trace of the running example, stipulate two hypotheses… | Synthetic scores and mechanism terms produce a concrete portfolio order. | 2 | No confusion; no change needed. |
| P76 | Table~ completes the synthetic gate calculation. Four valid rounds ea… | Synthetic round history passes the monitor gates. | 2 | No confusion; no change needed. |
| P77 | The reset retains both hypothesis IDs and all three observation IDs, … | Reset preserves IDs and budgets while rebuilding four input groups. | 1 | No confusion; no change needed. |
| P78 | the report-derived behavior, role, and remaining tokens; both hypothe… | The rebuilt request includes behavior, hypotheses, observations, and source context. | 2 | No confusion; no change needed. |
| P79 | The source-presence observation for or True remains static support. T… | Constructed retention does not establish context sufficiency or localization success. | 2 | No confusion; no change needed. |
| P80 | For each retrieved file, the final score is the maximum live hypothes… | Files and symbols have distinct ranking rules and may disagree. | 2 | No confusion; no change needed. |
| P81 | The controller stops at an attempt limit, token/probe/wall limits, a … | Dynamic stopping can inspect the pre-pruning leader rather than the retained pool. | 3 | Name the saved pre-reset pool before explaining the stop rule, or show select/prune/check in a three-step sequence. I reread to establish what “old pool” refers to. |
| P82 | Returned causal abstention uses a different rule: it is false if any … | Causal abstention depends on any historical dynamic causal support, not the current leader. | 2 | No confusion; no change needed. |
| P83 | Algorithm~ expands both ways over known relations using the previous … | Neighborhood expansion is bidirectional and bounded, without coverage guarantees. | 2 | No confusion; no change needed. |
| P84 | The fourteen configurations in Table~ manipulate one implementation; … | Fourteen configurations are variants of the same implementation. | 1 | No confusion; no change needed. |
| P85 | In particular, no_mde and stateless_summary retain typed validation, … | Observation-text controls retain internal typing but omit several model-visible records. | 2 | No confusion; no change needed. |
| P86 | Both controls omit the same model-view content, but no_mde keeps its … | The two observation-text controls differ in dialogue persistence. | 1 | No confusion; no change needed. |
| P87 | Per-call portfolio selection also remains active in no_forgetting and… | Several variants alter ongoing visibility as well as retention, confounding formatting attribution. | 2 | No confusion; no change needed. |
| P88 | The isolated-role condition still reuses physical facts through the c… | Isolated roles share cached facts but not each other's views. | 1 | No confusion; no change needed. |
| P89 | The initial_clue parameter supplies unverified text only on the first… | A first-call unverified clue defines an operational wrong-lead recovery track. | 2 | No confusion; no change needed. |
| P90 | RQ1 uses paired common-case rankings for each primary comparator. RQ2… | Primary and component comparisons use matched cases and seeds within their respective studies. | 2 | No confusion; no change needed. |
| P91 | For conditional recovery, count eligible cases separately for each wo… | Recovery denominators are workflow-specific and do not support paired causal claims. | 2 | No confusion; no change needed. |
| P92 | The additional audit is exploratory and not implemented by the existi… | The proposed extra audit is exploratory and unimplemented. | 1 | No confusion; no change needed. |
| P93 | For recreation, count one event each time a previously pruned hypothe… | Recreation audit measures absent old links among fully reconstructable reappearances. | 2 | No confusion; no change needed. |
| P94 | For logical suppression, the denominator is validated proposals in pr… | Suppression audit counts already-handled proposed IDs and a changed-prediction subset. | 3 | Use proposals as the counting unit throughout; say whether repeated proposals with one handled ID count repeatedly. “Numerator counts the logical probe IDs” momentarily suggests unique-ID counting while the denominator counts proposals. |
| P95 | Both audits reconstruct access scope from the request's role and shar… | Audit scope reconstruction and missingness bound interpretation of event counts. | 2 | No confusion; no change needed. |
| P96 | Requests, responses, and observation artifacts are content-addressed.… | Content addressing and hash links establish limited provenance and tamper evidence. | 2 | No confusion; no change needed. |
| P97 | Token accounting charges model input and output even for invalid resp… | Tokens and physical checks have explicit charging rules; wall limits are not universal deadlines. | 2 | No confusion; no change needed. |
| P98 | Retrieval and learned localization. BugLocator combines report--sourc… | Retrieval and learned execution-based localization use different state and evidence. | 1 | No confusion; no change needed. |
| P99 | Agentic, explanation-guided, and graph-guided search. AutoFL couples … | Agentic and graph systems motivate the comparison without claiming superior navigation. | 2 | No confusion; no change needed. |
| P100 | Memory and restart policies. MemFL constructs project/class summaries… | Prior project memory, feedback, paging, and restart work delimit this within-run combination. | 2 | No confusion; no change needed. |
| P101 | Ledger is the closest execution-state predecessor: it separates repai… | Ledger is the closest state-management predecessor but does not reproduce this restart policy. | 2 | No confusion; no change needed. |
| P102 | Diagnosis, execution evidence, and provenance. Reiter's consistency-b… | Formal diagnosis, execution evidence, and provenance are related but distinct foundations. | 2 | No confusion; no change needed. |
| P103 | This work studies one scoped-assessment and portfolio-restart policy.… | Practical significance requires useful policy findings or repeatable failure mechanisms. | 1 | No confusion; no change needed. |
| P104 | Only restricted Agentless and RGFL localization components are implem… | Only restricted Agentless and RGFL components are executed comparisons. | 1 | No confusion; no change needed. |

## Technical objects: plain-language reconstruction

| Object | Inputs → outputs | Why needed / readability |
|---|---|---|
| Example listing | Explicit false option → normalized true flag passed toward rendering | Demonstrates symptom/cause separation; immediate with basic Python. |
| Notation table | Names of repository, state, budgets, and monitor values → shared shorthand | Supports the algorithms; ordinary reference effort (2). |
| M1–M4 | Report/source/proposals/check results → behavioral, structural, hypothesis, and investigation records | Separates reported behavior, code facts, explanations, and checks; understandable (2). |
| T1–T7 table | Raw report/source and proposed checks → validated records, assessments, reconstructed requests | Provides the pipeline map; clear at 2. |
| Flow figure | Public case → retrieval, role proposal, execution, ledger, monitor, reset, next request | Makes preserved observations versus cleared conversations visible; clear at 2. |
| Controller algorithm | Public report, source revision, backend, configuration, budgets → rankings, records, costs, audit, abstention | Defines attempted versus valid rounds and reset placement; 2 with surrounding explanations. |
| Probe executor/cache/ledger | Validated check and source/procedure identity → reused or new verified observation | Avoids physical reexecution and preserves provenance. Logical handled IDs are a separate filter; that distinction needs the P52–53 fix. |
| Distance equation | Mechanism word sets and first-location paths → number between zero and one | Supplies cheap diversity, not semantic independence; 2. |
| Probe ordering | Probes, live hypotheses, handled IDs, heuristic costs/reliability → priority-sorted remaining probes | Allocates bounded checks; 2. |
| Portfolio selection | Live hypothesis scores, pairwise distances, bound k → at most k selected hypotheses | Retains alternatives while favoring scored candidates; 2. |
| Plateau algorithm | Recent valid-round samples, budgets, thresholds, cumulative count → reset Boolean and diagnostics | Makes the heuristic trigger reproducible; conjunction and strict affordability inequality are readable at 2. |
| Reset algorithm / retention property | Scoped hypothesis pools, dialogues, observation ledger, monitor → pruned pools, cleared dialogues/window, unchanged observation IDs | Defines exactly what forgetting means and what its invariant does not prove; 2. |
| T7 reconstruction | Accessible records, behavior, retained hypotheses, role, budget, source windows/relations → next model request | Restores usable input while risking large contexts and missing interpretation links; 2. |
| Constructed gate table | Four synthetic rounds, scores, 16k budget, configured gates → passing reset and retained portfolio | Concrete arithmetic makes controller behavior understandable; 2. It does not measure model recovery. |
| File and symbol rankings | Live scores/locations and retrieval order → two separately ordered candidate lists | Gives the actual evaluation output; 2. |
| Stop and abstention rules | Current/saved pools, dynamic support and historical assessments → stop reason and causal-abstention flag | Distinguishes execution termination from causal claims; old-pool branch needs P81 clarification. |
| Neighborhood algorithm | Ordered seeds, resolved source relations, hop bound → seed-first expanded file list | Connects symptom to structurally related files with finite work; 2. |
| Defaults table | Chosen engineering constants → reproducible library configuration | Distinguishes choices from learned/calibrated values; 2. |
| Variants table | Full prototype plus selected policy/view changes → fourteen comparison configurations | Explains what each contrast can test; 2, supported by explicit attribution limits. |
| Misdirection track | Rank-two retrieval clue, first request, labels and first valid leader → workflow-specific eligible recovery cases | Operationalizes following a wrong lead without claiming psychological fixation; 2. |
| Proposed trajectory audits | Ordered requests/proposals, retained/pruned IDs, handled sets, scope and artifacts → recreation/link-loss and suppression event counts | Tests policy edge cases; reconstruction audit is 2, suppression counting unit is 3 (P94). |
| Related-work comparison table | Cited methods and reported state/evidence boundaries → comparison of memory, reset, and output granularity | Positions the contribution without equating missing reports with missing capability; 2. |

## Five-sentence comprehension summary

MORPH-FL investigates a Python bug report by retrieving source files, proposing explanations and checks, and ranking candidate files and symbols within fixed budgets. It stores checked observations outside role conversations and distinguishes the recorded result from an assessment of a particular prediction. When recent valid rounds satisfy heuristic plateau and affordability gates, it clears dialogue and retains a small scored, lexically diverse hypothesis portfolio while preserving every observation ID. Retention does not guarantee that old interpretations remain linked, that reconstructed requests are sufficient or small enough, or that static support establishes the runtime cause. The prospective study compares complete memory-policy packages using patch-location proxies and cost measures, with exploratory audits for interpretation loss and suppressed reassessment, and currently reports no empirical findings.
