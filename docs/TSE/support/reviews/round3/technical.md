# Technical review: Sections 1–4

**Recommendation: Minor Revision (for the scoped method/specification review). Confidence: high (0.85).** This is not a whole-paper acceptance recommendation. I assessed the literal method in Sections 1–4 against the implementation, without consulting previous reviews or support notes. Missing empirical results are outside this review's scope. I did not independently verify related-work sources or run benchmark experiments.

## Assessment and strengths

The specified prototype is technically coherent as a deliberately heuristic policy study. Its contribution is modest but clearly bounded: observation records, scoped interpretations, conversations, and live hypothesis scores are different objects. The paper does not confuse an unchanged observation-ID set with sufficient reconstructed context or improved localization. The portfolio and plateau algorithms are finite, readable, and closely match `search/policies.py`. The constructed reset arithmetic is consistent with those formulas.

Several unusually important implementation limitations are disclosed explicitly: logical-request suppression after pruning, loss of old score/support links, unbounded observation views, static evidence versus runtime causality, historical rather than leader-specific abstention, and the stale pool used by the dynamic stop. These disclosures substantially improve reproducibility. The description of observation-text controls also correctly limits the inference to a package comparison rather than attributing differences to typed representation alone. I found no basis within this scope to require a redesigned algorithm as a condition of describing and evaluating the present prototype.

## Concerns and remedies

### 1. T7 does not track unresolved predictions individually

- **Severity:** Moderate; must fix the specification.
- **Location:** Section 3, Reset and reconstruction, sentence beginning “T7 distinguishes static observations”; `src/morph_fl/transformations/pipeline.py:169–195`.
- **Type:** Literal specification mismatch / epistemic presentation.
- **Finding:** The manuscript says that predictions without dynamic-kind support are presented as unresolved. The implementation instead adds *all* predictions of a hypothesis to `unresolved` only when the hypothesis has no dynamic-kind support at all. A hypothesis with two predictions and support for just one has neither prediction listed as unresolved. The view also labels dynamic support as `verified_prediction_observations` using evidence kind, without a prediction-specific assessment link or an assessment-scope check. This is a further limitation of reconstruction, distinct from the already disclosed run-level abstention and early-stop semantics.
- **Remedy:** Describe the actual hypothesis-level rule and its partial-support failure case. Do not claim prediction-specific unresolved tracking. A documentation correction is sufficient for the present policy study; implementing prediction-level provenance would change the method and should be separately versioned if pursued.

### 2. The admitted predicate/kind combinations are broader than the scoring prose implies

- **Severity:** Low; must fix for an exact executable specification.
- **Location:** Section 3, Proposals, execution, and scoped assessment, T6 weight paragraph; Table of defaults; `transformations/pipeline.py:112–145`.
- **Type:** Specification precision / validation boundary.
- **Finding:** “AST evidence adds 1” is not universally true. `source_contains` is assessed first, without checking evidence kind; an AST observation contains `matched`, so an AST probe paired with `source_contains` can receive a source-presence assessment and weight 0.25. Synthesis does not enforce predicate/kind compatibility. Conversely, unsupported combinations are generally inconclusive. The code's precise weighting is source-presence assessment scope first, then AST kind, then other kinds. String predictions also default to `source_contains`, making this more than an impossible hand-crafted state.
- **Remedy:** State the weight precedence and predicate/kind dispatch explicitly, or qualify the existing prose as referring to conventional compatible pairs. Explain the default predicate for string predictions. Do not imply the validator rejects all semantically incompatible pairs.

### 3. Portfolio selection applies during every request, including the controls

- **Severity:** Low; clarification desirable.
- **Location:** Section 3, controller and variant table; `search/controller.py:196–209`; `search/config.py:88–94`.
- **Type:** Experimental mechanism interpretation.
- **Finding:** The controller selects at most `portfolio_size` hypotheses for each typed request even without a reset. `context_only` retains all live hypotheses internally at reset but still presents only a selected portfolio on the next call. `single_hypothesis` also restricts every request, not only restart retention. Thus these conditions affect live-state survival and ongoing visibility in different ways. The controller algorithm contains the selection step, but the short variant descriptions can invite an overly narrow restart-only reading.
- **Remedy:** Add one explicit sentence explaining that the per-call selection remains active in `no_forgetting` and `context_only`, and that `single_hypothesis` changes both per-call visibility and reset retention. Interpret the component comparisons accordingly.

## Questions / must-fix items

1. Will T7 be described as hypothesis-level dynamic-support classification, including the case where an untested prediction disappears from `unresolved` after another prediction gains support? This is the main required correction.
2. Will the scoring specification state actual predicate/kind dispatch, source-presence precedence, and the string-prediction default?
3. Please make explicit which variant contrasts change ongoing request visibility as well as the reset transition.

The first two corrections can be made without source changes. The existing interpretation-loss, dependence between checks, heuristic score accumulation, and context-growth limitations remain real limitations, but they are already disclosed and are not independent grounds for demanding an idealized replacement implementation. My recommendation assumes conclusions remain limited to this literal policy and its configured controls.
