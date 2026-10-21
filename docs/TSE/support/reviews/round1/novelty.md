# Independent reviewer 2: novelty and positioning, round 1

Recommendation: **Weak Reject** for the scoped front half. Confidence: **High (4/5)** on the specified method and its positioning; moderate on completeness of the rapidly changing literature. Reviewed Introduction, Background, Approach, and Related Work in `docs/TSE/main.tex`; inspected later outlines only for consistency. Inspected implementation state, policies, reconstruction, and baseline documentation. Did not consult writer support notes or other reviews. Primary-source searches performed independently on 2026-10-20.

## Assessment

The paper asks a worthwhile, quite specific question: can an investigator clear conversation while preserving checkable observations and a small alternative portfolio, and does that combination earn its cost over simpler memory? The implemented boundary is described with unusual honesty. The front half is coherent enough to support a rigorous study. However, the closest-work set omits an especially close 2026 coding-agent execution ledger, and the principal summary control is materially weaker than its everyday name suggests. Consequently, novelty and the proposed decisive comparison remain insufficiently established. This is not a rejection because the draft has explicitly reserved its empirical findings: those are unresolved publication evidence requirements, not fabricated or contradictory claims.

## Strengths

1. The observation/assessment/dialogue distinction is operational rather than metaphorical. Sections II-A and III-D/H separate static facts, interpretation, and causal support, and distinguish record retention from useful reconstruction and ranking benefit.
2. The contribution statement explicitly disclaims novelty for memory and restarts individually. Related Work acknowledges MemFL and Repository Memory, distinguishes repair success from localization, and labels local upstream adaptations accurately.
3. The source-only benchmark boundary, unreviewed patch proxies, null confidence, sequential roles, heuristic utility, unbounded reconstruction, and literal stopping semantics are disclosed. The sampled controller/policy/reconstruction source agrees with those descriptions.
4. The example is properly labeled synthetic; it does not masquerade as an observed recovery. Negative findings are allowed by the RQs.

## Concerns and concrete remedies

### 1. Major — missing closest predecessor for the ledger/reuse contribution

Location: Introduction paragraphs 4–6 and contribution list; Related Work “Memory and restart policies,” “Diagnosis, execution evidence, and provenance,” and Table of closest systems.

