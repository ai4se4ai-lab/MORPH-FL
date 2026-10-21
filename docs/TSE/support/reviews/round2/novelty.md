# Independent novelty and positioning review — round 2

Scope: Sections 1–4 of `docs/TSE/main.tex` and `references.bib`. I did not read earlier reviews or writer support notes. This is a review of the front half, not an assessment of unreported empirical findings.

**Recommendation: Major Revision. Confidence: high on the closest-work distinctions, medium on eventual TSE contribution significance.**

The front half presents a coherent and potentially publishable research question: what should a fault-localization investigator retain when its dialogue is restarted, and does the resulting policy justify its cost? It does not yet establish a substantial new technique independently of its future evaluation. I would not reject it for merely using familiar components, nor accept it on the strength of the retention invariant. The necessary revision concerns the scientific contribution that the specification actually supports. Missing results would separately prevent acceptance of a complete TSE research article; that is not being counted here as a front-half defect.

## What is new, and what is already established

The plausible residual contribution is the operational combination of source-versioned observations, explicit scoped assessments, a bounded hypothesis portfolio, and adaptive dialogue restarts in budgeted fault localization. The paper now explicitly relinquishes novelty claims for external memory, execution ledgers, lexical retrieval, graph navigation, and restarting search individually. That is the right boundary.

The closest source checks support the manuscript's account:

- [Ledger, Sections 3.1–3.4](https://arxiv.org/html/2608.00808v1) maintains deterministic execution state alongside persistent history, renders it before decisions, and mediates repeated actions. Its history is retained; the examined method does not define this paper's portfolio reset. Thus the Ledger distinction is legitimate, but externalizing observations and caching repeated checks are established overlap.
- [Scaling Discovery Requires Forgetting, Sections 3.1–3.3](https://arxiv.org/pdf/2610.20563) discards sessions and search state, retaining the best candidate and score. The difference between a scored candidate and unverified fault explanations is substantive. The paper does not establish that retaining several explanations is better; it appropriately poses that as a question.
- [MemFL, Section IV-D](https://arxiv.org/html/2506.03585v1) uses project/class summaries and guidance developed from pseudo-training bugs with buggy/patched methods. [Repository Memory, Section 3](https://arxiv.org/html/2510.01003v2) exposes historical commits/issues and cached summaries of active files. These support the distinction between prior repository/task knowledge and a ledger of observations from the current investigation. Neither justifies claiming memory for localization as new, and the manuscript does not do so.

These sources also substantiate the corresponding bibliography titles and cited method distinctions. I found no material misrepresentation in those closest-work descriptions. The table's explicit “not stated” qualification is preferable to treating an omitted feature as proof of absence. I did not independently certify every bibliographic field or every table cell.

## Strengths

1. **Precise claim boundaries (Sections 1–2 and 3.7).** Record retention, reconstructed-view sufficiency, ranking quality, and causal validity are separated. The source-only benchmark boundary is especially valuable: quote/AST success is not sold as failure reproduction.
2. **An executable research object (Section 3).** Portfolio selection, reset gates, caching, ranking, and stopping are concrete enough to inspect. The synthetic reset step explains what is retained without passing off an invented recovery as a result.
3. **Fairer positioning (Sections 1 and 4).** Ledger is recognized as the closest execution-state predecessor. Restricted localization adaptations are distinguished from reproductions of full upstream systems. The simple observation-text control is described accurately rather than called a generic representative of summaries.
4. **Falsifiable value proposition.** Unfavorable outcomes can favor the simpler control. The paper does not require every component or every restart to help in order to report an honest result.

## Concerns and remedies

### 1. Major: the distinctive assessment layer is not reliably preserved as an executable relation

**Location:** Sections 3.2 and 3.4, especially the missing prediction/probe reference in assessments, handled logical probe IDs surviving resets, and suppression of reassessment after changed predictions.

The observation ledger survives, but the interpretation that makes this more than a conventional cache may disappear when a hypothesis is pruned. Recreated hypotheses may not regain scores or support links, and a changed prediction can fail to receive a fresh assessment. These are candidly disclosed; disclosure prevents overclaiming but does not demonstrate that the proposed hypothesis/observation/assessment architecture realizes its intended scientific role. This matters directly to novelty: the new ingredient is not simply that a dictionary is left untouched during reset.

**Remedy/type:** Implementation and claim alignment. Either make prediction-to-observation assessments persist and reassessable across reconstructed hypotheses, or explicitly make the loss/suppression behavior part of the studied policy and investigate its consequences. The latter is permissible, but the contribution must remain a prototype policy study rather than a robust evidence-reuse architecture. No full formal diagnosis engine is required.

### 2. Major: the control supports a package claim, with limited ability to explain why the package matters

**Location:** Introduction, Section 3.1, Section 3.10 and Table of variants.

The deterministic observation-text control removes hypothesis records, predictions, behavior fields, and relations as well as changing dialogue policy. The manuscript correctly acknowledges this. Nevertheless, its distinctive research rationale concerns separating checked facts from explanations, and a favorable result against that control would not by itself show that such separation, rather than additional retained information, helps. The existing no-forgetting, fixed-reset, context-only and single-hypothesis contrasts are useful but cannot establish the representation claim on their own.

**Remedy/type:** Experimental-identification requirement or further narrowing. For a mechanism-level claim, include a matched-information handoff containing the same observation, hypothesis, prediction and relation content under a simple serialization, with reset timing held fixed. If the intended contribution remains only the complete package, state that as the primary claim and treat representation-level explanations as untested. An LLM-written summary and a full reproduction of every memory system are not mandatory.

### 3. Moderate: retention is an implementation invariant, not yet a substantial standalone research result

**Location:** Contribution list in Section 1 and retention property in Section 3.7.

The proof is correct for the defined operation: reset never writes the ledger. This is useful contract documentation, but its scientific weight is small. It establishes neither deliverability of an indefinitely growing observation view nor continuation quality. The paper already says this, so the issue is contribution emphasis rather than a false theorem.

**Remedy/type:** Positioning. Lead the eventual contribution story with a tested policy or a generalizable finding about restart boundaries. Present retention as a verified contract supporting that study. A negative finding can still be useful if it identifies a repeatable failure mechanism or conditions under which the simpler alternative wins; a collection of null contrasts alone would not automatically establish TSE significance.

### 4. Minor: tighten how architectural distinctiveness is presented

**Location:** Sections 1 and 4, closest-systems table.

Ledger's execution/semantic distinction and ordinary action/observation agent interfaces already cover part of the conceptual vocabulary. The residual novelty should consistently be stated as scoped prediction assessments plus portfolio reconstruction under the specified reset policy, rather than allowing “observation versus interpretation” alone to read as an invention. The current text is mostly careful; one concise synthesis after the table would make the distinction easier to evaluate than repeated caveats throughout the method.

**Remedy/type:** Editorial positioning. No new baseline is demanded by this concern.

## Questions for the authors

1. Is the intended eventual contribution a reusable evidence-management architecture, or an empirical study of this particular restart policy? The present implementation supports the second more strongly.
2. Which specific outcome would justify attributing benefit to scoped assessments, as distinct from preserving more hypothesis content or selecting different reset times?
3. If retained observations fit the ledger but no longer fit the reconstructed request, what conclusion will the paper draw about the policy? The declared unbounded view and context-limit termination should remain visible in the final interpretation.

## Must fix before a strong positive recommendation

- Resolve or deliberately study the assessment/reassessment loss at the reset boundary; keep the architectural contribution consistent with that choice.
- Align the central causal/mechanistic interpretation of comparisons with what the controls identify; add the matched-information control if representation-level claims are retained.
- Establish contribution significance through completed evidence, separately from the valid but elementary record-retention invariant. This is an acceptance requirement for the complete article, not a claim that Sections 1–4 should already contain results.

I see no requirement to invent a new graph algorithm, prove causal localization from static evidence, reproduce all related systems, or claim that previous memory methods fail. The paper's narrow question is defensible; the remaining challenge is showing that the distinctive boundary yields knowledge beyond a well-documented assembly of existing mechanisms.
