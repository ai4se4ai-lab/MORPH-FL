# Independent reviewer 3 — clarity, definitions, and positioning (round 1)

**Scoped recommendation: Weak Reject. Confidence: High on the manuscript's clarity and implementation correspondence; moderate on research positioning.**

I reviewed only the Introduction, Background and Problem Definition, Approach, and Related Work in `docs/TSE/main.tex`. I read the later outlines only to judge whether the stated questions can eventually be answered. I inspected the relevant controller, transformations, configuration, prospective protocol, and experiment README. I did not read writer support notes or other reviews, execute experiments, or independently verify the cited publications against their full primary texts. This is a recommendation on the completed methodological and positioning material, not a verdict derived from missing empirical results. The draft openly identifies those results as pending. The most important outstanding issue is the mismatch between the ordinary meaning of the central “text summary” alternative and its actual implementation, followed by insufficient operational detail for a key claimed empirical question.

## Assessment

The paper proposes an understandable boundary: retain observations and their provenance, clear conversations, and retain a selected portfolio of explanations. It distinguishes an implementation invariant from empirical utility unusually carefully. The method is sufficiently specified to reconstruct most of its control flow, and spot checks of `search/controller.py`, `search/config.py`, and `transformations/pipeline.py` agree with the prose. The manuscript's modest novelty claim is credible as a proposed combination; the text does not claim that external memory, multiple hypotheses, or restart policies are individually new.

The research questions are answerable at different levels. RQ1 has concrete patch-proxy ranking endpoints and planned paired comparisons. RQ2 can support exploratory statements about operational recovery and component contrasts, provided the paper preserves its present qualifications about eligibility and confounded manipulations. RQ3 can describe costs and evidence-handling failures. However, the Introduction also promises an empirical question about reconstructed-context sufficiency, for which the outlines do not yet specify an observable decision rule. Likewise, a ranking comparison with the implemented `stateless_summary` condition answers a narrower question than whether structured memory earns its cost over an effective text summary.

## Strengths

- The distinction among observations, assessments, and explanations is introduced before notation and carried consistently into the execution semantics. The running example explicitly separates ordinary Python reasoning from what static probes establish.
- Record retention, view sufficiency, and localization benefit are explicitly separated. The ID-set invariant is accurately limited to the reset operation, and even shallow immutability limitations are disclosed.
- The controller description exposes consequential implementation behavior: invalid responses cost tokens, scope-specific gain can arise from cache exposure, reconstructed requests remain unbounded by portfolio size, and final symbol and file rankings can disagree. These details materially improve evaluability.
- The manuscript treats source-only evidence, unreviewed patch proxies, null confidence, restricted upstream adaptations, and dynamic-stop limitations honestly. I found no unearned positive performance conclusion in the reviewed material. Placeholder result macros and the abstract make the prospective status unmistakable.
- Related Work acknowledges the closest external-memory systems and distinguishes execution evidence from source presence. The comparison table uses “not stated” rather than claiming unreported capabilities do not exist.

## Concerns

### 1. Major — the central summary comparison is narrower than its motivation suggests

**Location:** Introduction paragraphs beginning “A text summary is an important alternative” and “Our starting idea”; Approach, Experimental instrument and audit boundary; Table of controlled variants. Implementation: `src/morph_fl/search/controller.py:209–217` and `search/config.py:84–95`.

**Type:** Construct validity and presentation.

The manuscript motivates a general comparison against a text summary of observations. The implemented summary is a deterministic newline concatenation of path, line, and JSON observation payload for every accessible observation. It does not summarize reasoning, retain selected alternative explanations, or perform compression. It also removes agent-visible behavior fields, hypothesis/prediction records, and relations, and the stateless condition changes dialogue persistence. The Approach acknowledges a presentation package, which is good, but never explains the exact summary constructor. A reader can reasonably imagine a concise investigator-written or model-generated handoff summary and attribute a future difference to structured memory versus that alternative.

**Why it matters:** This alternative is central to the motivation and RQ3. Beating an uncompressed observation-text view would establish value relative to that view, not establish that prediction links and restart policy earn their complexity over text summaries generally. Conversely, losing to that simple control would be informative.

**Remedy:** Specify the literal summary fields and construction rule, name it consistently as a deterministic observation-text control, and narrow the Introduction/RQ3 interpretation accordingly. If the intended broader claim remains, add a properly budgeted summary handoff condition that actually preserves investigation state in prose. This is not a demand to reproduce all memory systems or to run every conceivable baseline.

### 2. Moderate — reconstructed-view sufficiency lacks an operational endpoint

**Location:** Abstract; Background, Locations, explanations, and evidence; Introduction contribution/motivation; reset subsection; Study/Results/Discussion outlines.

**Type:** Evaluability and claim alignment.

