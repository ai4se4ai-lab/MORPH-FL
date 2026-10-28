# Pilot output-quality review

## October 28 status and provenance check

Live scheduler inspection found no queued or running pilot jobs. Extended-study
jobs remain `JobHeldUser`; the tracker still reports 9,926/99,544 progress records.
The saved independent verification remains 400/400 primary predictions and
100/100 retrieval controls. No new inference results were produced by this check.

A synthetic regression demonstrated that the snapshot checker accepted a
self-consistent prediction/configuration pair using an unpinned model revision
or a changed shard count. It also failed to compare the deployed protocol's
digest with the pilot manifest. These are validation gaps, not demonstrated
changes to the completed pilot's results.

The local checker now validates the protocol digest, model revision, seed,
shard count/range, filename identity and primary-study mode against the frozen
pilot settings before scoring. Regressions reject changed revisions, shard
settings, preflight records and renamed cells. A separate read-only metadata
inspection confirmed that all 52 saved primary configurations on UFV match
these identity constraints and that the frozen protocol digest matches the
manifest. This metadata check did not reread or independently reverify all
prediction contents. Frozen deployment sources and saved predictions are unchanged.

## October 25 status check and local correction

Live SSH inspection at 18:49 UTC confirmed 400/400 primary records and the
completed coverage report. No pilot jobs remain queued or running. Extended
jobs remain explicitly `JobHeldUser`; this is the documented deferral, not a
new scheduler failure. Slurm accounting is disabled, so historical job success
is assessed from saved receipts and final verification rather than `sacct`.

A read-only inspection of the archived DeepSeek `astropy__astropy-7336`
MORPH trace found valid empty responses in steps 0–2. Each response copied the
unresolved behavior ambiguity, which `complaint_to_contract` then appended
again: the next requests contained two and then three identical messages.
This is a demonstrated prompt-growth defect, not evidence that all empty
predictions are parser failures or that deduplication will improve accuracy.

The local transformation now deduplicates ambiguity strings in their original
order and appends its unresolved-behavior message only when absent. A 16-round
regression checks that repeated empty responses preserve uncertainty without
growing duplicate messages. This correction is not deployed into the frozen
pilot or full-study runtime; any inference validation requires a separately
versioned development run. Existing predictions and scientific results remain
preserved. The status page now explicitly reports when no pilot jobs remain.

**Update, October 25:** the pilot is complete. See the
[final results and diagnostic counts](pilot_results.md); the partial observations
below are retained as the diagnostic history.

Diagnostic snapshot: 2026-10-24 22:45 UTC. The pilot is incomplete.

The scheduled read-only diagnostic job **18135** inspected DeepSeek prediction
audits. This is an output-quality limitation, even though inference tasks are
finishing successfully. It does not establish that the scheduler or GPU runtime
is failing.

| Workflow | Completed records inspected | Records with final hypotheses | Invalid-response events |
|---|---:|---:|---:|
| MORPH | 29 | 4 | 37 |
| No-forgetting | 27 | 4 | 35 |
| Fixed-reset | 27 | 4 | 37 |
| Stateless-summary | 27 | 24 | 31 |

These live per-workflow counts use different issue sets; event counts can exceed
record counts. Every invalid-response event above reports
`No valid localization JSON object with a hypothesis list`. Stateless-summary
also has seven invalid-hypothesis events involving source locations or mechanisms.
Most records terminate at the context/token allowance. These are recorded
outcomes, rather than failed jobs that should be silently discarded or retried.

On the separate matched 26-issue DeepSeek report snapshot, MORPH,
no-forgetting and fixed-reset each have hypotheses on only 4 issues;
stateless-summary has them on 23. All completed records report generated tokens.
Having generated tokens therefore does not establish useful localization output.

The controller retains its retrieval ranking when the final hypothesis pool is
empty, and derives function rankings from hypothesis locations. Empty pools
therefore limit what these results can say about hypothesis-based localization;
they can help explain fallback-like file results and weak function results.
This is an implementation-based interpretation, not a causal diagnosis of every
prediction. Invalid JSON alone does not explain every empty final pool: valid
empty responses and hypothesis retention also need trace inspection.

Keep the current frozen pilot and its unfavorable outcomes intact. Before
expanding or modifying the method, inspect malformed and valid-empty responses,
context allocation, and hypothesis creation/retention on development cases.
Any resulting prompt/parser/policy revision needs its own version and validation;
its rerun must not overwrite this pilot or be treated as independent confirmation.

Evidence: [diagnostic JSON](../../experiments/pilot/results/quality.json),
[interim comparison](../../experiments/pilot/results/interim-analysis/report.md),
[diagnostic collector](../../experiments/pilot/quality.py), and
[ranking construction](../../src/morph_fl/search/controller.py:476).
