# Fresh independent technical review — Stage G

Reviewed manuscript SHA-256: `5a68234474eb0ea6ffdbea8ea04775b0fac2e60988e7c4f31b211c2f2f35368c`.

Scope: Introduction; Background definitions and running example; Approach; Related Work. Abstract and later outlines were read for consistency only. I read the manuscript directly and spot-checked controller, configuration, session, and transformation code. I did not consult earlier reviews or drafting notes. This is a simulated technical review, not journal peer review.

## Recommendation for these four sections

**Minor revision. Confidence: moderately high (4/5) for the specification and its consistency with the inspected implementation; moderate for novelty positioning.** This is a recommendation about the four specified sections, not acceptance of the eventual complete TSE paper. The unfinished empirical manuscript cannot presently establish practical significance.

The sections provide a technically credible, unusually candid specification of a particular experimental instrument. I found no undisclosed fatal technical inconsistency in the inspected paths. The manuscript expressly limits its claims to a package comparison and does not present observation retention as semantic preservation, causal verification, or a novel ledger algorithm. The remaining concerns below are clarification and precision issues rather than reasons to redesign the method before these sections can stand.

## Strengths

- The separation among observations, interpretations, dialogue, and evaluation labels is clear and consequential. Source-presence support is not confused with reproduction of a failure, and patch changes are correctly described as imperfect localization proxies.
- The reset is specified operationally, including its weak invariant and important failure cases. Lost interpretation links, logical-probe suppression, unbounded reconstructed observation views, and stale-pool dynamic stopping are disclosed rather than concealed behind the term “evidence-preserving.”
- The constructed example now reaches a complete numerical reset decision and reconstruction. Its explicit synthetic status avoids suggesting an observed model recovery.
- Algorithms, weighting rules, ceilings, and selected source anchors make the implementation inspectable. Spot checks agree with the described assessment precedence, handled-ID suppression, hypothesis recreation behavior, historical causal-abstention flag, and reset ordering.
- Related Work gives external memory and execution ledgers appropriate credit. The text does not infer that an unstated capability is absent, and distinguishes executed restricted adaptations from related systems that were not reproduced.

## Concerns and requested remedies

### 1. Minor — causal terminology for explicit predicates

**Location:** Background “Locations, explanations, and evidence”; Approach “Proposals, execution, and scoped assessment” and “Ranking, stopping, and uncertainty.”

**Type:** Conceptual precision / interface interpretation.

The text carefully disclaims proof of cause, but still uses “dynamic causal prediction” for the implementation's `causal_prediction` scope. In the inspected code, a registered procedure's exit code or output substring is sufficient for this scope; no check establishes that the predicate distinguishes the proposed mechanism from an alternative. An arbitrary failing registered test can therefore support a declared predicate without being causally diagnostic. The caveats substantially contain this problem, but the scope name can still imply stronger semantics than the operational rule.

**Remedy:** State once, directly alongside the scope definition, that `causal_prediction` is an implementation label for a declared dynamic predicate and does not certify causal discrimination. Consider “dynamic-predicate support” in explanatory prose while retaining the literal field name where necessary. No implementation change is required for the stated source-only study.

### 2. Minor — alternative-count construction depends on proposal order

**Location:** Approach “Probe ordering and portfolio selection,” immediately after Algorithm 2.

**Type:** Specification completeness / reproducibility.

The prose says declared alternatives are other pooled hypotheses with differing expected values or predicates. In the controller, each probe's alternatives are constructed immediately after its hypothesis is inserted, during sequential processing of the current response. Consequently an earlier proposal cannot count a later, newly introduced alternative in that response, while the later proposal can count the earlier one. Probe utility may therefore depend on proposal order beyond the documented final tie-break rule. This is a small but relevant detail because utility determines which checks fit a finite probe/time budget.

**Remedy:** Add that alternative IDs are captured at proposal processing time and may be asymmetric within a batch. If the intended algorithm instead computes them after all proposals are materialized, that would be a future implementation change requiring a new frozen version; it should not be silently substituted into this specification.

### 3. Minor — separate current source evidence from carried report interpretation

**Location:** Approach “Typed investigation state and transformations” and “Reset and reconstruction.”

**Type:** Information-flow clarity.

The reset description emphasizes pruning hypotheses while retaining observations. However the report-derived behavioral record is also carried into reconstruction, and the controller replaces it with fields from the latest accepted response in the active scope. This means the reset can preserve the latest model's interpretation of expected/observed behavior even if the hypothesis associated with that interpretation is pruned. The text calls report extraction conjectural, but does not state this update/retention interaction as explicitly as it states the hypothesis-link limitation.

**Remedy:** Add a short sentence specifying last-valid-response replacement of behavioral fields and their survival across dialogue reset. This helps readers understand exactly which interpretations the forgetting boundary retains. It is not necessary to add a new ablation or claim this is harmful without data.

### 4. Minor — novelty rests on an empirical policy finding, not the specification alone

**Location:** Introduction contribution list; final Related Work synthesis.

**Type:** Contribution sufficiency / eventual interpretation.

The manuscript itself acknowledges this correctly: an external ledger, heuristic portfolio, and restart policy are established ingredients, while retention is nearly immediate from the reset's write set. The specification is useful, but TSE-level significance will depend on a generalizable policy result or a repeatable, informative failure mechanism. A broad set of inconclusive comparisons plus the invariant would leave the contribution insufficient. This is not a request to manufacture stronger novelty claims in these sections.

**Remedy:** Retain the current restrained positioning. Once results exist, rewrite the contribution statement around the specific supported knowledge rather than leaving the executable instrument as the principal scientific outcome.

## Questions / must-fix before finalizing these sections

1. Is the batch-asymmetric alternative count intentional? Specify the actual behavior either way.
2. Confirm explicitly that retained behavioral fields are the latest accepted model extraction and remain conjectural after reset.
3. Clarify the operational meaning of the causal-prediction scope so procedure success cannot be read as a mechanism test.

These are minor textual fixes. I do not require implementing content-matched summaries, changing score weights, repairing all disclosed dynamic-interface limitations, or proving view sufficiency to make the present four-section specification internally honest.

## Separate eventual whole-paper evidence needs

- Complete paired ranking and actual-cost results, eligible-label denominators, failed/context-limited runs, and honest coverage of restricted external adaptations are necessary before an effectiveness or efficiency conclusion.
- Source-only observations can support an empirical ranking study but cannot validate runtime causal diagnosis. Keep dynamic claims outside the demonstrated benchmark evidence.
- The proposed recreation and suppression audit must actually be implemented, versioned, and run before frequencies are reported. A retained-ID check cannot stand in for that audit.
- Conditional clue recovery uses workflow-specific eligibility and cannot establish a paired causal anti-fixation effect. Mechanism conclusions must remain conditional and descriptive under this design.
- Closest-work characterizations require final primary-source checking. I assessed the manuscript's positioning and qualifications here, not an independent reproduction or full bibliographic verification of each cited system.

These evidence needs are not hidden major-revision requests for the four reviewed sections; they determine whether a completed paper earns a favorable publication recommendation.
