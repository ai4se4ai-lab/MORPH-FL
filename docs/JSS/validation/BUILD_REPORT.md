# Completed-study build and verification

Date: 28 October 2026. Current PDF: **29 pages**, including appendix and references; **71 cited bibliography keys** and five editable highlights.

## What was verified

- The fixed study has all 400 model/workflow/issue/seed keys and 100 control records, fifty selected issues, twelve repositories and 48 function-eligible issues per condition.
- `scripts/analyze_completed_study.mjs` independently reconstructs point estimates, reset exposure, paired hit/pool counts and all six generated tables from the complete score inputs. Saved interval endpoints and effects are parsed from the original report, which is included in input digests. The original bootstrap was not rerun.
- The audit checks citation keys, labels, highlight lengths and absence of excluded historical result values. It records hashes for all fifteen manuscript/section/table source files.
- Documentation checks verified 52 local links in the root README, JSS README and current revision record.
- Three independent AI reviewer agents assessed the completed-only plan and draft. Exact corrections were integrated; this is simulated review, not journal peer review.

## Typesetting

pdfLaTeX → BibTeX → pdfLaTeX → pdfLaTeX completed. The final log has no undefined citations/references, duplicate labels or rerun request. All 29 pages were rendered and visually inspected, including full-page checks of title, result tables and process/cost diagnostics. No clipped or overlapping text was observed. All six generated evaluation tables use full text width.

The supplied CAS keyword overlay emits its known 117.0831 pt zero-width-box diagnostic at maketitle, plus empty-anchor warnings. A sans-serif small-caps substitution remains. These are template/font diagnostics without observed clipping. BibTeX emits nine existing empty-pages warnings; missing metadata were not fabricated. The MiKTeX installation prints update/OS notices independent of manuscript content. Vendor files were not edited.

## Scope of assurance

Passing score-table reconstruction is not fresh raw generation/signature or benchmark execution validation. Public raw sources, traces, labels, environment and receipts still require release. No new model inference or corrected-runtime accuracy result was produced.

The earlier truncated historical prediction export is not an input to this paper. Its failed integrity check and prior manuscript are preserved separately; this revision does not claim that file was repaired. The complete score-only evidence base and historical evidence issue must remain distinct.

