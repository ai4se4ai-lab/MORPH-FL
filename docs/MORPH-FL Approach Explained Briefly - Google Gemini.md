> **Implementation alignment note:** This supplied AI-generated conversation is preserved as a design discussion. Its claims about mathematical guarantees, graph-edit distance, expected entropy reduction, calibrated confidence, causal slices and performance are not established results. Use [ALGORITHMS.md](ALGORITHMS.md), [CLAIM_ALIGNMENT.md](CLAIM_ALIGNMENT.md) and the [measured RQ discussion](../experiments/baselines/results/research_questions.md) for paper-ready definitions and evidence.

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 



**can you explain this approach in 3 paragraphs in simple language: # MORPH-FL: Model-Driven Hypothesis Evolution with Strategic Forgetting for Bug Localization** 

**<mark></mark>** 

**Here is an explanation of the MORPH-FL research approach in three simple paragraphs:** 

**MORPH-FL (Model-Driven Hypothesis Evolution with Strategic Forgetting for Bug Localization) is a new research concept designed to fix a major flaw in AI coding assistants: when they investigate a software bug, they tend to latch onto their first guess and stubbornly reread the same wrong files over and over. Instead of letting an AI agent accumulate a messy, ever-growing chat history that encourages this kind of reasoning lockin, MORPH-FL translates a bug report and a codebase into structured, testable engineering models. These models separate visible symptoms from hidden causes and represent competing explanations as falsifiable theories rather than simple file guesses.** 

**To prevent the AI from getting stuck in conversational ruts, MORPH-FL introduces a strategy called Portfolio-Preserving Forgetting. When an investigation stalls or starts chasing its tail, the system periodically wipes out the agents' bloated chat transcripts, speculative brainstorming, and redundant file-searching baggage. However, it does not throw away hard facts. It carefully retains a compact snapshot of verified test results, provenance data, and a diverse portfolio of 2 to 4 competing hypotheses, using them to instantly spin up a fresh team of agents with clean slates.** 

**Finally, rather than relying on unstructured agent debates that often amplify wrong assumptions, MORPH-FL assigns investigators distinct epistemic roles—such as behavioral, structural, and skeptical investigators—to rigorously test and challenge explanations. These agents execute specific, budget-controlled probes to gather differentiating evidence rather than guessing blindly. By combining explicit software models with intelligent, evidencepreserving memory resets, MORPH-FL aims to make AI-powered bug localization significantly more accurate, cost-effective, and robust on complex cross-file bugs.** 

https://gemini.google.com/app/55303d6a1facc754 

1/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Break down the four linked model layers (M1 to M4) in MORPH-FL and how they interact.** 

**In the MORPH-FL framework, Model-Driven Engineering (MDE) is used to replace unstructured chat transcripts and file guessing with explicit, machine-processable abstractions. The architecture is built on four linked model layers that span from user reports to verified empirical evidence.** 

# **1. Breakdown of the Four Layers (M1 to M4)** 

|**Layer**|**Name**|**Core Purpose**|**Key Componen**|
|---|---|---|---|
|**M1**|**Symptom &**<br>**Behavioral Model**|**Captures the**<br>**discrepancy between**<br>**expected and**<br>**observed behavior.**|**Triggers, precon**<br>**expected/obser**<br>**outcomes, and**<br>**invariants (e.g.,**<br>**stored_order**<br>**== payable_t**<br>**).**|
|**M2**|**Structural & System**<br>**Model**|**Represents the static**<br>**and dynamic**<br>**architecture of the**<br>**repository.**|**Components, m**<br>**call graphs, data**<br>**edges, state**<br>**transitions, and**<br>**locations with**<br>**provenance/con**<br>**ratings.**|
|**M3**|**Fault Hypothesis**<br>**Model**|**Replaces file-ranking**<br>**lists with explicit,**<br>**falsifiable causal**<br>**explanations.**|**Candidate fault**<br>**elements, propo**<br>**failure mechanis**<br>**predicted**<br>**observations, an**<br>**support/contrad**|
||||**levels.**|



https://gemini.google.com/app/55303d6a1facc754 

2/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

|**Layer**|**Name**|**Core Purpose**|**Key Componen**|
|---|---|---|---|
|**M4**|**Investigation &**|**Manages how**|**Test/probe plan**|
||**Evidence Model**|**hypotheses are tested**<br>**under strict resource**|**generated asse**<br>**observed runtim**|
|||**and cost budgets.**|**results, model**|
||||**traceability links**<br>**cost metrics.**|



# **2. How the Layers Interact** 

**The four layers do not operate in isolation; they form a continuous, closed-loop transformation and verification pipeline during bug localization:** 

**Initialization (M1 + M2 → M3): When a bug is reported, M1 extracts the formal behavioral contract from the natural language complaint, while M2 parses the codebase into a typed architectural graph. Combining the violated invariant (M1) with the system's data-flow pathways (M2) allows MORPH-FL to generate diverse causal Fault Hypotheses (M3)—pinpointing how an upstream component could corrupt state before reaching the symptom site.** 

**Operational Execution (M3 → M4): Once competing hypotheses (H1, H2, H3, etc.) are established, they must be tested. M4 takes the predicted observations from each hypothesis and translates them into actionable, budgeted probes, unit tests, or static queries designed specifically to discriminate between explanations rather than blindly reading files.** 

**The Feedback Loop (M4 → M3 → M2/M1): Executing the probes in M4 generates hard evidence (e.g., captured arguments, test failures, or trace outputs). This evidence is fed back into M3 to strengthen, weaken, or contradict active** 

**Explain how Portfolio-Preserving Forgetting decides when to trigger a reset and what it safely retains.** 

https://gemini.google.com/app/55303d6a1facc754 

3/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Portfolio-Preserving Forgetting (PPF) is the core adaptation mechanism in MORPH-FL that solves the "reasoning fixation" problem. Instead of letting AI agents spin their wheels in an ever-growing, biased chat history, PPF decides when an investigation has hit a wall and safely cleans the slate without losing hard-won facts.** 

# **1. How PPF Decides When to Trigger a Reset** 

**PPF avoids rigid, fixed-timer resets in favor of a monitored plateau signal. A reset is triggered when empirical signs indicate that the agents are no longer making productive, original progress:** 

**Diminishing Evidence Gain: The rate of discovering new, verified facts drops significantly across recent investigation windows.** 

**Behavioral Loops: Agents begin repeating identical file inspections, duplicate queries, or redundant code-browsing traces.** 

**Hypothesis Convergence (Lock-in): The active hypotheses across different agents have artificially collapsed into the same wrong or overly narrow explanation.** 

**Escalating Costs: The computational cost, token count, or API budget per new discriminating observation climbs too high.** 

**Exploration Threshold: A minimum initial exploration budget has been consumed, ensuring agents have had a fair chance to test their initial ideas before a reset is evaluated.** 

**To prevent wasteful churn, PPF also factors in the cost of restarting, ensuring that short or highly productive agent sessions are never interrupted prematurely.** 

# **2. What PPF Safely Retains vs. Discards** 

**The primary insight of PPF is separating speculative search baggage from epistemically verified knowledge.** 

## **What Gets Forgotten (Discarded)** 

**Full agent conversation transcripts and chat histories.** 

**Verbose chain-of-thought narratives and speculative brainstorming that lacked empirical backing.** 

