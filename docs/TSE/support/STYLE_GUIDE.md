# Manuscript style guide

Prepared using the installed skill-creator guidance; no academic-writing or LaTeX skill is installed. Skill roots inspected: /home/majid/.codex/skills/.system and /home/majid/.codex/plugins/cache/openai-curated-remote.

Write as a researcher responsible for each claim. Introduce the practical need before the record or formula that addresses it. Explain the implemented MDE mechanism through model responsibilities, links, transformation interfaces, and downstream decisions. Distinguish this implementation contribution from unsupported claims of MDE novelty or effectiveness. Keep observations, assessments, hypotheses, and conversation distinct. Explain static versus dynamic support at first use. Label the synthetic example every time its provenance could be mistaken for a run.

Use one main claim per sentence and one purpose per paragraph. Vary rhythm without synonym changes for defined terms. Prefer concrete mechanism names to evaluative adjectives. Introductions argue; approach paragraphs explain execution order; related work compares scoped capabilities. No generic opening, marketing, invented anecdote, deliberate error, or concealed AI assistance. Do not add sophistication through notation: define every symbol once, with domain.

Outcome-dependent prose belongs in claimslot macros. Never turn record retention into semantic sufficiency or accuracy. Distinguish implementation defaults from prospective study settings. Restricted baseline components must never be presented as full upstream systems. Cite only primary documents opened for this task. The final review remains independent, its output unedited, and acceptance is never guaranteed.

## Correction after author feedback
The earlier guide was applied too defensively. Main-text priority is the scientific argument and a complete understandable investigation, not exhaustive qualifications. Introduce familiar concepts before identifiers. Organize the approach around decisions and information flow, not software modules. Keep code-level exceptional behavior in a clearly referenced appendix. A substantive paragraph should connect its need, mechanism and consequence; splitting every technical caveat into a separate paragraph does not itself make an article readable. Use published TSE exemplars to inspect rhetorical structure, never to copy phrases. Reviewer acceptance and numeric readability scores are not substitutes for the author's judgment of writing quality.


## MDE exposition after the implementation audit
MDE_DESIGN_STUDY.md records inspected TSE/ICSE/EMSE examples. MDE_IMPLEMENTATION_AUDIT.md and mde_source_manifest.json tie the revised Approach to current code. Explain model-to-model mapping, extraction, execution and model-to-text rendering distinctly; do not dismiss the active model architecture as merely an implementation label. State partial validation and trace granularity precisely.


## Approach entry and progression
The Overview must contain exactly two prose paragraphs: the high-level method and its application to the running example. Keep component enumeration, T1–T7 mappings, notation, and controller details in the detailed subsections. Each subsequent subsection opens with a short motivation that connects its purpose to the preceding activity. The controller algorithm and a motivated walkthrough belong immediately after the Overview, before model definitions and transformation details; model retention at reset follows the reset-policy explanation.


## Explicit algorithm references
When prose refers to a displayed algorithm, name it with `Algorithm~\ref{...}`. Do not use vague substitutes such as "the procedure below," "this procedure," or "the reset procedure." When discussing a particular routine, name the routine and its containing algorithm. Keep generic uses of "procedure" for checks, execution methods, and other concepts that do not refer to a displayed algorithm.
