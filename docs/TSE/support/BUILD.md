# Build the standalone manuscript

Required source pair: ../main.tex and ../references.bib. No section/figure inputs are required; algorithms, vector figure, tables and all prose are inline. IEEEtran journal class and packages follow ../../tse-template.tex; unrelated LIFTDroid template macros were removed. T1 encoding is loaded before the class for XeTeX compatibility.

Typical TeX Live build from docs/TSE:

```
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

This session used Tectonic0.17.0 (XeTeX) with the official IEEEtran class and IEEEtran.bst. Its binary/cache and PDF inspection tools were isolated under /tmp and the user cache, not added to this repository. Draft placeholders are visible. Final mode intentionally fails without audited generated/results.tex. The result generator is a fail-loud stub, not an automatic claim writer.

Known toolchain diagnostics: benign underfull boxes and an upstream algorithm.sty comment encoding warning. No missing citations/references or overfull boxes in the final checked build. The manuscript has 11 pages including outlines/references; eventual evaluation length and the current TSE-specific submission limit require author assessment before submission.


## Current model-driven revision
The revised paper includes inline model-family and transformation-interface tables and an overview with M1–M4/T1–T7 annotations. Tectonic remains the build engine; all sources are inline in main.tex plus references.bib. The current verification record is build_verification.json; older page counts and figure-link statements above describe earlier versions. check_running_example.py now checks the MDE trace and a scripted real-controller reset, and check_synthetic_trace.py checks the constructed reset arithmetic. PYTHONPATH must include the repository src directory when running either script.

## Whole-paper presentation review (21 October 2026)
The final controller algorithm uses the standard small algorithm font. The placeins float barrier ensures Algorithm 1 appears before its walkthrough; ragged-bottom layout avoids stretching paragraph gaps around the overview figure and algorithms. Current output is 22 pages. Both running-example scripts, 40 targeted tests, cross-reference/citation-key checks, and final layout checks passed. See PRESENTATION_REVIEW_20261021.md and build_verification.json; these records supersede earlier page-count statements without changing historical experiment manifests.