https://gemini.google.com/app/55303d6a1facc754 

4/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Duplicated retrieval logs and stale task decompositions.** 

**Biased or unverified assumptions that contributed to reasoning fixation.** 

## **What Gets Safely Retained** 

**The Bug Report & Environment: The original issue description, repository commit state, and reproducible test setup.** 

**Verified Observations: All test results, captured runtime values, and stack traces that carry strict provenance and reproducibility records.** 

**Typed Source Links: The underlying system model and versioned code links.** 

**A Diverse Hypothesis Portfolio: A curated, non-redundant set of 2 to 4 defensible competing hypotheses (including the strongest alternative) to ensure the next team explores genuinely different causal pathways.** 

**Crucially, "forgetting" in MORPH-FL is an epistemic reset, not physical deletion. An immutable background log still preserves all historical activity for auditing and research reproducibility, but the newly spawned agents receive only a clean, validated model snapshot.** 

**Break down the 7 model transformations (T1 through T7) that drive the MORPH-FL pipeline.** 

**The MORPH-FL framework operates through seven systematic model transformations (T1 through T7). These transformations bridge the gap between unstructured human bug reports and automated, model-driven reasoning, ensuring that every step of the localization process is explicit, verifiable, and falsifiable.** 

# **The Seven Transformations (T1 to T7)** 

https://gemini.google.com/app/55303d6a1facc754 

5/33 

|**Transformation**<br>10/19/26, 10:29 AM|**Input**<br> **Output**<br>**→**<br>MORPH-FL Approach Explained Bri|**Scientific Role in MORPH-FL**<br>efly - Google Gemini|
|---|---|---|
|**T1: Complaint-to-**|**Natural-language bug report**|**Converts informal prose into**|
|**Contract**|**Symptom / behavioral**<br>**model (M1)**<br>**→**|**explicit, falsifiable behavioral**<br>**expectations, explicitly**<br>**marking any ambiguities.**|
|**T2: Code-to-System**|**Repository + optional**|**Extracts cross-file**|
|**Model**|**runtime traces**<br> **Typed**<br>**architecture and data-flow**<br>**model (M2)**<br>**→**|**relationships, dependencies,**<br>**and data flows that surface-**<br>**level text similarity cannot**<br>**capture.**|
|**T3: Model Composition &**<br>**Slicing**|**Behavioral model (M1) +**<br>**system model (M2) **<br>**Relevant causal slices**<br>**→**|**Narrows down the scope of**<br>**investigation while**<br>**preserving potential nonlocal**<br>**causes and structural**<br>**traceability.**|
|**T4: Explanation Synthesis**|**Causal slices**<br> **Diverse fault**<br>**hypothesis models (M3)**<br>**→**|**Generates alternative, non-**<br>**overlapping failure**<br>**mechanisms rather than just**<br>**differently worded file**<br>**guesses.**|
|**T5: Hypothesis-to-Probe**|**Hypothesis model**<br> **Test,**<br>**probe, static query, or**<br>**counterfactual check (M4)**<br>**→**|**Forces hypotheses to make**<br>**concrete predictions that**<br>**can independently support**<br>**or contradict the**<br>**explanation.**|
|**T6: Evidence-to-Model**<br>**Update**|**Probe execution results**<br>**Revised hypothesis models**<br>**and evidence ledger**<br>**→**|**Ensures that learning persists**<br>**outside agent chat histories,**<br>**updating confidence and**<br>**ranking rigorously.**|



https://gemini.google.com/app/55303d6a1facc754 

6/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Transformation Input → Output Scientific Role in MORPH-FL T7: Model-to-FreshValidated evidence + Implements MDE-guided Context selected hypothesis portfolio strategic forgetting, wiping → Minimal new agent task bloated chat transcripts briefing while retaining hard facts.** 

# **How the Pipeline Flows** 

**1. Ingestion & Modeling (T1–T2): The process begins by parsing what the user observed versus what should have happened (T1), alongside parsing the codebase into a structured architectural graph (T2).** 

**2. Scoping & Hypothesis Generation (T3–T4): MORPH-FL slices the system model against the behavioral contract (T3) to synthesize a diverse portfolio of competing, falsifiable fault explanations (T4).** 

**how mde techniques contribute to more efficient forgetting approach in bug localizations** 

**In Model-Driven Engineering (MDE) approaches like MORPH-FL, model-driven techniques are precisely what make Portfolio-Preserving Forgetting (PPF) efficient and safe. Without MDE, "forgetting" in AI agents usually means wiping chat history and relying on messy text summaries—which often lead to losing critical context or accidentally preserving hidden biases.** 

**MDE transforms forgetting from an arbitrary text-truncation trick into a precise, semanticsaware state reset. Here is how MDE techniques directly enable a more efficient and reliable forgetting approach:** 

# **1. Clean Separation of Structural Signal from Conversational Noise** 

https://gemini.google.com/app/55303d6a1facc754 

7/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Traditional AI agents mix everything into a single, unstructured text stream: tool outputs, file contents, correct deductions, and speculative brainstorming.** 

**The MDE Contribution: MDE explicitly separates the conversational narrative (which is full of bias and fixation) from the formal system and behavioral models (M1–M4). Because the state is stored as typed metamodels rather than prose, the system can completely discard the agent chat transcripts while leaving the underlying model integrity untouched.** 

# **2. Typed Provenance and Immutable Evidence Links** 

**When resetting agents, a major risk is accidentally throwing away hard-won facts or keeping unverified guesses disguised as facts.** 

**The MDE Contribution: MDE enforces strict metamodel constraints where every observation, test result, and causal edge must carry typed provenance (e.g., explicitly linked to a specific test execution or static analysis pass). During a reset, the system can instantly filter out unverified hypotheses while mathematically guaranteeing that all empirically confirmed facts remain intact in an evidence ledger.** 

# **3. Programmatic Diversity in Hypothesis Portfolios** 

**When restarting an investigation, simply telling a fresh agent "try again" often results in it walking down the exact same cognitive path.** 

**The MDE Contribution: Because hypotheses in MORPH-FL are structured objects within an MDE framework (containing specific failure mechanisms, predicted observations, and source elements), the system can algorithmically evaluate the distance or overlap between explanations. This allows the framework to curate a truly diverse portfolio of 2 to 4 non-redundant hypotheses to seed the new agent team, ensuring they explore orthogonal causal paths.** 

# **4. Model Slicing for Minimal, High-Signal Contexts** 

**Giving a restarted agent an entire codebase or a massive text summary overwhelms its context window and invites new fixations.** 

**The MDE Contribution: MDE enables model composition and slicing (T3). When a reset occurs, the framework slices the large architectural system model down to** 

https://gemini.google.com/app/55303d6a1facc754 

8/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**only the components, data-flow paths, and invariants relevant to the retained hypothesis portfolio. The restarted agent receives a compact, highly focused model briefing rather than a bloated history log, drastically reducing token waste and improving reasoning efficiency.** 

**how mde techniques are used in Portfolio-Preserving Forgetting (PPF) and what are the connections betweeen them** 

**In Portfolio-Preserving Forgetting (PPF), Model-Driven Engineering (MDE) is not just a storage format—it is the underlying mechanism that enables the system to clean an agent's memory without losing hard-won facts.** 

