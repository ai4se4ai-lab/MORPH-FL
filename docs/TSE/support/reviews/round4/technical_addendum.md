# Stage G amendment verification — round 4

Verified amended `docs/TSE/main.tex` SHA-256: `905dce7a604e0c10b25338ce8577903b89058548613d2fdebecae089cd4dee81`.

This is targeted verification of amendments to the four previously reviewed sections, not a new full review. The original `technical.md` remains unchanged.

**Amended-version recommendation: Accept for these four sections. Confidence: 4/5 on the technical specification.** All three requested textual clarifications are resolved. This does not recommend acceptance of an unfinished whole paper or establish empirical significance.

1. **Dynamic scope terminology — resolved.** Background now calls this dynamic-predicate support, explicitly identifies `causal_prediction` as the implementation label, and states that an exit code or output match need not distinguish the proposed cause from alternatives. This directly addresses my concern without pretending the implementation performs a causal-discrimination check.
2. **Batch-asymmetric alternatives — resolved.** The text following the probe-ordering algorithm now specifies that alternative IDs are captured during proposal processing, before later batch proposals enter the pool, with asymmetric counts and proposal-order dependence. This accurately exposes the inspected controller behavior.
3. **Retained behavioral interpretation — resolved.** The typed-state subsection now explicitly states that the latest accepted response replaces the active scope's behavioral fields and that these survive reset even when a related hypothesis is pruned. Their conjectural status is retained.

The additional source-presence amendment improves the earlier definition: scope now follows the assessed predicate and its producing procedure's match flag, with the numbered-line quote extent distinguished from the whole-file AST extent. This is consistent with the previously inspected assessment precedence. The revised audit language also properly uses assessable opportunities for event percentages and separately reports missing-artifact opportunities, avoiding treating missing data as no event.

**New issues:** None identified in this targeted amendment verification. The clarification of descriptive cost comparisons does not change the original review's requirement that eventual effectiveness and efficiency claims be supported by complete ranking and actual-cost evidence.

The original review's whole-paper evidence needs and contribution-sufficiency qualification still apply: practical significance must come from reproducible policy findings or informative repeatable failure mechanisms, not retention-ID equality alone. Primary-source bibliographic checking and completion of the empirical study remain outside this amendment sign-off.
