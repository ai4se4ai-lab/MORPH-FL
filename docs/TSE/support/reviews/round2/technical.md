# Independent technical review — round 2

**Scope:** completed Sections 1–4 of `docs/TSE/main.tex`, with later outlines read only for consistency. This is a technical specification review, not acceptance of an unfinished empirical journal submission. I did not read prior reviews or writer-support notes.

**Recommendation: Accept within this scope. Confidence: high for source correspondence and algorithmic consistency; moderate for positioning, whose cited primary literature I did not independently re-audit.**

## Assessment

The completed method is technically coherent and unusually explicit about the distinction between retaining observation records, reconstructing useful context, and improving localization. I found no material mismatch requiring revision between the stated algorithms/defaults and the inspected implementation. The empirical placeholders and subsequent outlines do not contradict the completed sections by claiming demonstrated benefits.

I checked `search/controller.py`, `search/config.py`, `search/policies.py`, `transformations/pipeline.py`, `domain/models.py`, and the executor and ledger implementations. I also inspected the label/metric interface and source-window construction. Targeted verification passed: `PYTHONPATH=src python3 -m unittest tests.unit.test_method tests.unit.test_controller tests.unit.test_reset_policy` ran 37 tests successfully. This does not constitute benchmark or dynamic-container validation.

## Strengths

- **Algorithms and defaults match execution.** Portfolio selection preserves its score/ID tie behavior, diversity uses the actual lexical/path formula, and neighborhood expansion uses the previous hop's set. The plateau algorithm correctly uses valid rounds, the latest valid round's half-token estimate, a strict affordability inequality, and a cleared window with cumulative round count retained. The worked reset's distance, expenditure, window cost, and threshold checks are consistent.
- **Identity and retention claims have the right boundaries.** Sections 3.2, 3.4, and 3.7 distinguish hypothesis, logical-probe, physical-cache, observation, and assessment identities. The text explicitly discloses missing prediction/probe references in assessments, suppression after hypothesis recreation, loss of interpretation links, and shallow payload mutability. The observation-ID retention proof describes the actual reset writes rather than implying semantic completeness.
- **Scoring is represented as a heuristic.** Static checks do not become runtime evidence; cumulative support need not be independent; score margins can overwhelm the bounded diversity bonus. The source/AST/other weights, no-probe proposal scores, and ranking fallback are correctly stated.
- **Stopping and output semantics are accurately separated.** Section 3.8 discloses the pre-pruning pool reference, the procedure-ID-based early stop, historical-assessment causal abstention, null confidence, and the independence of file and symbol rankings. These are important qualifications, not incidental implementation details.
- **The experiment is framed at the level its controls can identify.** Sections 1, 3.1, and 3.9 acknowledge that observation-text controls change information content as well as presentation and do not establish superiority over prose handoffs generally. Source-only evidence and patch-change proxy targets remain explicit.

## Concerns and severity

**No blocking technical concerns found in the reviewed sections.** Several substantial prototype limitations remain—unbounded reconstructed observation views, semantically redundant score accumulation, incomplete assessment identity, and suppressed reassessment after recreation—but each is already disclosed at the relevant method boundary. Requiring their removal would change the prototype rather than correct its specification. Their empirical consequences remain questions for the planned study.

One precision point merits attention when presenting eventual results: T7 marks unresolved predictions at the hypothesis level, based on whether that hypothesis has any dynamic-kind support (`fresh_context`, `runtime`/`unresolved` construction). It does not independently establish that every prediction in a multi-prediction hypothesis was tested. Section 3.2's assessment limitation and Section 3.8's abstention qualification already prevent a broad causal interpretation; future result prose should preserve that restriction. **Severity: low; remedy type: interpretation discipline, not a required code change.**

## Questions for the completed study

1. How often do retained observations remain available while their former scoring links cannot be recovered after pruning/recreation? The ordered artifacts can distinguish this from record loss.
2. How often does reconstructed context exceed the backend limit, and how does that affect the matched-budget comparison with dialogue-retaining controls?
3. Do reported mechanism effects survive cases dominated by redundant static support increments? This would contextualize the disclosed heuristic without requiring a new algorithm.

These questions concern pending empirical evidence. They are not additional prerequisites for accepting the completed specification.

## Must-fix items

None identified for Sections 1–4. A whole-paper publication decision remains contingent on completing and auditing the planned empirical study.