**In traditional AI workflows, resetting an agent means clearing a text transcript and providing a plain-text summary. This often leads to "summary decay," where subtle details are lost, or "bias bleeding," where early wrong guesses are preserved in prose. MDE solves this by replacing conversational text with formal, typed metamodels (** **_M_ 1 through** **_M_ 4 ).** 

# **1. Concrete MDE Techniques Used in PPF** 

**MDE Technique** 

**How It Operates in PPF** 

**Metamodel Layering & Distinguishes conversational narrative (untrusted) from Constraints empirical observations (** **_M_ 4 ) and structural dependencies (** **_M_ 2 ). Constraints enforce that an observation cannot exist without a valid execution trace or test provenance.** 

**Model Slicing (** **_T_ 3 )** 

**Programmatically extracts only the minimal sub-graph of code components, dependencies, and invariants relevant to the retained hypotheses, ignoring unneeded context.** 

https://gemini.google.com/app/55303d6a1facc754 

9/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**MDE Technique** 

**How It Operates in PPF** 

**Model Difference & Calculates the structural and semantic "distance" between Distance Metrics candidate hypotheses (** **_M_ 3 ) to algorithmically prevent redundant or overlapping explanations from clogging the retained portfolio. Model-to-Text Automatically serializes the validated model snapshot (** **_K_ ) into Transformation (** **_T_ 7 ) a focused, low-token prompt brief for newly spawned, fresh agent sessions.** 

# **2. Direct Connections Between MDE and PPF** 

**The diagram below illustrates how MDE techniques directly enable the core capabilities of Portfolio-Preserving Forgetting:** 



<!-- Start of picture text -->
+-------------------------------------------------------------------+<br>|                        MDE TECHNIQUES                             |<br>+-------------------------------------------------------------------+<br>| Metamodel     Model Slicing    Typed Provenance   Model Distance  |<br>| Layering      & Slicing (T3)   Constraints        Metrics         |<br>+-----+---------------+-----------------+------------------+--------+<br>|               |                 |                  |<br>| Enables       | Enables         | Guarantees       | Drives<br>v               v                 v                  v<br>+-----+---------------+-----------------+------------------+--------+<br>| Epistemic     | Token & Cost   | Zero Fact Loss   | Portfolio    |<br>| Reset         | Reduction      | across Resets    | Diversity    |<br>+-------------------------------------------------------------------+<br>|                    PPF CORE CAPABILITIES                          |<br>+-------------------------------------------------------------------+<br><!-- End of picture text -->

**Connection A: Metamodel Layering → Epistemic Reset Because search narratives (chat histories) and fault models (** **_M_ 3 ) live in different abstraction layers, PPF can safely execute a destructive reset on the conversation layer while leaving** 

https://gemini.google.com/app/55303d6a1facc754 

10/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**the underlying knowledge layer completely intact.** 

# **Connection B: Typed Provenance Constraints → Zero Fact Loss** 

**In** **_M_ 4 (the Investigation & Evidence Model), every piece of evidence requires an explicit, reproducible reference (e.g., a test assertion result or stack trace ID). When PPF triggers a reset, an automated model filter evaluates every claim:** 

**Verified claims (backed by** **_M_ 4 evidence) are retained in the evidence ledger. Unverified speculation (unsupported agent claims) is automatically purged.** 

# **Connection C: Model Distance Metrics → Portfolio Diversity** 

**A common failure mode in LLM resets is that new agents immediately drift back to the same popular (but wrong) explanation. In PPF, hypotheses in** **_M_ 3 are represented as structured graphs (Location + Failure Mechanism + Predicted Observation). PPF computes graph distance across candidates to select 2 to 4 strictly non-redundant hypotheses, forcing restarted agents to explore orthogonal causal paths.** 

**Connection D: Model Slicing (** **_T_ 3 ) → High-Signal Relaunch Briefing** 

**Instead of feeding a restarted agent a long text summary, transformation** **_T_ 7 takes the sliced system model (** **_T_ 3 ) and converts it into a concise, high-density briefing. This drastically reduces token expenditure while maximizing the agent's focus on unresolved, discriminating questions.** 

**now produce a psudocode of the approach that explain how it works and then explain in using an example** 

**Here is the high-level pseudocode for the MORPH-FL approach, followed by a step-by-step walkthrough using our checkout discount example.** 

# **1. MORPH-FL Pseudocode** 

**<mark></mark>** 

**Plaintext** 

https://gemini.google.com/app/55303d6a1facc754 

11/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**FUNCTION MORPH_FL(bugReport, repository, totalBudget) // Step 1: Ingestion & Model Construction (M1 & M2) behavioralModel = ExtractBehavioralContract(bugReport)        // T1 systemModel = ParseCodebaseToTypedGraph(repository)           // T2** 

**// Step 2: Initialize Investigation State evidenceLedger = InitializeEvidenceLedger(bugReport) hypothesisPortfolio = GenerateDiverseHypotheses(behavioralModel, systemModel) activeAgents = SpawnInvestigators(hypothesisPortfolio) remainingBudget = totalBudget** 

**WHILE remainingBudget > 0 AND NOT IsResolved(hypothesisPortfolio)** 

**// Step 3: Budgeted, Independent Probing (M4 / T5) probes = SelectDiscriminatingProbes(hypothesisPortfolio, evidenceLedger) newObservations = ExecuteProbesIndependently(probes, repository)** 

**// Step 4: Evidence Update & Provenance Tracking (T6) UpdateEvidenceLedger(evidenceLedger, newObservations) UpdateHypothesisPortfolio(hypothesisPortfolio, evidenceLedger)** 

**// Step 5: Evaluate Stagnation & Trigger PPF if Needed (T7) IF CheckStagnation(activeAgents, evidenceLedger) THEN // Portfolio-Preserving Forgetting (PPF) validatedSnapshot = ExtractVerifiedModelSnapshot(evidenceLedger, hypo retainedHypotheses = SelectDiversePortfolio(hypothesisPortfolio)** 

**// Wipe bloated chat transcripts, retain hard facts and models RetireAgents(activeAgents) activeAgents = SpawnFreshAgents(retainedHypotheses, validatedSnapshot END IF** 

**remainingBudget = remainingBudget - CostOfCurrentWindow() END WHILE** 

**// Step 6: Final Causal Explanation & Root-Cause Localization RETURN SynthesizeLocalizationReport(hypothesisPortfolio, evidenceLedger) END FUNCTION** 

**** 

**** 

# 2. Step-by-Step Example Walkthrough 

https://gemini.google.com/app/55303d6a1facc754 

12/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Let's trace how this algorithm handles our shopping cart coupon bug where OrderService.ts incorrectly persists the subtotal (100) instead of the discounted payableTotal (90).** 

## **Step A: Model Initialization (T1 & T2)** 

**Behavioral Model (M1): Extracts the invariant** 

**stored_order_total == payable_total . It notes that when a 10% coupon is applied, the expected stored total is $90.00, but the observed stored total is $100.00.** 

**System Model (M2): Parses the repository into a typed dependency graph ( CheckoutPage → CheckoutController → PricingService → OrderService → OrderRepository ).** 

## **Step B: Hypothesis Portfolio Generation (T3 & T4)** 

**Instead of guessing a single file, MORPH-FL synthesizes a diverse set of competing, falsifiable hypotheses (M3):** 

