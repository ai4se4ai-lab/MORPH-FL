# Literature search protocol

Independent Stage B; no manuscript prose read. Search date and cutoff: 20 October 2026 (UTC). Coverage: foundational work without lower date bound; targeted updates 2025–2026. This is a focused positioning search, not a systematic review or proof of priority.

Sources: arXiv abstracts/full HTML/PDF, ACL Anthology full paper, author-hosted papers, OpenReview (blocked direct access; indexed published cover plus arXiv accepted revision), IEEE Xplore (LS-CM full text blocked), Crossref metadata API, W3C recommendation. Third-party search results were discovery leads only. Search engine crawl/publication-age labels were not trusted as manuscript dates.

Queries included: Agentless AutoFL AgentFL fault localization; RGFL 2601.18044 LocAgent ARISE 2605.03117; MemFL 2506.03585 code localization memory 8yjWLJy2eX; LS-CM 11609447; Scaling Discovery Requires Forgetting; Improving Code Localization with Repository Memory arxiv; DeepFL/DeepRL4FL full text; spectrum fault localization Abreu; BugLocator; Reiter diagnosis; provenance; TSE author information and AI disclosure.

Include a source for a method claim only after opening its method, checking title/authors/version/year and finding a matching passage. Prefer verified publication metadata while retaining the exact method version URL. Exclude papers after cutoff, similarly named federated-learning systems, and inaccessible method claims. Citation CSV records evidence passages and exclusions. No performance numbers are imported into the paper.

Each web source has a 200-word total paraphrase budget across all delivered prose derived from it unless a tool states a larger limit; direct quotations are avoided. Comparison table uses <65 words/source, CSV <25, notes <50, leaving manuscript allocation small. Author should keep source-derived manuscript text to ~60 words for each closest source, counting introduction and table together, and ~30 for foundational sources. Metadata and independently reasoned MORPH-FL differences are not substantive source paraphrase. Never spend a fresh 200 words for a different URL/version of the same work.

Failures are retained explicitly: OpenReview browser challenge; IEEE full-text challenge for LS-CM; BM25 full monograph access failures; Abreu 2007 full paper not retrieved. These do not justify bibliographic guesses. Search found newer AgentFL publication called SoapFL; AgentFL preprint remains explicitly identified until published-method equivalence is checked. No “first” claim is licensed.

## Independent reviewer extension (same cutoff)
The independent positioning reviewer identified Ledger (arXiv2608.00808v1, 1 August2026) and AdaRepair-Mem (2609.20130v1, 17 September2026). The writer opened both full HTML methods on20 October2026 and added verified version-specific metadata and scoped comparisons. Ledger is a close execution-state predecessor and changes the residual framing: external ledgers, deterministic reuse and rendered state are established ingredients. The proposed distinction is the current-run hypothesis assessment/portfolio restart experiment. No priority claim is established. AdaRepair-Mem is cross-task stage-aware memory, not evidence that within-run restarts have already been tested.


## Author-requested MDE exposition and implementation alignment
After inspecting the current schemas, transformations, controller and tests, inspected primary TSE (Sánchez Cuadrado et al. 2017), ICSE (Salay et al. 2014) and EMSE (Martens et al. 2011; Höppner and Tichy 2024) papers. MDE_DESIGN_STUDY.md records the writing/justification practices adopted; MDE_IMPLEMENTATION_AUDIT.md records which mechanisms exist in this code. All four publication records were verified through Crossref. No new priority, semantic-preservation, or transformation-language superiority claim follows from this focused study.


## Localization-specific MDE extension
Focused search for studies that use executable models, metamodel footprints, contracts, transformation traces, and symbolic model analysis for fault localization. The five included primary methods and inspected sections are in citations_verified.csv. General model-transformation studies remain separate from this direct localization group. Excluded unrelated physical-system diagnosis and generic probabilistic-model papers from the MDE category. DOI metadata was checked through Crossref and publisher/institutional records.
