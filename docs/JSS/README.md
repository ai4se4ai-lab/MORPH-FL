# Does Forgetting Help?

Current paper: **Does Forgetting Help? Studying Context Reset Policies in LLM Fault Localization**.

[Reading PDF](main.pdf) · [LaTeX entry point](main.tex) · [Typesetting archive](jss-source.zip) · [Completed-study revision and reviewer responses](COMPLETED_STUDY_REVISION.md)

## Evaluation scope

The paper reports one fully collected study: 50 fixed issues from 12 Python repositories, two model checkpoints, four context workflows, seed 1, **400 investigations plus 100 deterministic retrieval controls**. It reports all specified cases, not selected completed portions of a larger experiment.

Earlier 139/219-issue snapshot results, three-seed comparisons, external-adapter scores and expanded-study inventories have been removed from the manuscript. The earlier manuscript and its evidence-integrity limitations remain preserved under `history/` and the repository's historical reports. They have not been relabeled as completed experiments or repaired.

The word “pilot” remains in original collection paths and manifests for traceability. The paper's reader-facing name is a fixed two-model study. Its single-seed scope, 132 reused Qwen records, post hoc interpretation, patch proxies, bundled treatment and known ambiguity-growth defect remain explicit. Collection completeness is not a claim of causal or confirmatory validity.

## Rebuild and verify results

From the repository root, with Node.js 22+:

```powershell
node docs/JSS/scripts/analyze_completed_study.mjs
```

This checks all 400 issue/model/workflow/seed keys, all 100 controls, eligibility, saved aggregates, reset exposure and paired outcomes; it verifies that the six generated tables exactly equal their reconstruction and writes [completed-study-audit.json](validation/completed-study-audit.json). Saved interval endpoints are parsed from the original report and its digest is recorded. Intervals are not newly bootstrapped.

To regenerate tables after intentional evidence/analysis changes:

```powershell
node docs/JSS/scripts/analyze_completed_study.mjs --write
```

The script reads only the study scores, summaries, controls, diagnostics, coverage/receipt metadata, report and selection manifest. It never runs an LLM or modifies frozen experiments. It does not freshly validate inaccessible raw prediction signatures/audits or reconstruct ranks from raw generations. These remain artifact-release responsibilities.

The historical `verify_evidence.mjs` audit is retained separately and points to the preserved historical manuscript. Its failed historical prediction-export hash is not an input to this paper.

## Compile

From the repository root in PowerShell:

```powershell
./docs/JSS/build.ps1
```

The source uses the supplied Elsevier `cas-sc` class and author-year references. The manuscript is a single file, `main.tex`, with all references in `references.bib`. The six result tables emitted by the analyzer into `generated/*.tex` are inlined verbatim in `main.tex`; if `--write` regenerates them, copy the changes into `main.tex`. The previous multi-file version is preserved in `history/before-single-file-rewrite/`. Note that the cas class ignores bare float specifiers on tables, so tables use `[pos=!htb]`.

The remaining scripts record one-time editorial changes. Do not rerun assembly scripts over the finished manuscript; only the completed-study analyzer and build script are intended for routine use.

## Review and release

Three independently assigned AI reviewers reviewed the completed-study plan and revised draft. Their reports are `reviews/bounded-{methods,empirical,editorial}-{initial,final}.md`. Exact feedback and integrated changes appear in [COMPLETED_STUDY_REVISION.md](COMPLETED_STUDY_REVISION.md). These are simulated reviews, not journal peer review or acceptance.

See [AUTHOR_ACTIONS.md](AUTHOR_ACTIONS.md) for current release/scientific work, [REVIEWER_SELF_CHECK.md](REVIEWER_SELF_CHECK.md) for difficult questions, [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) for publisher checks, and [validation/BUILD_REPORT.md](validation/BUILD_REPORT.md) for verification status.

The manuscript is complete as an editorial artifact. Public raw artifact/environment release, final declarations and the known-defect validation objection remain. No JSS acceptance or completed causal experiment is claimed.

