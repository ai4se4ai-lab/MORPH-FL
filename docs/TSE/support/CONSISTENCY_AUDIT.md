# Consistency audit of the structural rewrite

The earlier audit-draft report is archived under versions/. This audit concerns the author-requested replacement, whose exact hashes and compile checks are recorded in build_verification.json.

- All paper content remains in main.tex with references.bib as the sole bibliography input. No section/figure inputs were introduced. The official template class/package conventions remain.
- Main-text exposition was rewritten; detailed algorithms and operational limits were moved to an inline appendix. ALGORITHM_MAP.md records the new publication-order mapping. Code behavior and study results were not changed.
- The bypass/defaulting example now contains two explicit AST-match predictions. Actual executor/assessment calls confirm contradiction/-1 and support/+1. The synthetic reset calculation uses the same mechanisms, dissimilarity1, scores-1/+1, and two initial observations. It is a constructed state transition, not benchmark evidence.
- Observation retention remains distinct from interpretation retention, context sufficiency, and localization quality. Link loss, handled-ID suppression, predicate-kind precedence, old-pool stopping, historical abstention, null confidence, and approximate Python analysis remain documented.
- The main algorithm summarizes the normal full-method path; response failures, ablations, exact budget gates, and shared/isolated conditions remain specified in the appendix. Candidate list is fixed at initialization, with later source-window rotation.
- No repository result number was copied. Outcome-dependent placeholders remain in the Results outline. Main-text examples contain explicitly synthetic values. Full empirical sections remain outlines.
- All18 bibliography entries are used; verified primary-source records remain in citations_verified.csv. TSE exemplar sources used for rhetorical design are documented in STYLE_REDESIGN.md; no wording was copied.
- Labels, references, citations, bibliography and overflow are checked in the final build metadata. The code listing is a single float so its two files are not split across columns. Figure branches distinguish continuation, reset and termination.
- Existing inspected source/protocol/template/prompt digests match source_manifest.json. The writing revision did not alter source or results. Pre-existing .gitignore changes are untouched.
- Earlier AI acceptance/readability claims do not transfer to this rewrite. FINAL_REVIEW.md and REWRITE_READER.md record the relevant editorial assessment without fabricated acceptance scores.

Remaining publication/evidence requirements are in GAP_REPORT.md. Build diagnostics and source/PDF hashes are in build_verification.json; benign upstream encoding/underfull warnings are retained in build logs.