[Turning Interaction History into Execution State: A Runtime Layer for Long-Horizon Coding Agents](https://arxiv.org/html/2608.00808v1), posted August 2026, introduces Ledger. Its method separates semantic reasoning from deterministic state, records observations and attempted commands, renders a state view into prompts, and returns still-valid earlier results in place of redundant execution. This is substantially closer to MORPH-FL's versioned observation ledger, physical cache, and reconstructed request than MemGPT or PROV alone. Ledger's observation records and modification counters also address validity of previously observed file ranges. It is a repair-agent runtime rather than an explicit fault-hypothesis restart system, so this does **not** establish that MORPH-FL is redundant. It does mean the current novelty comparison misses a central neighbor.

Remedy/type: literature and argument revision. Add a primary-method comparison covering ledger content/validity, observation versus interpretation, redundant-action mediation, history retention, and restart/portfolio policy. State the residual contribution as prediction-scoped assessment plus an observation-retaining restart/portfolio experiment, if that remains accurate. Do not imply Ledger studies restarts without evidence. Decide explicitly whether a ledger-only/no-restart control already present is a sufficient conceptual comparator; a full reproduction is not automatically required. The present invariant alone is too elementary to distinguish the work from ordinary external-state persistence.

### 2. Major — “text summary” alternative does not isolate the advertised question

Location: Introduction paragraph 5 and RQ3; III-A; III-J variants; Table of controlled variants. Source: `search/controller.py` around 209–247 and `search/config.py` variant definitions.

The `stateless_summary` is a concatenation of observation location and JSON output. It removes hypothesis mechanisms, explicit predictions, behavior state, and relations; it also uses no prior dialogue on every call rather than adaptive resets. This is a useful deliberately simple evidence-text baseline, but it is not a conventional generated investigation summary. A positive contrast could arise from omitted semantic content, different relation access, or different history policy, rather than structured prediction links earning their cost. The manuscript partially acknowledges a presentation package, but still presents the summary alternative as the principal test of its central complexity argument.

Remedy/type: comparison specification and claim alignment. Define exactly what the baseline summarizes, whether any model writes it, and what information it retains. Either introduce a content-matched unstructured serialization/summary with matched reset schedule and relation exposure, or narrow the main claim to superiority over this particular evidence-text policy. No additional positive finding is required. Explicitly separate representation, retained information, and reset timing in the interpretation of contrasts.

### 3. Moderate — current memory comparison hides materially different memory lifetimes

Location: Introduction summary paragraph; Related Work memory paragraph and closest-systems table.

[MemFL](https://arxiv.org/html/2506.03585v1) constructs debugging guidance using a small pseudo-training bug set, including buggy and patched methods, then evaluates on held-out folds. Its dynamic memory is not simply a summary of the current investigation. [Repository Memory](https://arxiv.org/html/2510.01003v2) retrieves pre-issue commits/linked issues and functionality summaries. These are mainly cross-issue/project knowledge, whereas MORPH-FL's evidence ledger is within-run state at one fixed revision. The current descriptions are broadly correct, but the table's single “state across steps/trials” column obscures this useful distinction.

Remedy/type: positioning precision. Add memory lifetime and construction supervision (current run, past issues, project summaries, scored optimization trials) to the comparison or nearby prose. This strengthens a legitimate distinction without claiming other memories fail.

### 4. Moderate — newer adaptive repair memory should be assessed, not silently excluded

Location: Related Work memory subsection/table.

[AdaRepair-Mem](https://arxiv.org/html/2609.20130v1), September 2026, stores stage-specific repair experiences and routes memory to localization as well as other stages. Its Section IV-B7 explicitly evaluates file localization. It differs from current-run evidence-preserving resets, but it is relevant to the paper's 2026 memory-plus-localization frontier. This is a separate issue from demanding all modern repair agents as executable baselines.

Remedy/type: bounded literature revision. Discuss its cross-task stage-aware retrieval and explain why the proposed within-investigation restart boundary is different. No need to reproduce its repair success figures or compare those numerically with patch proxies. Extend the search cutoff statement and characterize the search as “examined systems,” as the table already sensibly does.

### 5. Moderate — score accumulation can overwhelm the diversity term

Location: III-D/E and III-H, score weights, portfolio selection, final ranking.

Static support increments are additive, while the diversity bonus is at most one. Mechanism/probe identity permits repeated semantically similar proposals to acquire separate records, and cached observations can support distinct hypotheses. Thus the ranking and pruning may favor checkable source features or accumulated checks rather than discriminating explanations. The text correctly says these are not probabilities, but that disclaimer does not explain why the score is an appropriate survival criterion for an anti-fixation portfolio. Equation (1) and Algorithm 3 make this limitation inspectable, rather than erroneous.

Remedy/type: design rationale and empirical boundary. Explain the intended tradeoff and its plausible failure cases; make score-margin versus diversity and support-count behavior observable in trajectory analysis. If no sensitivity/normalization comparison is planned, frame this as one heuristic instantiation, and avoid general conclusions about the value of hypothesis diversity from its failure. No invented validation or retuning is requested.

### 6. Minor — too much implementation exception detail interrupts the core mechanism

Location: III-C/D/H/I and engineering constants table.

The exposition repeatedly shifts from the central state boundary to incidental behavior: class symbols, whole-file AST matching, prediction reassessment suppression, pre-pruning stop references, and historical run-level abstention. These disclosures are valuable but obscure the minimal design and make accidental prototype behavior look like a methodological choice.

Remedy/type: presentation. Introduce a compact “prototype semantics and limits” subsection/table; keep operationally necessary behavior in the algorithms and move less central caveats there. Do not hide the limitations or silently describe an idealized implementation.

## Independent literature verification

The primary [forgetting paper](https://arxiv.org/pdf/2610.20563), Section 3, supports the manuscript's distinction: it clears sessions and search state, retaining the best candidate and score in scored optimization. Its conclusion explicitly leaves when to forget and what to retain as future questions. The existing description is fair; it does not prove benefit in localization. The primary MemFL and Repository Memory descriptions also support the broad current positioning, subject to the lifetime distinctions above. Ledger is the most important newly identified omission; AdaRepair-Mem is a secondary omission. Search results also surfaced other 2026 memory papers, but I do not infer their full capabilities from titles or require citations to every search hit.

## Questions for the authors

- What information should an adequate unstructured investigation summary retain, and does the implemented baseline retain it?
- Which contribution remains beyond deterministic execution ledgers plus established restart search: explicit scoped assessment, the portfolio, adaptive timing, or their tested combination?
- How frequently can source-fact score margins make a diverse alternative impossible to retain, and what trajectory evidence will reveal this?
- Will the final discussion distinguish within-run observation memory from project/history memory throughout?

## Must fix before a publishable submission

Address Ledger directly and sharpen the residual novelty; specify and correctly bound the summary comparison; distinguish memory lifetimes and assess the recent stage-aware memory predecessor; preserve the source-only/patch-proxy limits in all eventual claims. Completed matched-budget findings, reconstruction-failure accounting, and eligible wrong-lead trajectories remain necessary to establish practical significance, but none should be invented to repair this front half. The outlined empirical study can resolve these evidence requirements without changing the honest current premise.
