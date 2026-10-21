# Independent review: clarity and evaluability, Sections 1–4

**Recommendation: Minor Revision (scoped to Sections 1–4). Confidence: high.**

I reviewed the abstract and Sections 1–4 of `docs/TSE/main.tex`; I read the later section outlines only to check consistency with the stated questions and limits. This is not an assessment of empirical results, external literature accuracy, or implementation correctness. The prospective status and unbound results are explicit, so missing empirical findings are not a reason for this scoped recommendation.

## Strengths

- The paper defines localization, hypothesis, observation, assessment, evidence scope, context, reset, and the three distinct properties of retention, view sufficiency, and localization benefit before relying on them. In particular, the distinction between retaining a record and furnishing a sufficient next request is unusually clear (Section 2.1).
- The example is accessible and correctly limited. It connects a visible symptom to a different source file while distinguishing reasoning about Python semantics from an actually executed dynamic check (Section 2.2). It never presents the synthetic continuation as measured recovery.
- Section 3.6 now supplies a complete constructed **reset step**, including portfolio selection, monitor inputs, all affordability gates, retained state, cleared state, and the next request's contents (lines 319–323). The arithmetic is intelligible: the shared term gives lexical distance 0.8, total distance 0.88; four 512-token rounds leave 13,952; the final three rounds cost 1,536; the restart estimate is 256. High diversity does not block this reset because repetition satisfies the alternative branch. The example does not need an invented model continuation or successful localization to demonstrate its stated transition.
- The actual comparison target is disclosed rather than disguised: observation text omits information and changes presentation, so this is a package contrast rather than a clean test of typed representation or summaries in general (Introduction; Sections 3.1 and 3.9). The limits on causal inference, confidence, role isolation, and physical versus logical probe reuse are also explicit.
- RQ1 concerns patch-proxy rankings, RQ2 combines eligible misleading-lead trajectories with component contrasts, and RQ3 concerns actual costs and evidence handling. The later outlines preserve these scopes and do not introduce a promised measurement of view sufficiency, calibrated confidence, or causal correctness.

## Concerns and remedies

1. **Minor; exposition; abstract.** “Two empirical questions: whether the resulting rankings justify the added cost” is phrased as one compound question, while the introduction enumerates three RQs. The intended distinction can be reconstructed, but the abstract makes the question structure unnecessarily ambiguous. **Remedy:** say “ranking effectiveness and the cost of obtaining it,” or explicitly name effectiveness and cost as the two empirical dimensions, with mechanism addressed separately. This is a wording change, not a request for another experiment.

2. **Minor; non-specialist accessibility; Sections 3.2–3.3, particularly lines 167–174.** The exposition moves from the intuitive example to M1–M4, T1–T7, BM25, access scopes, and two probe identities in a short span. Definitions are present, but BM25 is introduced as a name without a plain-language gloss. Readers outside retrieval or agent implementation may lose the main control flow amid the identifiers. **Remedy:** gloss BM25 as a lexical report-to-source ranking method on first use, and add one brief sentence linking the transformation labels to the intuitive sequence “prepare source, propose an explanation and check, record the result, rebuild context.” Existing algorithms can retain their technical detail.

3. **Minor; navigation/evaluability; RQs and Table 3 (controlled variants).** The variant table explains individual manipulations well, but the reader must assemble which planned contrasts principally answer each RQ, and the later study outline refers to six primary workflows without naming them there. This does not contradict Sections 1–4, and it is reasonable for a working outline, but a concise mapping would improve reviewability before the study section is expanded. **Remedy:** identify the principal control pairings for each RQ in the eventual study prose or add a compact RQ-reference column/cross-reference. Preserve the existing warnings that package and role contrasts are not perfectly isolated interventions.

## Questions for the authors

- Is the abstract's “two empirical questions” intended to mean effectiveness and efficiency, with RQ2 as a mechanism analysis? A small wording adjustment should make the answer unambiguous.
- When the study outline is expanded, which six workflows constitute the primary comparison family? Name them alongside the already disclosed component controls so readers can connect each claim to its contrast.

## Must-fix for this scoped revision

Clarify the abstract's question count and supply a plain-language first-use gloss for BM25. The comparison-to-RQ mapping is a small presentation improvement to carry into the expanded study section. I find no remaining major clarity or evaluability defect in the reset specification or its synthetic reset trace, and I do not require empirical outcomes or a simulated successful model response to accept the method exposition.
