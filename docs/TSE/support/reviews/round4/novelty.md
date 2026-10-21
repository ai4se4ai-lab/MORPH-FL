# Stage G: fresh novelty and positioning review

Reviewed scope: Introduction, Background and Problem Definition, Approach, and Related Work in `docs/TSE/main.tex`, together with `references.bib`. Later sections were inspected only for consistency with the stated scope. No prior reviews, reader notes, or writer notes were consulted. Main-file SHA-256: `5a68234474eb0ea6ffdbea8ea04775b0fac2e60988e7c4f31b211c2f2f35368c`.

**Recommendation: Accept for the four-section novelty/positioning remit. Confidence: high (4/5).** This is not a recommendation to accept a completed TSE research article: results are explicitly placeholders, so empirical significance and publication readiness cannot yet be established. I found no major or mandatory minor correction to the novelty claims in these sections.

## Assessment

The residual research object is clear and appropriately narrow: an executable, task-specific policy combining scoped prediction assessments, retained observations, hypothesis-portfolio pruning, and dialogue restart. The manuscript does not claim invention of persistent memory, execution ledgers, caching, restart search, graph retrieval, or provenance. It expressly declines to treat its retention invariant as an algorithmic contribution. That positioning is credible even though the components themselves are established.

The closest-source discussion is unusually important here and is substantively fair. Ledger already supplies deterministic execution-state records, prompt state views, and redundant-action mediation. The manuscript names it as the closest execution-state predecessor and places the distinction at assessed hypotheses and the restart policy, rather than at externalizing observations. Ledger's examined method retains persistent interaction history, supporting the stated distinction without proving that Ledger could not be extended to restart. The text avoids that stronger claim.

The memory and restart comparisons also support the narrower scope. MemFL's project summaries and debugging guidance use pseudo-training bugs and buggy/patched methods; Repository Memory integrates historical artifacts and file summaries with LocAgent; AdaRepair-Mem routes retrieved prior repair experiences by stage. These are not equivalent to the within-investigation observation state studied here. Scaling Discovery Requires Forgetting does explicitly restart agent sessions and search state from a best scored candidate. The manuscript correctly treats that as a restart predecessor and explains the difference between an available optimization score and an unverified fault explanation. None of this establishes that the proposed combination will outperform the predecessors, and the manuscript does not say it does.

The experimental attribution limits are stated rather than hidden. In particular, the deterministic observation-text handoff is not presented as a strong model-generated summary baseline or a content-matched test of typed representation. Internal no-forgetting is not passed off as a Ledger reproduction. The no-forgetting, fixed-reset, context-only, and single-hypothesis variants can characterize this policy family; the text acknowledges that some contrasts change multiple features. Those qualifications make the claimed contribution smaller, but more defensible.

## Strengths

- Introduction lines 63–88 and Related Work lines 556–564 identify the predecessor overlap and the remaining question directly. The claim is an empirical instrument and policy study, not an inflated architectural advance.
- Background lines 91–103 separates location-proxy success, causal explanation, observation retention, and reconstructed-view sufficiency. This prevents a reset invariant from being mistaken for useful memory or correct diagnosis.
- Approach lines 264–305 and 377–405 discloses lost interpretation links, suppressed reassessment, heuristic score accumulation, and unbounded reconstructed observation views. These limitations materially bound what can be novel or effective, and the proposed evaluation is explicitly about this actual instantiation.
- Related Work and the closest-systems table distinguish reported capabilities from capabilities merely not established in the examined sources. Restricted upstream adaptations are labeled separately from unexecuted related systems.

## Concerns and remedies

1. **Severity: major for eventual whole-paper significance; not a defect in current four-section claim correctness. Location: contribution list, lines 82–88; Related Work lines 562–564; results placeholders. Type: missing empirical contribution, explicitly deferred.** Once the ledger, caching, memory, and restart ingredients are acknowledged as prior art, the instrument alone does not yet demonstrate a substantial research advance for TSE. The manuscript already recognizes this. Remedy: complete the registered comparisons and establish a reproducible useful policy finding or a well-supported, repeatable failure mechanism with practical implications. A favorable outcome is not mandatory, but an inconclusive package comparison plus the tautological retention property would not establish significance. This concern does not justify demanding invented results or stronger current novelty language.

2. **Severity: minor, optional. Location: Introduction lines 82–88 and Approach lines 493–525. Type: presentation of residual contribution.** The three contribution bullets mix the comparison protocol, prototype, and traceable state-update rules. These are legitimate deliverables but could read as three separate advances when the defensible novelty is their use to investigate one restart boundary. Remedy: in a final submission, lead with the specific finding supported by the completed study and present the prototype and contract as its enabling artifacts. The surrounding prose already supplies the necessary qualification, so this is editorial guidance rather than a current must-fix.

## Questions and must-fix status

- What reproducible policy conclusion or repeatable failure mechanism will the completed study establish beyond existing execution-state management and scored-search restarts? The present text correctly leaves that open.
- Are the eventual claims limited to the implemented package and its controls? The current wording says yes; preserve that boundary unless further experiments support narrower attribution.
- **Must-fix within the four reviewed sections: none identified for novelty/positioning.**
- **Before a whole-paper publication recommendation: empirical significance must be assessed from completed evidence.** This is an outstanding assessment, not evidence that the current method succeeds or fails.

## Independent primary-source checks

Checked the cited primary versions directly for the closest distinctions:

- [Ledger, v1](https://arxiv.org/html/2608.00808v1), especially execution-state management, persistent history, inform, and govern.
- [MemFL, v1](https://arxiv.org/html/2506.03585v1), especially dynamic-memory construction and pseudo-training inputs.
- [Repository Memory, v2](https://arxiv.org/html/2510.01003v2), especially memory sources and LocAgent integration.
- [AdaRepair-Mem, v1](https://arxiv.org/html/2609.20130v1), especially stage-aware routing and prior experience records.
- [Scaling Discovery Requires Forgetting](https://arxiv.org/pdf/2610.20563), especially the restart state and best-candidate evaluation boundary.

These checks support the distinctions reported above. They are not an exhaustive literature search or an implementation audit of MORPH-FL. The study, discussion, threats, and conclusion outlines are consistent with the four sections' restrained positioning and do not introduce an incompatible novelty claim.
