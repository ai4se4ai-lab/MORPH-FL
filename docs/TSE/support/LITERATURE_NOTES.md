# Method notes and writing constraints

All core keys and primary URLs are in citations_verified.csv. References.bib now has 30 usable entries after the related-work and MDE expansions. Preprint year follows the specifically opened revision when key uses 2024 (MemGPT); latest publication metadata is not inferred from a template's keyword string.

MemFL is the closest direct memory competitor: its IV-D2 builds guidance from pseudo-training bugs with buggy/patched methods. That differs from preserving observations in one target investigation. Repository Memory uses prior commits/issues and active-file summaries (§3); it therefore defeats a general claim that repository localization lacks persistent memory. AgentFL already has State Storage, a parser and prompt generator (III-A), so typed task outputs alone are weak novelty.

RGFL §3.1 reasons over candidates separately before ranking. LocAgent §3 exposes typed graph navigation and an event log. ARISE §3 bundles structural and def-use evidence under a token budget. These defeat claims that structural navigation, intermediate representations, explanations, or structured context are new. The examined ARISE method is arXiv v1, 4 May 2026, with Shahd Seddik and Fatemeh Fard; newer website metadata must not be silently mixed into this version.

Forgetting §3 resets both sessions and visible candidate history while retaining the best scored candidate. Its four tasks concern optimization, not fault localization. Use it to motivate testing search-state policies, not as proof of fixation or restart benefit in localization. Reflexion §3 retains reflective text across trials. MemGPT §2 pages between context and external storage and manages the queue/summary. Summarization is therefore an established alternative that the controlled summary condition must take seriously.

BugLocator §III ranks files using report/source similarity plus prior similar fixes. DeepRL4FL §§IV–VIII learns from coverage, execution/dependency information and source; it is also a verified primary source for explaining the contrast between observed failure and fault location (§II) and the need to avoid calling source inspection dynamic evidence.

Reiter §§2–4 uses logical models and observations for consistency diagnosis; MORPH-FL is not thereby a model-based diagnosis implementation. W3C PROV-DM §§2/5 models provenance of entities, activities and derivations; logging provenance does not prove a diagnosis true or implement the standard.

IEEE author guidance: https://www.computer.org/publications/author-resources opened; it delegates page limits to each journal and gives regular/special journal abstracts 100–200 words. An old TSE information PDF was discovered but must not be treated as current page-limit authority. https://ieee-cas.org/publications/using-ai-generated-content-ieee-article states acknowledgement disclosure should name system, sections and extent. Verify current TSE-specific page limit separately; no claim of a verified current limit is made here.


Related-work expansion: SmartFL, LLMAO, and KBL primary methods and publication metadata were inspected and added. RELATED_WORK_STYLE.md records the venue-specific writing study and the resulting group comparisons. The new prose distinguishes retrieval, execution analysis, learned prediction, graph navigation, reusable knowledge, current-task state, and restart policies. No experimental superiority is inferred from a representational difference.

MDE expansion: four primary sources now support model/metamodel/transform descriptions and related-work positioning; see MDE_DESIGN_STUDY.md. Method implementation details come from the current code audit, not by analogy with those papers.


## MDE techniques specifically for fault localization
Added a dedicated MDE-Based Fault Localization subsection, separate from general transformation engineering. Opened five primary methods and verified their publication metadata: SimFL/iSimFL (STVR 2016), metamodel-footprint localization (TSE 2015), transformation-rule SBFL (TOSEM 2018), static/dynamic hybrid localization (JOT 2022), and symbolic DSLTrans localization (SoSyM 2024). The SimFL method was inspected in the author's 2015 technical report, Sections 3–4; it is linked explicitly rather than claimed to be the publisher PDF. Oakes et al. appeared online in 2023 and in the 2024 issue. No performance figures or priority claims were imported.

Comparisons distinguish the artifact being debugged, the localization evidence/oracle, and the role of MDE: executable blocks or transformation rules with slices/contracts/traces/path conditions versus MORPH-FL's versioned source model and evolving hypothesis/investigation models. M1 natural-language invariants are not OCL contracts; T6 assessment is not rule-coverage suspiciousness; T7 reconstruction is not symbolic verification. Potential backend reuse is identified as requiring integration and evaluation.
