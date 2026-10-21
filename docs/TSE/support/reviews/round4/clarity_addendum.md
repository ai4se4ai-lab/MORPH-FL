# Stage G clarity amendment check

**Amended-version recommendation: Accept for the completed-section rigor/clarity/evaluability scope. Confidence: high (0.88).** This is an amendment check within round 4, not a new full review or a recommendation to accept the unfinished paper at TSE.

Verified `docs/TSE/main.tex` SHA-256 `905dce7a604e0c10b25338ce8577903b89058548613d2fdebecae089cd4dee81`. The original `clarity.md` is unchanged. Checked the requested amendments and their immediately relevant definitions; no agents were used.

## Disposition

- **Source-presence definition: resolved.** Background now defines the scope through the source-contains predicate and producing procedure's returned match flag. It explicitly distinguishes a numbered-line quote check from a whole-file AST check, including the important warning that an AST match does not establish a literal quote or particular line match. This resolves the must-fix scope issue.
- **Dynamic terminology: clarified.** Dynamic-predicate support is tied to a registered procedure's outcome. The internal `causal_prediction` label is disclosed without implying causal discrimination from an exit code or output match.
- **RQ3 judgment: resolved.** RQ3 now commits to descriptive ranking–cost profiles, states a matched-case no-worse-accuracy/no-greater-cost comparison, and avoids a scalar preference among tokens, probes, and wall time. A result that trades accuracy against a reported cost has an explicit descriptive treatment.
- **Audit denominator: resolved.** Both audits now require total opportunities, assessable opportunities, events, and unassessable counts. Displayed percentages use assessable opportunities, and missing artifacts cannot be counted as absence of events. The suppression definition is consistent with that convention.
- **Additional technical clarifications: clear within this review's scope.** The text explicitly says alternative counts are captured during sequential proposal processing and can be asymmetric and order-dependent. It also identifies the latest accepted behavioral interpretation as carried state that survives dialogue reset independently of related-hypothesis pruning. These additions improve interpretability of the policy boundary.

## Remaining concerns

No unresolved must-fix clarity/evaluability concern remains from my original review. The optional editorial suggestion to consolidate the lifecycle of cached, handled, retained, score-linked, and model-visible state remains useful but does not block these sections.

One terminology refinement is optional: the stated no-worse-in-every-dimension relation is weak dominance. If the paper later calls a profile strictly or Pareto superior, require at least one strict improvement and specify the accuracy endpoint and uncertainty treatment in the completed analysis. This does not undermine the present commitment to descriptive tradeoffs.

Whole-paper evidence remains pending exactly as in the original review: the study, complete results, audit implementation/version, eligible denominators, actual costs and failures, and evidence-conditioned significance cannot be certified from these sections. The amended text does not present those pending findings as established.
