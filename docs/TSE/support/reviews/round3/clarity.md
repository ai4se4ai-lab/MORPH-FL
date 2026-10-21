# Independent clarity and evaluability review

Scope: abstract and Sections 1–4 of `docs/TSE/main.tex`, with later outlines checked only for consistency. I read the manuscript directly and did not consult prior reviews or support notes. Repository inspection was limited to the registered protocol and analysis entry points where useful for evaluating the stated endpoints.

**Recommendation: Minor Revision for the scoped method/positioning draft. Confidence: high.** This is not an acceptance recommendation for a completed TSE empirical article: the manuscript explicitly has no bound results, and the later sections are outlines. Within the requested scope, the central distinctions are unusually clear, the method is inspectable, and the remaining clarity problems are repairable without redesign. Practical significance remains an empirical question.

## Strengths

- The observation/explanation/dialogue distinction is understandable before the dataclass terminology appears. The false-default example makes static support versus runtime causal evidence concrete, and the worked reset supplies actual numbers rather than only schematic arrows.
- Guarantees are carefully bounded. The observation-ID invariant, payload overwrite protection, incomplete assessment relation, retained interpretation loss, logical suppression, unbounded reconstruction, null confidence, and historical abstention semantics are all disclosed. The text does not equate a retained ledger with a sufficient next context.
- The observation-text control is described concretely and its information-content and timing confounds are acknowledged repeatedly. RQ1/RQ3 package claims and the inability to isolate typed representation are consistent across the introduction, approach, and outlines.
- Related work identifies memory and ledger predecessors without claiming their silence establishes absence. The external adaptations and nonexecuted related systems are distinguished clearly.

## Concerns and remedies

### C1 — RQ2 needs a more explicit decision rule

**Severity:** moderate. **Location:** Introduction RQ2; Section 3 experimental instrument; Study/Results outlines. **Type:** evaluability and inferential clarity. **Must fix:** yes.

“Eligible wrong-lead trajectories and compatible component contrasts” is a sensible restriction, but it leaves a reader unable to tell which observable result would support the portfolio/reset mechanism rather than a ranking difference of the whole package. The text supplies an eligibility rule, and the threats outline correctly notes that eligibility is workflow-specific, but it does not yet state how those selected trajectories and the four named component contrasts will be interpreted together. Different workflows can have different eligible subsets, so their conditional recovery percentages are not automatically paired mechanism effects.

**Remedy:** Add a compact RQ-to-evidence mapping: specify each comparison, measured outcome, denominator, and permitted inference. State explicitly that conditional recovery across different eligible subsets is descriptive; identify which contrasts use common cases and which trajectory observations can demonstrate a particular transition without attributing a general causal mechanism. Define what counts as a compatible versus conflicting component pattern, or state that the synthesis is qualitative and cannot independently confirm the hypothesized mechanism.

### C2 — The additional loss/suppression audit is an undeclared operational dependency

**Severity:** moderate. **Location:** Section 3 proposals/execution; Introduction RQ3; Results outline. **Type:** endpoint specification. **Must fix:** yes, before freezing the study or making frequency claims.

The manuscript candidly says frequency estimates are unmeasured and require additional analysis. Nevertheless, RQ3 asks about evidence-handling failures and the results outline promises the audit. The observable events are named but their counting rules are absent: for example, whether a recreated hypothesis lacking former links is one event per hypothesis, proposal, reset, or run; and whether an intentionally suppressed request is a failure or merely policy behavior. This matters because record retention can succeed while each of those events occurs.

**Remedy:** Define the audit unit and denominator, the event predicates, how predictions are recovered from ordered artifacts, and which events are called failures versus potential failure mechanisms. Keep the endpoint explicitly planned until that analysis exists and is checked. A small specification table is sufficient; no new claim of view-sufficiency measurement is needed.

### C3 — Variant labels invite stronger interpretations than their manipulations support

**Severity:** minor. **Location:** Table of controlled variants and adjacent prose. **Type:** terminology/control clarity. **Must fix:** no, but recommended.

The prose acknowledges package confounds, yet table questions such as “does role diversity matter?” and “does challenge guidance matter?” sound more isolating than changing to a structural role or omitting a scheduled role necessarily is. `no_mde` and `stateless_summary` are especially easy to misread even with the later explanation that neither removes typed internals nor generates a summary.

**Remedy:** Preserve implementation keys but add descriptive display names and use “contrast associated with …” wording for nonisolating changes. State whether role scheduling changes the number or distribution of calls, and distinguish the dialogue/reset schedule of the two observation-text variants in one directly comparable sentence.

### C4 — Implementation caveats obscure the first-pass conceptual route

**Severity:** minor. **Location:** Section 3, especially typed state, proposals, stopping, and variants. **Type:** nonspecialist readability. **Must fix:** no.

The manuscript is honest but dense: dataclass groups, seven transformations, access scopes, logical versus physical probe identities, score rules, and edge cases arrive in quick succession. A software-engineering reader can reconstruct the method, but must repeatedly decide which details are essential to understanding the policy and which qualify its implementation. “Dynamic-kind support,” “historical-assessment abstention,” and “reassessment suppression” are particularly demanding on a first pass.

**Remedy:** Give one short plain-language default-run summary before the implementation detail: what a role receives, what it proposes, what a check changes, and what a reset keeps/discards. Group the known loss/suppression and stopping edge cases in a compact contract table, retaining their present precision. Explain the audit-oriented terms where first used rather than requiring readers to infer them from the code names.

## Questions for the authors

1. Is RQ2 intended to establish a causal mechanism, or characterize operational behavior conditional on this implementation? The latter matches the current controls and most of the prose; make that wording uniform.
2. Which exact evidence-handling audit endpoints will be frozen before results are inspected, and which remain exploratory?
3. Will the two observation-text configurations be presented under descriptive names in results so readers do not mistake deterministic payload concatenation for a generated handoff summary?

## Guarantee and outline consistency check

I found no central contradiction between Sections 1–4 and the later outlines. Source-only ranking, patch-change proxies, noncalibrated confidence, package comparisons, unmeasured semantic view sufficiency, and the limitations of proxy-wrong-lead recovery remain consistently bounded. The conclusion outline's “specification and guarantees” should continue to mean the narrow reset/ledger contract, not a promise of preserved interpretations or useful continuation. The additional audit must not be presented as an already implemented or validated measurement. No new guarantee is needed; clearer endpoint mapping is the main remaining requirement.
