# Independent technical review — round 1

**Recommendation: Weak Reject. Confidence: High for implementation correspondence; medium overall.**

Scope: Introduction, Background/definitions/running example, Approach, and Related Work. I read main.tex and repository implementation, without writer support notes or other reviews. This recommendation concerns the scoped method specification, not missing empirical results. I do not require evaluation findings for this review. I did not independently verify the cited papers against their primary texts, so my related-work judgment concerns the positioning and claims as written rather than a full literature audit.

## Summary and strengths

The paper proposes retaining versioned observations while resetting conversations and pruning explanatory hypotheses. It carefully separates record retention, reconstructed-view sufficiency, and measured localization benefit. That distinction is substantive and correctly avoids treating a source quote as runtime confirmation. The running example communicates this limit effectively. The related-work positioning acknowledges existing memory and restart mechanisms and does not claim either in isolation.

The implementation correspondence is unusually candid. I checked controller.py, policies.py, config.py, transformations/pipeline.py, executor.py, ledger.py, domain/models.py, and sessions.py. Portfolio scoring, lexical distance (including empty-set behavior), reset gates, valid versus attempted rounds, per-scope pruning, unbounded observation reconstruction, default constants, separate file/symbol ranking, historical abstention, and the stale pre-pruning early-stop reference are described accurately. The reset's observation-ID invariant follows directly from its writes; it is appropriately weaker than a useful-memory guarantee. No Critical issue found.

## Concerns

### 1. Major — retained facts cannot restore an identically reintroduced pruned hypothesis

**Location:** Approach: proposals/execution, reset/reconstruction, Algorithm 1; controller.py:320–405 and 441–463; pipeline.py:68, 102; policies.py:36–50.

The shared-condition `seen` set survives reset and records logical probe IDs. Pruning removes the hypothesis object, its support/contradiction lists, and its score. If a later role proposes the same path/mechanism/kind and parameters, synthesis recreates the same hypothesis/probe IDs with empty support and score zero. `rank_probes` filters the probe out before the physical cache is consulted. Therefore the preserved observation cannot restore that hypothesis's previous assessment or score through the ordinary proposal path. Raw observations remain visible, but their availability is distinct from executable reuse by the scoring mechanism.

This can erase a previously recorded contradiction from a reintroduced live hypothesis, or prevent a supported hypothesis from regaining its rank. It does not violate the stated ID-retention invariant; it is an important semantic limitation of the proposed evidence-preserving restart mechanism that is currently absent from the otherwise detailed reset discussion. It may also affect the pruning contrast.

**Remedy/type:** Method clarification and implementation decision. Prefer separating physical execution deduplication from assessment eligibility, and restore or recompute assessment links when a hypothesis returns. Otherwise explicitly specify this irreversible logical-probe suppression, explain its consequences, and make its occurrence auditable. A small deterministic regression test would be appropriate if behavior changes.

### 2. Moderate — changed predictions can be silently suppressed, beyond the limitation already disclosed

**Location:** Background definition of assessment; Approach: hypothesis/probe identity and scoped assessment; pipeline.py:68–108; controller.py:329–363, 373–405; domain/models.py:123–129.

Probe identity includes hypothesis identity and parameters but excludes the prediction. Reusing identical check parameters with a changed expected value or predicate produces the same logical probe ID. In shared mode it is filtered before assessment, even if the earlier assessment was inconclusive. The manuscript discloses suppression when an observation is already in support/contradiction lists, but this earlier `seen` suppression is stronger and also applies to inconclusive outcomes. I verified with a small Python invocation that changing the prediction while retaining parameters yields the same probe ID and zero ranked probes with the previous ID in `seen`.

Moreover, an Assessment stores hypothesis ID and evidence ID but no prediction ID or probe ID. Once a hypothesis has multiple predictions, the assessment record alone cannot identify which prediction was tested. Event order and proposal artifacts may help reconstruct a particular execution, but that is weaker than the claimed explicit prediction–observation link in typed state.

**Remedy/type:** Clarify and preferably separate observation identity, logical request identity, and prediction assessment identity. Add prediction/probe references to assessments, or state a precise reconstruction rule and limitations. Do not imply that every revised explicit prediction receives an assessment.

### 3. Moderate — additive static support rewards accumulation rather than discrimination

**Location:** Introduction contribution framing; Approach: proposals/scoped assessment, utility, ranking.

The manuscript correctly labels scores heuristic, but the mechanism deserves one more concrete limitation. An existing source line containing an expected quote is cheap to propose and increases a hypothesis's ranking score. Multiple distinct quote parameters can supply multiple positive increments for the same underlying source expression, while paraphrased mechanisms create separate hypothesis IDs. AST checks search the whole file and can contribute larger weights without checking the nominated line. Neither `alternatives` nor the utility requires a check to distinguish competing mechanisms. Thus a confidently accumulated static-presence score can reflect check enumeration or wording rather than improved causal localization.

This is not an objection to static evidence per se, nor a demand for runtime evaluation. It matters because portfolio retention and final rankings use these scores, so their accumulation semantics directly shape the restart boundary.

**Remedy/type:** Explicitly discuss this score-inflation dependence and distinguish observation novelty from independent information. State whether semantic duplicate normalization is deliberately absent. A worked tiny example or deterministic diagnostic would make the limitation reviewable; do not present the constants as solving it.

### 4. Minor — running-example listing is not valid standalone Python as printed

**Location:** Background, Listing 1.

The listing places a leading space before top-level `def` and `from` statements, producing unexpected indentation if copied verbatim. `render` is also left undefined, although the text appropriately says it is illustrative rather than executable.

**Remedy/type:** Remove unintended top-level indentation; label the render dependency as omitted or supply a minimal definition if standalone execution is intended. This does not undermine the explanation of `False or True`.

## Questions for the authors

1. Is permanent suppression of identical logical probes after their hypothesis is pruned intentional? What exact behavior should occur when a role reintroduces a previously contradicted hypothesis?
2. What is the authoritative mapping from an Assessment to one of several predictions on its hypothesis? Can consumers recover that mapping without replaying the event stream?
3. Is every accessible observation intentionally eligible to influence model reasoning while only a subset can influence a regenerated hypothesis's executable score? Please distinguish these two retention paths explicitly.

## Must-fix for the scoped method

Resolve or explicitly specify the pruning/`seen` interaction, including loss of support and contradiction links on reintroduction. Complete the prediction-assessment identity semantics and disclose suppression of revised predictions following inconclusive checks. Explain the score-accumulation limitation sufficiently to prevent readers from treating novelty or heuristic utility as discrimination. Fix the listing indentation.

I would reconsider toward acceptance of the scoped method once these semantic gaps are addressed. The honest separation of guarantees from empirical questions is a strength, and I do not regard the registered results placeholders as a reason for this recommendation.