**H1: CheckoutPage.tsx displays the wrong value.** 

**H2: PricingService.ts computes the discount incorrectly.** 

**H3: OrderService.ts passes the wrong value to persistence.** 

**H4: OrderRepository.ts overwrites a correct total.** 

## **Step C: Exploration & Probing (T5 & T6)** 

**Agents are assigned distinct epistemic roles to test these explanations:** 

**The dynamic investigator runs a test and observes that PricingService successfully computes $90.00 (contradicting H2).** 

**However, inspection shows that OrderRepository.save receives $100.00.** 

**This observation is recorded with strict test provenance in the Evidence Ledger (M4), strengthening H3 and weakening H1 and H4.** 

## **Step D: Stagnation & Portfolio-Preserving Forgetting (T7)** 

**Suppose agents initially spent too much time reading UI code ( CheckoutPage.tsx ) before discovering the pricing test result. Their conversation logs are bloated with repetitive file-** 

https://gemini.google.com/app/55303d6a1facc754 

13/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**browsing traces.** 

**The PPF Trigger: The system detects a plateau (low new evidence gain, repetitive inspections).** 

**What is Forgotten: The bloated chat transcripts and speculative UI brainstorming are wiped clean.** 

**What is Retained: The verified observation (PricingService returns 90, but save receives 100) and a narrowed, diverse hypothesis portfolio focusing on H3 and H4.** 

**The Relaunch: A fresh agent team is spawned with a clean slate, receiving only the compact model snapshot and a focused briefing to trace the data flow directly into OrderService.ts .** 

## **Step E: Final Localization Result** 

**The framework pinpoints services/OrderService.ts and outputs a rigorous, inspectable causal chain:** 

**1. PricingService correctly computes discounted payableTotal = 90 .** 

**2. OrderService incorrectly substitutes cart.subtotal = 100 into the persistence call.** 

**3. Supported by captured test arguments and static def-use paths.** 

**if is want to write a paper about this approach for TSE what other psudo code I have to provide to clarify the approach** 

**For a top-tier archival journal like IEEE Transactions on Software Engineering (TSE), reviewers look for formal rigor, reproducibility, and clear algorithmic definitions. A single high-level loop is not enough; you need to unpack the internal decision-making mechanics that differentiate MORPH-FL from standard agentic workflows.** 

**To satisfy TSE rigor, you should include four additional, granular pseudocode algorithms (or formal specifications) that detail the core methodological innovations.** 

# **1. Stagnation Detection & Adaptive PPF Triggering Algorithm** 

https://gemini.google.com/app/55303d6a1facc754 

14/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Why TSE reviewers want this: Reviewers will immediately ask: "How do you know when to forget? Isn't a reset just an arbitrary timer?" This algorithm formalizes the monitored plateau signal, showing that resets are driven by measurable epistemic stagnation rather than guesswork.** 

**Plaintext** 

# **<mark></mark>** 

**FUNCTION EVALUATE_STAGNATION(activeAgents, evidenceLedger, searchMetrics, budget) // 1. Compute recent evidence gain rate over window W recentEvidenceGain = CountNewVerifiedObservations(evidenceLedger, window = W)** 

**// 2. Compute behavioral repetition and inspection overlap repetitionScore = MeasureDuplicateFileInspections(activeAgents, window = W)** 

**// 3. Compute semantic similarity / collapse among active hypotheses hypothesisDistance = CalculatePortfolioDiversity(activeAgents.hypotheses)** 

**// 4. Compute cost efficiency slope costPerNewEvidence = CurrentTokenOrDollarCost(activeAgents) / MAX(1, recentEv** 

**// 5. Evaluate combined plateau condition isStagnant = (recentEvidenceGain < THRESHOLD_GAIN)** 

**AND (repetitionScore > THRESHOLD_REPETITION** 

**OR hypothesisDistance < THRESHOLD_DIVERSITY) AND (budget.consumed > MIN_INITIAL_EXPLORATION_BUDGET)** 

**RETURN isStagnant, {recentEvidenceGain, repetitionScore, hypothesisDistance} END FUNCTION** 

** ** 

# **2. Information-Gain Probe Selection & Ranking Algorithm** 

**Why TSE reviewers want this: This details Transformation** **_T_ 5 , proving how MORPH-FL avoids random code reading by selecting probes that explicitly maximize disagreement between competing hypotheses.** 

**<mark></mark>** 

**Plaintext** 

https://gemini.google.com/app/55303d6a1facc754 