The manuscript calls reconstructed-context sufficiency an empirical question distinct from ranking benefit. That distinction is valuable, but the future sections list retention audits, recovery, budget curves, and rankings without explaining what observation would count as an insufficient view. Backend context failures test deliverability; lower rankings test utility; neither by itself diagnoses missing investigation information. In particular, “needed for useful continuation” is broad enough to become a retrospective interpretation of any unfavorable run.

**Remedy:** Either identify sufficiency as an unmeasured explanatory question, or define a limited operational endpoint and audit procedure before results: for example, whether accessible observations and unresolved predictions needed for a specified next step are represented, with explicit eligibility and adjudication rules. No new human study is automatically necessary; a narrower claim is acceptable. Preserve the distinction from the existing retention-ID check.

### 3. Moderate — the worked example stops before the central reconstruction decision

**Location:** Background running example; Approach portfolio, plateau, and reset subsections.

**Type:** Accessibility and methodological exposition.

The example illustrates source-presence semantics well, but remains entirely conditional at precisely the point where the new contribution operates: “once the plateau conditions hold,” a reset occurs and a portfolio “may include” the relevant hypothesis. Readers must combine several formulas and prose passages to determine one actual reset and the resulting request. The numerous honest caveats do not replace an executable-sized example.

**Remedy:** Add one clearly synthetic trace with explicit hypotheses/scores, a three-sample monitor window, remaining budget, portfolio selection, retained observation ID, and the fields supplied on the next request. It need not imply measured recovery. This would simultaneously explain the score/diversity tradeoff, reset gates, and retention-versus-view distinction without expanding the algorithm catalogue.

### 4. Minor — notation and algorithm numbering add avoidable navigation work

**Location:** Notation table; algorithms in Candidate construction, utility, plateau, and reset subsections.

**Type:** Editorial clarity and reproducibility.

The notation table defines many principal symbols but not several algorithm arguments or thresholds (`P`, `V`, `J`, `n_0`, `rho`, and the taus); some are only resolved later in the defaults table. `A` denotes dialogues even though assessments are another major state object. The captions call procedures “canonical Algorithm 3” and “canonical Algorithm 2” in the opposite order from their appearance, while LaTeX assigns its own sequential numbers. This creates two numbering schemes without an explained reader benefit.

**Remedy:** Use publication order or describe the identifiers as implementation procedure IDs rather than algorithm numbers; define algorithm arguments locally and make clear where assessments reside. This is a small correction, not evidence that the formulas are wrong.

### 5. Minor — the illustrative listing is not valid as displayed Python

**Location:** Listing “Illustrative pre-fix source in two files.”

**Type:** Example correctness.

Top-level `def` and `from` lines have a leading space. Copied into either indicated file, they produce unexpected indentation. The intended Boolean-default bug is clear and does not depend on the whitespace error, but a paper about executable checks should make the example directly runnable.

**Remedy:** Remove the leading top-level indentation and retain normal indentation only inside function bodies. If desired, define a minimal render stub separately; do not suggest that the existing listing demonstrates execution of the full report.

## Figures, tables, related work, and reproducibility

The flow diagram communicates the observation-retention boundary and labels dashed feedback explicitly; I found no substantive graphical claim inconsistent with the prose. The shared “retained observation ledger / scoped assessments” box could be read as combining the separately defined record types, but this is a minor schematic simplification. The defaults table is valuable and makes the chosen heuristics inspectable. The closest-systems table is cautious; its absence statements must continue to mean only what the caption says. I cannot certify its source-level accuracy without reading those publications, and I make no accusation of an inaccurate comparison.

The source anchors, repository defaults, explicit study overrides, pinned prospective protocol, and literal scoring/ranking rules give the proposed method a useful reproducibility foundation. A final reader-facing study section will still need concrete model/data/procedure versions and a clear artifact entry point; the current outlines expressly reserve that content. I do not count the absence of completed results, typeset result tables, or full later sections as an additional defect in this scoped review.

## Questions for the authors

1. Is the intended summary alternative specifically the current raw observation-text constructor, or a handoff summary of the investigation? What exactly should a positive comparison license the authors to conclude?
2. Will view sufficiency have an independently specified observable endpoint, or should it remain an unmeasured limitation?
3. Which combined component contrasts would support the RQ2 hypothesis, and which plausible mixed patterns would leave the mechanism unresolved? The present wording appropriately avoids interpreting reset counts alone, but a compact prospective interpretation table would make this stronger.

## Must fix for the reviewed material

1. Disclose the exact summary constructor and align the central motivation and eventual interpretation with the alternative actually tested.
2. Align claims about empirical view sufficiency with a defined endpoint or explicitly mark that question as unmeasured.
3. Correct the Python listing and the conflicting algorithm numbering.

A small complete synthetic reset trace would substantially improve accessibility. The proposal is disciplined and testable; the weak-reject recommendation reflects the remaining gap between its central comparison language and its operational instrument, not a requirement that it demonstrate positive empirical results.