15/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**FUNCTION SELECT_DISCRIMINATING_PROBES(hypothesisPortfolio, systemModel, evidenceL candidateProbes = {}** 

**// 1. Generate potential probes from hypothesis predictions FOR EACH h IN hypothesisPortfolio DO predictions = h.predictedObservations FOR EACH p IN predictions DO probe = TranslatePredictionToExecutableProbe(p, systemModel) candidateProbes.add(probe) END FOR END FOR** 

**// 2. Score probes by expected information gain (discrimination value) FOR EACH probe IN candidateProbes DO // Measure how effectively this probe splits the active hypothesis set expectedDisagreementReduction = CalculateEntropyReduction(hypothesisPortf estimatedCost = EstimateExecutionCost(probe) probe.utilityScore = expectedDisagreementReduction / estimatedCost END FOR** 

**// 3. Filter unsafe, redundant, or unaffordable probes validProbes = FILTER(candidateProbes, p => p.isSafe AND NOT IsRedundant(p, ev // 4. Return top-k utility probes RETURN SORT_BY_UTILITY_DESC(validProbes) END FUNCTION** 

**** 

**** 

# 3. Evidence-Preserving State Reconstruction (The Reset Operator) 

Why TSE reviewers want this: This formalizes the exact mechanics of Transformation **_T_ 7** . Reviewers need to see the mathematical and structural boundary between what is destroyed (chat baggage) and what is preserved (provenance-backed models). 

**Plaintext** 

**<mark></mark>** 

**FUNCTION EXECUTE_PORTFOLIO_PRESERVING_RESET(sessions, hypotheses, evidenceLedger) // 1. Archive full run history for experimental auditing (immutable log) AuditLog.StoreFullSessions(sessions)** 

https://gemini.google.com/app/55303d6a1facc754 

16/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**// 2. Extract strictly verified evidence with valid provenance pointers verifiedSnapshot = SELECT e FROM evidenceLedger WHERE e.status == "VERIFIED" A** 

**// 3. Select a bounded, diverse subset of non-redundant hypotheses retainedHypotheses = SELECT_DIVERSE_PORTFOLIO(hypotheses, count = 3)** 

**// 4. Construct the minimal model context snapshot K modelSnapshot K = { evidence: verifiedSnapshot, portfolio: retainedHypotheses, unresolvedQuestions: ExtractUnresolvedInvariants(retainedHypotheses) } // 5. Destroy bloated agent working context FOR EACH s IN sessions DO s.DestroyChatTranscript() END FOR** 

**// 6. Transform model snapshot into clean, distinct agent briefs freshBriefs = TRANSFORM_MODEL_TO_BRIEFS(K)** 

**RETURN SpawnFreshAgents(freshBriefs) END FUNCTION** 

 

 

4. Semantic Model Slicing Algorithm ( **_T_ 3** ) 

Why TSE reviewers want this: Demonstrates how MDE techniques reduce context window bloat by slicing the system graph against the behavioral contract. 

**Plaintext** 

**<mark></mark>** 

**FUNCTION SLICE_SYSTEM_MODEL(systemModel, behavioralModel) // 1. Identify symptom entry point from bug report invariant symptomNode = FindSystemElementByLocation(systemModel, behavioralModel.violat** 

**// 2. Perform backward slicing along typed data-flow and control-flow edges backwardSlice = ExtractBackwardDependencies(systemModel, symptomNode, maxDept** 

**// 3. Perform forward slicing from potential trigger sources** 

https://gemini.google.com/app/55303d6a1facc754 

17/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**forwardSlice = ExtractForwardDependencies(systemModel, behavioralModel.trigge** 

**// 4. Intersect slices with active hypothesis candidate elements causalSlice = INTERSECT(backwardSlice UNION forwardSlice, activeHypothesisEle** 

**// 5. Return minimized model sub-graph with retained typed edge metadata RETURN ConstructSubGraph(systemModel, causalSlice)** 

**END FUNCTION** 

**the reviewres might ask how thresholds and const values are defined in EVALUATE_STAGNATION. the appraoch must be general enough and not just of a usecase** 

**To satisfy top-tier software engineering reviewers (e.g., for TSE or TOSEM), you cannot present thresholds as "magic numbers" tuned specifically for one benchmark or toy example. Reviewers expect a grounded, adaptive, or empirically calibrated thresholding framework that generalizes across projects, repository sizes, and bug types.** 

**Here is how you can address this question rigorously in your paper, along with a formal methodology section to include in your text.** 

# **1. The Methodological Strategy for Threshold Generalization** 

**Instead of hardcoding static constants, MORPH-FL defines its hyperparameters through three complementary strategies:** 

**1. Normalized/Relative Metrics (Scale Independence): Rather than using absolute token counts or raw file counts, rates are measured relative to the project size (e.g., fraction of total repository files inspected) or moving averages over rolling investigation windows.** 

**2. Empirical Calibration on a Validation Split: Values are tuned strictly on a disjoint validation set (e.g., historical bug fixes from a separate dataset or time period) and held constant during evaluation on test benchmarks.** 

https://gemini.google.com/app/55303d6a1facc754 

18/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**3. Adaptive Dynamic Baselines: Thresholds scale dynamically based on the complexity of the task (e.g., budget remaining or size of the call graph slice).** 

# **2. Parameter Definitions & Selection Rationale** 

**You can directly incorporate a table like this into your paper’s methodology section to explain each constant in EVALUATE_STAGNATION :** 

|**Threshold / Constant**|**Definition**|**Default Range /**|**S**|
|---|---|---|---|
|||**Formula**||
|**W** **(Window Size)**|**Rolling window of**|**_W_** **∈[3,** **5]**|**B**|
||**consecutive probe**|**investigation steps**|**r**|
||**executions / tool calls**||**n**|
||**used to evaluate**||**p**|
||**recent progress.**||**la**|
||||**o**|
|**THRESHOLD_GAIN**|**Minimum rate of new,**|**(or**<br>**Δ****_E_/****_W_** **≤0**<br>**<** **1**|**I**|
||**verified observations**|**new verified fact)**|**s**|
||**added to the evidence**||**y**|
||**ledger per window**<br>**.**<br>**_W_**||**e**<br>**o**|
|**THRESHOLD_REPETITION**|**Jaccard overlap of**|**_J_(****_A_**<br> **,** **_A_**<br> **)** **≥**<br>**_t_**<br>**_t_−1**<br>**0.70**|**Q**|
||**inspected files/nodes**||**lo**|
||**across the last**<br>**_W_**||**r**|
||**iterations.**||**t**<br>**lo**|
|**THRESHOLD_DIVERSITY**|**Minimum mean**|**_D_(****_H_)** **<** **0.30**|**D**|
||**pairwise**|**(Normalized Graph /**|**lo**|
||**semantic/structural**|**Vector Distance)**|**c**|
||**distance between**||**c**|
||**active hypotheses in**||**r**|
||**.**<br>**_M_**<br> **3**||**s**|



https://gemini.google.com/app/55303d6a1facc754 

19/33 

|10/19/26, 10:29 AM<br>M|ORPH-FL Approach Explained Briefly -|Google Gemini||
|---|---|---|---|
|**Threshold / Constant**|**Definition**|**Default Range /**<br>**Formula**|**S**|
|**MIN_INITIAL_EXPLORATION_BUDGET**|**Minimum budget**|**of total**<br>**10%** **−15%**|**P**|
||**fraction or probe**|**token/probe budget**|**r**|
||**count consumed**||**h**|
||**before stagnation**<br>**checks are enabled.**||**a**|



# **3. How to Write This in the Paper (Draft Text)** 

**You can adapt the following text for the Methodology / Parameter Setup section of your TSE paper:** 

## **Handling Stagnation Thresholds and Generalizability** 

**A common concern in adaptive search mechanisms is the risk of overfitting hyperparameters to specific benchmarks. In MORPH-FL, thresholds in EVALUATE_STAGNATION are designed to be scale-invariant and domainagnostic by operating on normalized metrics and dynamic windows rather than absolute values:** 

**1. Scale-Invariant Repetition Metrics: The file inspection repetition score uses a rolling Jaccard similarity index over visited nodes rather than absolute counts, ensuring identical behavior on 10-file modules and 10,000-file enterprise repositories.** 

**2. Structural Distance Metrics: THRESHOLD_DIVERSITY measures the average pairwise Graph Edit Distance (GED) across the candidate fault subgraphs in** **_M_ 3 . Disagreement is evaluated on topology and causal mechanisms, independent of programming language or code style.** 

**Show all 5 pseudocode algorithms for MORPH-FL formatted and formatted for a TSE paper submission.** 

https://gemini.google.com/app/55303d6a1facc754 

20/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Here is the complete suite of five formal pseudocode algorithms formatted specifically for a top-tier archival journal submission (such as IEEE Transactions on Software Engineering). Together, they define the algorithmic core, verification loops, and adaptation mechanics of MORPH-FL.** 

## **Algorithm 1: The Main MORPH-FL Localization Loop** 

**Plaintext** 

**<mark></mark>** 

**ALGORITHM: MORPH-FL Localization Loop INPUT: Bug report B, code repository R, total execution budget C OUTPUT: Ranked fault locations with causal explanations and evidence ledger** 

**1: MB ← ExtractBehavioralContract(B)                           // Transformation 2: MR ← ParseCodebaseToTypedGraph(R)                          // Transformation T 3: E  ← InitializeEvidenceLedger(B)** 

**4: H  ← SynthesizeHypothesisPortfolio(MB, MR)                 // Transformation T4 5: A  ← SpawnInvestigators(H)** 

**6: c_rem ← C 7:** 

- **8: WHILE c_rem > 0 AND NOT IsResolved(H) DO** 

**9:     // Step A: Select and execute budgeted, discriminating probes (T5) 10:    Probes ← SelectDiscriminatingProbes(H, MR, E) 11:    Obs    ← ExecuteProbesIndependently(Probes, R) 12: 13:    // Step B: Update evidence ledger and hypotheses (T6) 14:    UpdateEvidenceLedger(E, Obs) 15:    UpdateHypothesisPortfolio(H, E) 16: 17:    // Step C: Evaluate stagnation and trigger Portfolio-Preserving Forgetting 18:    IF EvaluateStagnation(A, E, H, c_rem) THEN 19:        Snapshot_K ← ExtractVerifiedModelSnapshot(E, H) 20:        H_diverse  ← SelectDiversePortfolio(H, count = 3) 21:        RetireAgents(A) 22:        A          ← SpawnFreshAgents(H_diverse, Snapshot_K) 23:    END IF 24: 25:    c_rem ← c_rem - CostOfCurrentWindow() 26: END WHILE** 

https://gemini.google.com/app/55303d6a1facc754 

21/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**27:** 

**28: RETURN SynthesizeLocalizationReport(H, E)** 

## **Algorithm 2: Stagnation Detection & Adaptive PPF Triggering** 

### **Plaintext** 

# **<mark></mark>** 

**ALGORITHM: EvaluateStagnation INPUT: Active agent sessions A, evidence ledger E, hypothesis portfolio H, remain OUTPUT: Boolean decision (isStagnant) and diagnostic metrics** 

**1: W ← 4 // Rolling investigation window size 2: recentGain ← CountNewVerifiedObservations(E, window = W) 3: repScore   ← MeasureDuplicateFileInspections(A, window = W) 4: divScore   ← CalculatePortfolioDiversity(H.elements) 5: costSlope  ← CurrentTokenCost(A) / MAX(1, recentGain) 6: 7: // Check scaled epistemic plateau condition 8: consumedBudget ← TotalBudget - c_rem 9: minExplorationReached ← (consumedBudget >= 0.15 * TotalBudget) 10: 11: isStagnant ← minExplorationReached 12:               AND (recentGain < THRESHOLD_GAIN) 13:               AND (repScore > THRESHOLD_REPETITION OR divScore < THRESHOLD_DIV 14: 15: RETURN isStagnant, {recentGain, repScore, divScore}  ** 

## **Algorithm 3: Information-Gain Probe Selection & Ranking** 

**Plaintext** 

**<mark></mark>** 

**ALGORITHM: SelectDiscriminatingProbes INPUT: Hypothesis portfolio H, system model MR, evidence ledger E OUTPUT: Ordered list of executable probes ranked by utility score 1: candidateProbes ← ∅ 2: FOR EACH h IN H DO** 

https://gemini.google.com/app/55303d6a1facc754 

22/33 

10/19/26, 10:29 AM MORPH-FL Approach Explained Briefly - Google Gemini **3:     FOR EACH pred IN h.predictedObservations DO 4:         p ← TranslatePredictionToProbe(pred, MR) 5:         candidateProbes ← candidateProbes ∪ {p} 6:     END FOR 7: END FOR 8: 9: FOR EACH p IN candidateProbes DO 10:    // Compute expected reduction in hypothesis entropy (information gain) 11:    entropyReduction ← CalculateEntropyReduction(H, p) 12:    estCost          ← EstimateProbeExecutionCost(p) 13:    p.utilityScore   ← entropyReduction / estCost 14: END FOR 15: 16: validProbes ← FILTER(candidateProbes, p => p.isSafe AND NOT IsRedundant(p, E) 17: RETURN SORT_BY_UTILITY_DESC(validProbes)** 

## **Algorithm 4: Evidence-Preserving State Reconstruction (Reset Operator)** 

> **Plaintext** **<mark></mark>** 

- **ALGORITHM: ExecutePortfolioPreservingReset INPUT: Active agent sessions A, hypotheses H, evidence ledger E OUTPUT: Refreshed, lightweight agent team initialized with verified model snapsho 1: AuditLog.StoreFullSessions(A) // Preserve immutable history for experimental r 2: 3: // Step 1: Retain strictly verified evidence with valid execution provenance 4: verifiedSnapshot ← SELECT e FROM E WHERE e.status == "VERIFIED" AND e.provenan 5: 6: // Step 2: Select a bounded, non-redundant hypothesis portfolio 7: retainedHypotheses ← SelectDiversePortfolio(H, targetSize = 3) 8: 9: // Step 3: Construct minimal model context snapshot K 10: Snapshot_K ← { 11:     evidence: verifiedSnapshot, 12:     portfolio: retainedHypotheses, 13:     unresolvedInvariants: ExtractUnresolvedInvariants(retainedHypotheses) 14: } 15: 16: // Step 4: Purge bloated chat history 17: FOR EACH agent IN A DO** 

https://gemini.google.com/app/55303d6a1facc754 

23/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**18:     agent.DestroyChatTranscript() 19: END FOR 20: 21: // Step 5: Transform model snapshot into distinct, clean agent briefs 22: freshBriefs ← TransformModelToBriefs(Snapshot_K) 23: RETURN SpawnFreshAgents(freshBriefs)** 

**Algorithm 5: Semantic Model Slicing (** **_T_ 3 )** 

**Plaintext** 

**<mark></mark>** 

- **ALGORITHM: SliceSystemModel INPUT: Typed system model MR, behavioral model MB OUTPUT: Minimized system sub-graph preserving relevant causal paths 1: symptomNode ← FindSystemElement(MR, MB.violatedInvariant.location) 2: 3: // Perform backward data-flow and control-flow slicing from symptom 4: backwardSlice ← ExtractBackwardDependencies(MR, symptomNode, maxDepth = 5) 5: 6: // Perform forward slicing from behavior trigger components 7: forwardSlice  ← ExtractForwardDependencies(MR, MB.triggerComponents) 8: 9: // Intersect structural slices with active hypothesis candidate elements 10: causalSubGraph ← INTERSECT(backwardSlice ∪ forwardSlice, ActiveHypothesisElem 11: 12: RETURN ConstructTypedSubGraph(MR, causalSubGraph)  ** 

**Refine the three main research questions (RQ1, RQ2, and RQ3) for the MORPH-FL paper.** 

**For a top-tier archival journal submission (such as IEEE Transactions on Software Engineering or ACM TOSEM), research questions must be sharp, falsifiable, and tied directly to measurable variables.** 

https://gemini.google.com/app/55303d6a1facc754 

24/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Here are the refined, publication-ready versions of RQ1, RQ2, and RQ3 for the MORPH-FL paper, complete with their evaluation parameters.** 

## **RQ1: Localization Effectiveness and Cross-Layer Generalization** 

**RQ1: To what extent does MORPH-FL improve fault localization accuracy (Top-1, Top-5, Top-10, and Mean Reciprocal Rank) compared against state-of-the-art lexical retrievers, graphaware tools, and standard agentic baselines, particularly on multi-file, cross-layer, and low-lexical-overlap bugs?** 

**Independent Variable: Localization framework (MORPH-FL vs. BM25/embedding retrievers vs. standard multi-agent code browsers vs. static graph slicers).** 

**Dependent Variables: Top- accuracy, MRR, and recall at function/file level.** **_k_** 

**Evaluation Focus: Proving that structured models and causal slicing capture dependencies that surface-level text similarity or unstructured chat agents miss entirely.** 

## **RQ2: Mechanistic Contribution of Portfolio-Preserving Forgetting (PPF)** 

**RQ2: How effectively do model-guided hypotheses and PortfolioPreserving Forgetting (PPF) reduce reasoning fixation, and what is the individual contribution of each ablation component (e.g., adaptive trigger, diverse hypothesis portfolio, evidence retention) to recovering from incorrect early leads?** 

**Independent Variable: Architectural configuration (Full MORPH-FL vs. No Forgetting vs. Fixed-Interval Resets vs. Context-Only Forgetting vs. SingleHypothesis Retained).** 

**Dependent Variables: Fixation frequency, rate of recovery after an incorrect initial hypothesis, and hypothesis diversity score.** 

**Evaluation Focus: Directly answering TSE reviewers' skepticism: Does forgetting actually help, and which part of the forgetting operator drives the success?** 

## **RQ3: Cost-Efficiency and Epistemic Calibration under Budgets** 

**RQ3: At equal token, dollar, and tool-call budgets, does MORPH-FL achieve superior localization performance per unit cost, and how** 

https://gemini.google.com/app/55303d6a1facc754 

25/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**reliably do its uncertainty estimates and abstention policies reflect true localization difficulty?** 

**Independent Variable: Execution budget limits (strict, moderate, generous token/probe caps) and epistemic constraint settings.** 

**Dependent Variables: Performance-versus-cost area under the curve (AUC), token consumption per correct localization, and calibration error of confidence/uncertainty outputs.** 

**Evaluation Focus: Demonstrating that MORPH-FL does not merely brute-force solutions with endless LLM calls, but operates with high information gain and knows when to abstain rather than hallucinate confidence.** 

**outline the emperical evaluation based on benchmarks like swe-bench lit and defect4j and also provide comprehesive explanation of experiments that shold be performed to address reserach questions** 

**An empirical evaluation for a top-tier archival venue like IEEE Transactions on Software Engineering (TSE) must rigorously demonstrate that MORPH-FL outperforms existing approaches across diverse codebase scales, handles complex multi-file bugs, and proves that its specific design choices (MDE models and Portfolio-Preserving Forgetting) actually drive the performance gains.** 

**Below is a comprehensive empirical evaluation plan, detailing dataset selection, baselines, and the specific experiments required to answer RQ1, RQ2, and RQ3.** 

# **1. Benchmark Selection & Preparation** 

**To evaluate MORPH-FL across both micro-level structural defects and macro-level repository-wide bugs, the evaluation uses two complementary benchmark suites:** 

**Defects4J (Java): Provides hundreds of real, historically validated bugs across medium-scale open-source Java projects. It serves as the testbed for precise,** 

https://gemini.google.com/app/55303d6a1facc754 

26/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**method- and file-level localization accuracy, especially for algorithmic and withincomponent defects.** 

**SWE-bench Lite / SWE-bench (Python): Consists of real GitHub issues and pull requests across large, multi-file Python repositories (e.g., Django, SymPy, Scikitlearn). This tests MORPH-FL's ability to handle cross-layer dependencies, low lexical overlap between bug reports and source code, and long-horizon reasoning challenges.** 

## **Ground Truth & Leakage Prevention** 

**Pre-fix Snapshots: Experiments run strictly against the repository commit immediately preceding the bug fix.** 

**Leakage Control: Ensure test harnesses, commit messages, and patch contents are withheld from agents during the localization phase. Ground truth is defined strictly by the modified files/functions in the official patch, filtered to exclude test-only or refactoring edits.** 

# **2. RQ1: Effectiveness and Cross-Layer Generalization Experiments** 

**To answer RQ1, MORPH-FL is compared against representative baselines spanning traditional information retrieval, graph analysis, and modern agentic frameworks.** 

## **Baseline Families** 

**1. Lexical & Vector Retrieval: BM25 and strong code embedding retrievers (e.g., dense retrieval over repository chunks).** 

**2. LLM Reranking: Standard LLMs reranking the top-50 retrieved files based on the bug report.** 

**3. Unstructured Multi-Agent Baseline: An agentic workflow with repository browsing and testing tools, but using continuous, unmanaged chat histories and no MDE models.** 

**4. Static Graph Slicers: Traditional static call-graph and def-use dependence analysis starting from stack traces or entry points, without AI hypothesis evolution.** 

## **Evaluation Metrics** 

https://gemini.google.com/app/55303d6a1facc754 

27/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**Top- Accuracy (** **_k k_ ∈{1, 3, 5, 10} ): Percentage of bugs where the correct file/function is present in the top  ranked results.** **_k_** 

**Mean Reciprocal Rank (MRR): Measures the placement quality of the true fault location.** 

**Stratified Analysis: Sub-divide results by bug type (single-file vs. multi-file, stacktrace available vs. description-only, high vs. low lexical overlap with the report).** 

# **3. RQ2: Mechanistic Ablation Experiments (Testing PPF & MDE)** 

**To prove that MORPH-FL's specific components (rather than just brute-force LLM compute) drive success, a rigorous ablation study is conducted. Each variant deactivates or alters a single architectural pillar.** 

**Ablation Variant What is Modified or Scientific Question Removed? Answered Variant A: No Forgetting Disables PPF; agents retain Does resetting continuous chat history until conversational history budget exhaustion. prevent fixation? Variant B: Fixed-Interval Resets agents every** **_N_ steps Is adaptive, evidence-driven Forgetting rather than using the resetting superior to monitored plateau signal ( arbitrary timers? EvaluateStagnation ). Variant C: SingleRetains only the top-scored Does maintaining a diverse Hypothesis Retention hypothesis (** **_H_ 1 ) upon reset, portfolio prevent premature copying the optimization lock-in? approach of the source paper. Variant D: Text-Only Replaces MDE metamodels ( Does Model-Driven Summarization** **_M_ 1 –** **_M_ 4 ) and Engineering add value transformations with plainbeyond competent text LLM chat summaries conversational during resets. summarization?** 

https://gemini.google.com/app/55303d6a1facc754 

28/33 

|10/19/26, 10:29 AM|MORPH-FL Approach Explained B|riefly - Google Gemini|
|---|---|---|
|**Ablation Variant**|**What is Modified or**<br>**Removed?**|**Scientific Question**<br>**Answered**|
|**Variant E: No Skeptical**|**Removes the**|**Does explicit**|
|**Agent**|**adversarial/skeptical**|**counterexample search**|
||**investigator role from the**|**improve localization**|
||**agent team.**|**robustness?**|



# **4. RQ3: Cost-Efficiency and Resource Scaling Experiments** 

**To answer RQ3, experiments evaluate performance under strict resource constraints to demonstrate that MORPH-FL maximizes information gain per dollar and token.** 

## **Budget Stress-Testing** 

**Run all baselines and MORPH-FL across tiered budget caps (e.g., low, medium, and high token/tool-call limits).** 

**Plot Performance-vs-Cost Curves (Top-1 Accuracy vs. cumulative USD cost / inputoutput tokens).** 

**Measure the rate of redundant inspections (how many times agents reread the same file) across MORPH-FL versus unstructured agent baselines.** 

## **Uncertainty Calibration & Abstention** 

**Outline the implementation architecture and software tool stack required to build and run MORPH-FL.** 

**Building and running MORPH-FL requires an architecture that bridges modern Large Language Model (LLM) agent frameworks with traditional Model-Driven Engineering (MDE) and program analysis tooling. Because standard agent frameworks (like vanilla LangChain or** 

https://gemini.google.com/app/55303d6a1facc754 

29/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**AutoGen) rely on continuous, unstructured chat logs, a custom orchestration layer is required to enforce metamodels, graph slicing, and Portfolio-Preserving Forgetting (PPF).** 

# **1. Core System Architecture** 

**The MORPH-FL runtime architecture is organized into five interacting subsystems:** 



<!-- Start of picture text -->
[ Bug Report & Codebase ]<br>│<br>▼<br>┌───────────────────────────────────────────────┐<br>│ 1. Ingestion & Model Construction Engine      │  (T1, T2: AST Parsing, Call Gr<br>└──────────────────────┬────────────────────────┘<br>▼<br>┌───────────────────────────────────────────────┐<br>│ 2. Hypothesis Portfolio & Distance Engine     │  (M3: Graph Distance & Diversi<br>└──────────────────────┬────────────────────────┘<br>▼<br>┌───────────────────────────────────────────────┐<br>│ 3. Agent Orchestrator & PPF Controller        │  (T7: Stagnation Detection & C<br>└──────────────────────┬────────────────────────┘<br>│ Spawns / Resets<br>▼<br>┌───────────────────────────────────────────────┐<br>│ 4. Budgeted Probing & Verification Harness    │  (M4, T5: Sandbox Test Runner &<br>└──────────────────────┬────────────────────────┘<br>│ Verified Observations<br>▼<br>┌───────────────────────────────────────────────┐<br>│ 5. Immutable Evidence Ledger & Audit Store    │  (Provenance-backed fact store<br>└───────────────────────────────────────────────┘<br> <br><!-- End of picture text -->

## **Subsystem Breakdown** 

**1. Ingestion & Model Construction Engine (** **_M_ 1,** **_M_ 2 ): Parses natural-language bug reports into formal behavioral contracts (** **_T_ 1 ) and builds typed system graphs (** **_T_ 2 ) covering call trees, data-flow edges, and class hierarchies.** 

https://gemini.google.com/app/55303d6a1facc754 

30/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**2. Hypothesis Portfolio & Distance Engine (** **_M_ 3 ): Maintains and evaluates the active set of 2–4 competing causal explanations, using graph edit distance or semantic embedding distance to ensure portfolio diversity.** 

**3. Agent Orchestrator & PPF Controller (** **_T_ 7 ): Manages the multi-agent team (behavioral, structural, dynamic, and skeptical investigators). It continuously monitors epistemic progress via EvaluateStagnation and executes the PPF reset operator when exploration stalls.** 

**4. Budgeted Probing & Verification Harness (** **_M_ 4,** **_T_ 5 ): Translates hypothesis predictions into executable unit tests, static queries, or captured runtime traces, running them inside an isolated container sandbox.** 

**5. Immutable Evidence Ledger & Audit Store: A secure, write-append storage backend that records all verified observations with strict test provenance, ensuring zero fact loss during agent resets.** 

# **2. Recommended Software Tool Stack** 

**To implement this architecture with high performance and maintainability, the following open-source and enterprise-grade tool stack is recommended:** 

|**Layer / Subsystem**|**Recommended Tool /**<br>**Framework**|**Rationale & Role in MORPH-**<br>**FL**|
|---|---|---|
|**Language & Runtime**|**Python 3.11+**|**Industry standard for AI**<br>**research, LLM integration,**<br>**graph manipulation, and AST**<br>**parsing.**|
|**AST Parsing & Code**<br>**Analysis**|**Tree-sitter &LibCST**|**Multi-language, robust**<br>**concrete syntax tree parsing**<br>**to extract functions, classes,**<br>**and call structures (**<br>**).**<br>**_M_**<br> **2**|
|**Graph Modeling & Slicing**|**NetworkX orPyGraphviz**|**Powers the system model**<br>**call graphs, data-flow edge**<br>**mapping, and model slicing (**<br>**).**<br>**_T_**<br> **3**|



https://gemini.google.com/app/55303d6a1facc754 

31/33 

|**Layer / Subsystem**<br>10/19/26, 10:29 AM|**Recommended Tool /**<br>**Framework**<br>MORPH-FL Approach Explained Bri|**Rationale & Role in MORPH-**<br>**FL**<br>efly - Google Gemini|
|---|---|---|
|**Schema & Metamodel**<br>**Enforcement**|**Pydantic v2**|**Enforces strict metamodel**<br>**constraints (**<br>**–**<br>**) and**<br>**schema validation for**<br>**hypothesis structures and**<br>**evidence ledgers.**<br>**_M_**<br> **1** **_M_**<br> **4**|
|**LLM & Agent**|**Custom Asynchronous**|**Avoids rigid chat-loop**|
|**Orchestration**|**Agent Runner (built on**<br>**Instructor orLiteLLM)**|**abstractions; allows precise,**<br>**structured JSON extraction**<br>**of hypotheses and direct**<br>**control over context**<br>**resetting (**<br>**).**<br>**_T_**<br> **7**|
|**Execution Sandbox**|**Docker SDK for Python**|**Provides isolated, secure**<br>**container environments for**<br>**running untrusted test**<br>**probes, patches, and**<br>**dynamic instrumentation**<br>**safely.**|
|**Evidence & State**<br>**Persistence**|**SQLite withJSONB (via**<br>**SQLAlchemy)**|**Lightweight, robust storage**<br>**for the immutable evidence**<br>**ledger, audit logs, and**<br>**historical run metrics.**|
|**Vector & Distance Metrics**|**Scikit-learn (Cosine / Graph**<br>**Edit Distance)**|**Computes semantic and**<br>**structural distance metrics**<br>**between active hypotheses**<br>**to enforce portfolio diversity.**|



# **3. Runtime Lifecycle Execution Flow** 

**When executing MORPH-FL on a target repository (e.g., a Defects4J or SWE-bench instance), the runtime loop operates as follows:** 

https://gemini.google.com/app/55303d6a1facc754 

32/33 

MORPH-FL Approach Explained Briefly - Google Gemini 

10/19/26, 10:29 AM 

**1. Initialization: The engine loads the repository, triggers Tree-sitter to build the system graph (** **_M_ 2 ), and extracts behavioral invariants from the issue description (** **_M_ 1 ).** 

**2. Team Spawn: Three independent agent instances (structural, dynamic, and skeptical) are initialized with distinct behavioral prompts derived from the initial hypothesis portfolio (** **_M_ 3 ).** 

**3. Probing & Evaluation: Agents request probes. The runner executes them inside a Docker container. Observations are validated and written to the SQLite Evidence Ledger (** **_M_ 4 ).** 

**4. Stagnation Check: Every** **_W_ iterations, the PPF Controller evaluates recent evidence gain and hypothesis diversity. If a plateau is detected:** 

**Full agent chat transcripts are purged.** 

**Verified observations are locked in the ledger.** 

   - **A fresh, lightweight team is spawned with a sliced model context (** **_T_ 7 ).** 

**5. Termination: When the budget** **_C_ is exhausted or an explanation achieves maximal verification confidence, MORPH-FL outputs the ranked root-cause file with an audit trail.** 

## **To continue exploring the MORPH-FL implementation:** 

**Design the database schema for the Evidence Ledger and Metamodels ** 

https://gemini.google.com/app/55303d6a1facc754 

33/33 

