# Runtime and scheduling recovery — October 20, 2026

Active run: `ufv-full-v12-20261020-01`.
Deployment: `/home/babaei/projects/MORPH-FL-full-v12-20261020`.
Remote repair evidence directory (**M** below):
`/home/babaei/projects/MORPH-FL-full-v12-20261020/hpc/logs/ufv-full-v12-20261020-01/maintenance/ast-recovery-20261020`.

## Problems and repairs

| Problem | Cause / contribution of repair | Action and evidence | Current verification |
|---|---|---|---|
| Retrieval stopped at 1,412/1,414 | Recursive `ast.NodeVisitor` over a deeply nested expression in the final `sympy__sympy-24909` source | Explicit-stack generator visitors preserve DFS order, scoped definitions and graph outputs; deep unresolved call formatting falls back to source text if unparse overflows | GPU validation job **17970** reproduced the original crash and analyzed all 873 files with the patch: 22,347 symbols, 788,852 relations, zero diagnostics. `M/validation.json` |
| Resume would load a 209 GB prediction file into memory | Both `read_rows(out)` and interrupted-tail recovery used whole-file allocations | Stream both passes, validate all completed record keys and provenance, and preserve invalid final fragments before truncating them | Unit regression verifies no whole-file `read_bytes` call; recovery job **17979** is processing the existing checkpoint. Exact record completion still requires its receipt |
| Primary arrays 17937–17941 disappeared | Their `afterok` dependency canceled them after retrieval failed; `afterany` side stages then started | Stop the superseded downstream graph, preserve outputs, and submit a replacement from the unchanged frozen configuration only after full retrieval success | `M/recovery.json` records attempted scheduler operations; `M/restored_graph.json` will record the successful replacement graph |
| New predictions must disclose repaired runtime | Silently changing a frozen source identity would invalidate provenance | Keep scientific protocol bytes unchanged; allow only exact original/replacement hashes in `experiments/full/runtime_maintenance.json`; new records carry its hash | Original protocol SHA-256 remains `3afba2e46e120a3e35fc585e16ab9ddd474605ec93a5294abd8c618ad740f076`; original sources and manifest versions retained in M |
| Failure visibility without Slurm accounting | UFV disables `sacct` | Read step and job-end ledgers plus persistent maintenance incidents; retain failed attempts after recovery | Study document includes failures and maintenance validation, not an inference of scientific completeness |
| Cron repeated completed transfers | Every terminal check previously copied the same collection again | Reuse a successful local transfer when the artifact inventory is unchanged and the destination exists | Final copy still occurs when missing or changed; large graph/evidence archives remain on UFV |

The 30 separate preflight results and all completed study predictions are retained.
No checkpoint, model revision, benchmark membership, seed, workflow, precision,
context, sampling, token budget or metric definition is changed. The patched v12
suite was constructed from the actual deployed source; unrelated future local
v13 scientific changes were excluded. Fifty-one targeted local tests passed, including deep traversal, tail preservation,
source identity checks, reporting and idempotent graph recovery. Ordinary-source analyzer outputs compared
exactly with the original on three local module trees and a scheduled scoped fixture.

Deterministic retrieval recovery and analyzer validation use an idle P5000 GPU
allocation; they perform no LLM inference. Replacement model jobs retain their
original one/two-A30 requirements and throttles. Computation remains in scheduled
jobs, with lightweight submission/receipt checks on the login host.

## Recovery attempts retained for diagnosis

| Attempt | Outcome / diagnostic | Evidence |
|---|---|---|
| Validation 17969 | Harness import failed because the original backup has a `.original` suffix; fixed with an explicit `SourceFileLoader` | `M/validation-17969.err`; later 17970 passed |
| First retrieval retry 17973 | `MemoryError` exposed the second whole-file allocation in interrupted-tail recovery; subsequently patched | Remote `steps/retrieval/all/controls.log`; `M/events.json` |
| First replacement main arrays 17974–17978 | Canceled following failed retry 17973; they produced no primary records | Original `jobs.tsv`; replacement submission waits for verified retrieval |
| Array dependency edits | Requeue/hold/update commands partly operated on materialized tasks and returned errors for pending/running siblings; superseded graph was stopped and will be submitted cleanly | Exact commands and available return codes in `M/recovery.json` |
| Local broad full-study test | 13 tests passed; analysis test could not import unavailable local `matplotlib` | This is a local test-environment limitation; scheduled validation uses the installed UFV container |

## Automatic continuation and monitoring

The existing **30-minute tracker cron** remains installed on comp370. A temporary
additional cron entry runs `hpc/ufv/recovery_watch.py` every five minutes, guarded
by `flock`. It checks the fixed remote receipt path, never executes inference,
and launches no replacement jobs until a complete **1,414-record retrieval
receipt**, the AST validation and all five inference gates are present.

The remote idempotent helper `hpc/ufv/restore_after_retrieval.py` persists each
replacement stage ID in `M/restored_graph.json`. All remaining stages are rebuilt
from the frozen graph, so primary work precedes resumed side work and collection
waits for the new arrays. Existing completed cell/record checkpoints are reused.
The temporary cron entry removes itself after successful graph restoration; the
regular study tracker continues. Authentication uses the dedicated server key.

Local callback evidence: `hpc/logs/ufv-full-v12-20261020/recovery.log` and
`recovery-status.json`. The generated [study tracker](study_progress.md) remains
the live source of progress and scientific completion status. A submitted job
or successful runtime validation does not imply the full study has finished.


## October 20, 18:03 UTC verification

Retrieval has written all 1,414 conditions; receipt publication is waiting for
lossless compaction of the existing checkpoint. Recovery 17979 is active on
node3, with no new exception in its attempt. A process-metadata check found the
compactor reading **90.1 GB of 224.8 GB (40.1%)**. This is input-byte progress,
not a percentage of the study or a completion receipt. Memory use at that
observation was about 6.3 GiB against a 32 GB reservation; shared storage has
26 TB available. No restart or checkpoint rewrite was needed.

The temporary recovery callback now saves read-only `/proc` telemetry every
five minutes to local `hpc/logs/ufv-full-v12-20261020/recovery-io.json`.
`study_progress.md` includes its timestamp and compaction byte progress on each
refresh. Optional telemetry failure cannot prevent the receipt-based graph
restoration check. The probe targets the current recovery node, node3; after a
node change it may be unavailable until updated. It does not inspect model
inputs or run computations outside scheduled jobs. Fourteen reporting, telemetry
and recovery tests passed for this update.


## Recovery completed — October 20, 19:17 UTC

Retrieval 17979 completed successfully. Its receipt verifies **1,414/1,414**
conditions; the step ledger records exit code 0. The prediction file is now
about **41 MiB**, with full graphs retained in content-addressed storage.

The continuation helper submitted all **26** remaining stage jobs from the frozen
configuration. `M/restored_graph.json` records their commands and IDs. Two Qwen
primary tasks in array **17980** are running. The other families and side stages
wait on their restored dependencies. Primary-family arrays are **17980–17984**;
final collection is **18007**. Existing ablation records remain available for
resume. This establishes successful recovery, not full-study completion.

The temporary five-minute recovery cron entry removed itself after submission.
The regular half-hour tracker cron remains active. The living study table now
shows retrieval **COMPLETE (receipts verified)** and primary comparison **RUNNING**;
historical failures are retained with recovery evidence.

## October 20, 21:06 UTC — malformed AST probe repair

Live inspection found Qwen task `17980_1` failed after 75 completed records.
`steps/main_m0/0__2__0/investigate.log` records an `AttributeError` from
`query.get(...)` because a generated AST query was a string. The executor now
rejects non-object queries with `ValueError`, which the existing controller
records as a `probe_error` and handles without terminating the study cell.
Valid query behavior and scientific settings are unchanged.

The minimal executor patch is installed locally and in the frozen deployment.
The previous executor and maintenance manifest are preserved remotely under
`L/maintenance/probe-query-20261020/`. The updated maintenance manifest records
original/replacement hashes; all frozen source hashes and the unchanged protocol
hash were verified. Twenty-four local method and maintenance tests passed,
including malformed string, null, list, number and boolean queries.

`scontrol requeue 17980_1` succeeded at 21:06 UTC. Slurm confirmed restart count 1
and PENDING / JobArrayTaskLimit; the existing two-task throttle is preserved.
The retry has not yet run, so resumed inference is not yet verified. Two other
Qwen tasks remain running with their already loaded runtime. Their processes
were preserved; future task starts load the patched executor. The live snapshot
at 21:05:27 UTC contains 1,637/99,544 study records: 1,414 retrieval, 156 primary,
and 67 retained ablations. All five inference gates passed. Other model families
and side stages are dependency-queued. Shared UFV storage has 26 TB free, local
storage 31 GB free, and the independent 30-minute cron remains active.

## October 21 live audit — missing primary task recovery

Live inspection found original Qwen tasks `17980_0` and `17980_2` had failed
with the same malformed AST-query error in processes loaded before the executor
repair. Both tasks had expired from Slurm's job cache and had no completion
receipt. The existing task `17980_1` remains queued for its previously requested
retry. Successful later cells demonstrate the patched runtime can proceed.

Replacement array **18012**, containing only tasks **0 and 2**, was submitted
from the original recorded command with the same 12-hour, 40G, one-A30 resources
and two-task throttle. It waits for array 17980 to finish, avoiding extra
concurrent inference. DeepSeek array **17981** now waits on both 17980 and
18012; the remaining model/side/collection chain consequently waits as well.
Completed prediction records remain available for normal resume. The recovery
is queued, not yet verified by successful receipts. Exact commands and Slurm
verification are retained remotely in
`L/maintenance/probe-resume-20261021/recovery.json`.

All deployed frozen-source and maintenance hashes were verified against the
unchanged protocol before submission. No additional compute-source patch was
needed. Thirty-five local method, maintenance and tracker tests passed using
`PYTHONPATH=src python3 -m unittest` (pytest is not installed locally). The tracker
phase overview now reflects the complete model gates and receipt-verified
retrieval. UFV shared storage has 26 TB free; local storage has 31 GB free.
The independent half-hour reporting cron remains installed.

## October 21, 04:59 UTC — full-run health audit

Refreshed the live tracker: **2,326/99,544** study progress records, with all
five inference gates passed and retrieval receipt-verified at 1,414/1,414.
Four Qwen primary cells have successful step exits and completion receipts.
Tasks `17980_7` and `17980_8` are running; their logs show ongoing case execution.
The three earlier AST-query failures remain historical unresolved attempts:
`17980_1` is queued for retry, and replacement array `18012` covers tasks 0 and 2.
DeepSeek waits for both arrays. Later families, side studies and collection
remain dependency-queued. No new failed step was found. Recovery completion
still requires successful receipts; full scientific completeness is not established.

The unchanged deployed protocol and all **57 frozen source identities** passed
hash verification, including the explicitly recorded maintenance replacements.
Shared storage has 26 TB free. Local validation passed **116 tests** using the
existing `/tmp/morph-review-venv` environment and `PYTHONPATH=src`; the system
Python lacks optional matplotlib/libcst dependencies. The HPC self-test also
passed shell syntax, compilation, full/smoke graph validation and submission dry
runs. Stale README references to the detached monitor, historical collection job
and active deployment were corrected. No compute source or scheduler changes
were needed in this audit. The independent half-hour tracker remains active.

## October 21, 06:07 UTC — launcher warning repair

The refreshed snapshot contains **2,434/99,544** study progress records, an
increase of 108 since the previous audit. Both active primary tasks continue
writing completed cases. No new failed step was found; previous AST-query
retries and downstream dependencies remain queued as recorded above.

Container stderr exposed `scontrol: command not found` in distributed setup.
Applied the existing local `setup_distributed` function to the deployed
`hpc/slurm/common.sh`: single-node jobs use hostname when scontrol is absent,
explicit MASTER_ADDR is retained, and missing multi-node configuration fails
clearly. This launcher file is outside the protocol's frozen scientific source
set. The original file, original/replacement hashes and repair timestamp are
preserved under `L/maintenance/launcher-20261021/`. Bash syntax, isolated
single-node/explicit-address/multi-node-error checks and the HPC self-test pass.
Running processes were preserved; future task starts load the launcher repair.

A tokenizer warning about a 77,846-token candidate input was followed by case
completion. The deployed inference adapter checks input length against the
16,384-token context before calling generate and raises BudgetExceeded when
there is insufficient space. No context or scientific parameter was changed.
Shared storage still has 26 TB available. Full-study completion remains pending.

## October 21, 14:45 UTC — full-run audit

Refreshed the live tracker: **3,173/99,544** study progress records. All five
model gates passed, retrieval remains receipt-verified at **1,414/1,414**, and
10 Qwen primary cells have successful step exits. Tasks **17980_13** and
**17980_14** are running and writing completed cases; their current stderr files
are empty. No new failed step was found. The three historical AST-query failures
remain pending recovery: task 17980_1 and replacement array 18012 (tasks 0 and 2).
DeepSeek and the subsequent stages remain dependency-queued. These queued
recoveries still require successful receipts before being called resolved.

Verified all **57 deployed frozen source identities**, recorded maintenance
replacements and the unchanged protocol hash. All **116 local unit/integration
tests** passed in `/tmp/morph-review-venv`; the HPC self-test passed shell syntax,
compilation, full/smoke graph validation and submission dry runs. Shared storage
has 26 TB available and local storage has 31 GB. The half-hour tracker cron
remains installed. No additional compute-source patch or scheduler change was
needed. Scientific completeness and final outcomes remain pending.

## October 21, 18:07 UTC — repeat live audit

The refreshed snapshot reports **3,473/99,544** study progress records, up 300
since the previous audit. **12 Qwen primary cells** now have successful step
exits. Tasks **17980_15** and **17980_16** are actively completing cases; their
stderr files and those of the three preceding tasks are empty. No new failed
step is recorded. All five inference gates and complete retrieval remain valid.
The three historical AST-query failures still await their scheduled retries;
full-study completeness remains pending. All **57 deployed source identities**
and the unchanged protocol passed fresh hash verification. Shared storage has
26 TB available. No additional runtime repair or scheduler change was needed;
the live tracker was refreshed without changing scientific settings.

## October 21, 20:17 UTC — full-run health audit

The refreshed tracker contains **3,663/99,544** study progress records. All
five inference gates passed; retrieval remains receipt-verified at 1,414/1,414.
Fourteen Qwen primary cells have completion receipts. Live scheduler inspection
shows tasks **17980_17** and **17980_18** running, with the two-task throttle
preserved. The latest five primary stderr files are empty; no new failed step
appears in the tracker. Historical AST-query failures remain pending recovery:
task 17980_1 is queued, replacement array 18012 covers tasks 0 and 2, and
DeepSeek 17981 waits on both arrays. These failures require successful retry
receipts before being marked resolved.

Fresh hash verification passed for all **57 deployed frozen sources**, recorded
maintenance replacements and the unchanged protocol. All **116 local tests**
passed in `/tmp/morph-review-venv`; the HPC self-test passed shell syntax,
compilation, full/smoke graph validation and submission dry runs. Shared storage
has 26 TB available. No additional compute-source repair or scheduler change
was warranted. The tracker was refreshed and half-hour monitoring continues;
full-study completion and final scientific outcomes remain pending.

## October 22, 00:52 UTC — full-run health audit

The refreshed snapshot reports **4,083/99,544** study progress records, with
**16 primary completion receipts**. All five model gates and complete retrieval
remain valid. Scheduler inspection confirms Qwen tasks **17980_19** and
**17980_20** are running with the original two-task throttle; the latest eight
primary stderr files are empty. No new failed step is recorded. Historical
AST-query failures still await the queued task 17980_1 and replacement array
18012 (tasks 0 and 2); DeepSeek 17981 correctly waits for both arrays. Successful
retry receipts are still required before those failures can be marked resolved.

All **57 frozen source identities**, recorded maintenance replacements and the
unchanged protocol passed verification. All **116 local tests** and the HPC
self-test passed, including full/smoke submission dry runs. Shared storage has
26 TB available. The half-hour tracker entry remains installed and the cron
service is active. Slurm accounting remains disabled, so failure visibility
continues to use step ledgers and logs. No new repair or scheduler change was
warranted; full scientific completeness and final outcomes remain pending.

## October 22, 01:25 UTC — live follow-up audit

The refreshed tracker reports **4,118/99,544** study records (+35 since the
00:52 audit), with 16 primary completion receipts. Tasks 17980_19 and 17980_20
remain running; both investigation logs have reached 132/132 case records at
01:22 and 01:23 UTC respectively, but their completion receipts have not yet
been published. Record coverage alone is not treated as cell completion.
The latest eight primary stderr files are empty and no new failed step appears.
The three historical primary failures retain their queued retries; DeepSeek
still depends on both original and replacement Qwen arrays.

All 57 deployed frozen source identities and the unchanged protocol passed
fresh verification; shared storage has 26 TB available. No new source repair
or scheduler change was warranted. The successful 116-test and HPC self-test
results from the preceding audit remain applicable because no code changed.
The tracker was refreshed; full scientific completeness remains pending.

## October 22, 02:58 UTC — live full-run audit

The refreshed snapshot contains **4,260/99,544** study records (+142 since
01:25), with **18 primary completion receipts**. The two cells previously
awaiting receipts have completed. Qwen tasks **17980_21** and **17980_22** are
running; their investigation logs show 74/132 and 68/132 completed conditions.
The latest eight primary stderr files are empty and no new failed step appears.
All five model gates and complete retrieval remain valid. Historical failed
primary tasks retain their queued retries, and DeepSeek correctly waits for
both Qwen arrays. Recovery is not complete until retry receipts are present.

Fresh verification passed for all **57 frozen source identities**, recorded
maintenance replacements and the unchanged protocol. Shared storage has 26 TB
available. No runtime repair or scheduler change was warranted. No code changed,
so the preceding successful 116-test and HPC self-test results remain applicable.
The live tracker was refreshed; full scientific completeness remains pending.

## October 23, 05:37 UTC — full-run health audit

The refreshed snapshot reports **6,608/99,544** study records and **36 primary
completion receipts**. Qwen tasks **17980_39** and **17980_40** are running;
their investigation logs show 65/132 and 51/132 completed conditions. The latest
eight primary stderr files are empty and no new failed step appears. The three
historical primary failures still await task 17980_1 and replacement array 18012;
DeepSeek 17981 correctly depends on both arrays. All five inference gates and
complete retrieval remain valid; recovery and full-study completion still
require their respective receipts.

Fresh verification passed for all **57 frozen source identities**, recorded
maintenance replacements and the unchanged protocol. Shared storage has 26 TB
available. The half-hour tracker cron remains installed and its service active.
No compute-source repair or scheduler change was warranted. Added a dated
operational note to the static evaluation report, preserving its original
snapshot counts and explicitly distinguishing its recorded hash from mutable
live metadata. No manuscript or scientific outcome claims were changed.

## October 23, 13:32 UTC — full-run health audit

The refreshed tracker reports **7,282/99,544** study records and **41 primary
completion receipts**. Qwen tasks **17980_44** and **17980_45** are running;
the latest eight primary stderr files are empty. All five model inference gates
passed and retrieval remains receipt-verified at **1,414/1,414**. No new failed
step was found. The three historical AST-query failures still await queued task
17980_1 and replacement array 18012 (tasks 0 and 2). DeepSeek 17981 retains its
dependencies on both Qwen arrays; later stages remain queued. Successful retry
receipts are required before recovery can be called complete.

Fresh streaming SHA-256 verification passed for all **57 deployed frozen source
identities**, recorded maintenance replacements and the unchanged protocol.
The login host's older system Python lacks `hashlib.file_digest`; the read-only
audit therefore used a streaming SHA-256 implementation, without modifying the
Python 3.11 compute runtime or deployed scientific sources. All **116 local
unit/integration tests** passed in `/tmp/morph-review-venv`, and the HPC self-test
passed shell syntax, compilation, full/smoke graph validation and submission dry
runs. UFV shared storage has 25 TB available. The half-hour tracker cron remains
installed and its service is active. Slurm accounting is still disabled; failure
checks use available step ledgers, receipts and logs. No new compute-source or
scheduler repair was warranted. Full scientific completeness remains pending.

## October 23, 17:04 UTC — full-run health audit

The refreshed tracker reports **7,589/99,544** study records and **44 primary
completion receipts**. Active Qwen tasks **17980_47** and **17980_48** are
writing completed cases (30/132 and 9/132 respectively at log inspection).
The latest eight primary stderr files are empty. No new failed step was found;
all five model gates and receipt-verified retrieval remain valid.

The three historical AST-query failures retain their queued recoveries:
17980_1 and replacement array 18012 (tasks 0 and 2). Scheduler inspection
confirms 18012 waits for 17980, and DeepSeek 17981 waits for both arrays.
Successful recovery receipts remain necessary before marking these failures
resolved. Later stages and collection remain queued through the existing graph.

Fresh streaming SHA-256 verification passed for all **57 frozen deployed source
identities**, recorded runtime replacements and the unchanged protocol. All
**116 local unit/integration tests** passed, as did the HPC self-test (shell
syntax, Python compilation, full/smoke graph checks and submission dry runs).
Shared UFV storage has 25 TB available; the half-hour tracker cron is installed
and its service is active. Slurm accounting remains disabled, so the audit uses
step ledgers, receipts and available logs. No new source or scheduler repair was
warranted. The evaluation report retains its separate frozen scored snapshot;
this operational refresh does not change its measured comparisons. Full-study
scientific completeness remains pending.

## October 23, 20:08 UTC — full-run audit and verifier compatibility fix

The refreshed tracker reports **7,862/99,544** study progress records. Qwen
cells **17980_49** and **17980_50** are running and writing completed cases;
their inspected logs reached 33/132 and 15/132 conditions respectively.
The latest eight primary stderr files are empty. No new failed step was found.
Historical AST-query failures still require successful receipts from queued
17980_1 and replacement array 18012; subsequent model stages remain dependent
on those arrays. Full scientific completeness remains pending.

Read-only streaming verification passed for all **57 frozen source identities**,
all six recorded maintenance replacements, and the unchanged protocol. Shared
storage has 25 TB available. The live tracker was refreshed; the evaluation
report continues to use its separate frozen scored snapshot.

Fixed the local runtime-maintenance digest helper to stream SHA-256 in bounded
chunks instead of requiring Python 3.11's `hashlib.file_digest`. This makes the
helper usable by the older login-host Python documented in the preceding audit.
A regression test covers multi-chunk and empty files with `file_digest`
unavailable. All **117 unit/integration tests** passed with `PYTHONPATH=src`
in `/tmp/morph-review-venv`; the HPC self-test passed. This compatibility fix
has **not** been copied into the frozen active deployment; no scientific source,
protocol or scheduler changes were needed for the running experiment.

## October 24, 03:31 UTC — full-run health audit

The refreshed tracker reports **8,503/99,544** study progress records. Qwen
jobs **17980_53** and **17980_54** are running; their inspected investigation
logs reached 90/132 and 72/132 completed conditions. All five model preflights
and receipt-verified retrieval remain valid. The latest eight primary stderr
files are empty, and the step ledger contains no new failures.

A tokenizer length warning in task 17980_54 reported a 44,867-token candidate
prompt. Inspection of the adapter confirms it counts candidate prompts before
iteratively trimming supplied context; the inference backend separately checks
the common context allowance before generation. The affected RGFL condition
subsequently emitted `case_done` and execution advanced to the next case. This
warning therefore did not establish an oversized model generation or a failed
case, and no protocol-changing truncation repair was applied.

Historical AST failures still await task 17980_1 and replacement array 18012.
Direct scheduler inspection confirms 18012 waits for 17980 and DeepSeek 17981
waits for both arrays. Successful recovery receipts remain required. Later
stages remain queued in the existing dependency graph; full scientific
completeness is pending.

Read-only streaming verification passed for all **57 frozen source identities**,
all six recorded maintenance files, and the unchanged protocol. All **117 local
unit/integration tests** and the HPC self-test passed. Shared storage has 25 TB
available. Slurm accounting remains disabled, so failure checks use the step
ledger, receipts and logs. No new source or scheduler repair was warranted.
The tracker was refreshed; the evaluation report retains its frozen snapshot.

## October 24, 18:01 UTC — live experiment health audit

Manual tracker refresh reports **9,755/99,544** study progress records.
Qwen tasks **17980_63** and **17980_64** are running; their investigation
logs reached **61/132** and **32/132** completed conditions at inspection.
The inspected recent primary stderr files are empty. The step ledger contains
only the five previously recorded failed attempts; no new failure was found.
All five preflight gates and receipt-verified retrieval remain complete.

Historical primary failures still await queued task **17980_1** and replacement
array **18012** (tasks 0 and 2). Direct scheduler inspection confirms 18012
waits for 17980, and DeepSeek 17981 waits for both arrays. Later stages and
collection remain queued. Successful recovery receipts are still required;
full scientific completeness has not been established.

Shared UFV storage has **25 TB available**, and the half-hour tracker cron
remains installed. The living tracker and local status snapshot were refreshed.
No new runtime or scheduler issue requiring a repair was identified, so no
active experiment code, scientific settings, or scheduler dependencies changed.

## October 24, 18:16 UTC — prioritize a smaller exploratory pilot

Following user approval, pending extended-study jobs were placed on reversible
scheduler holds. Tasks 17980_63 and 17980_64 continue normally; no completed
outputs were removed. The exact 59 held job/task identities, queue snapshot,
and submission commands are preserved in
`/home/babaei/morph-ufv/pilots/pilot-20261024/schedule.json` and adjacent records.

The separate pilot freezes 50 repository-balanced, hash-selected issues,
excluding previously inspected IDs before outcomes are opened. It runs Qwen
and DeepSeek with seed 1, four primary workflows, and the unchanged 32k budget
and 16 rounds. It reuses 132 validated primary records plus 100 retrieval
records; 268 primary predictions remain. Qwen array **18105** waits for the two
running full-study tasks, DeepSeek array **18106** follows Qwen, and CPU report
job **18107** checks exact pilot coverage. New code only orchestrates subsets
around the verified frozen deployment; its inference/scientific sources are
unchanged. Pilot receipts never certify full-study shard completion.

A read-only scheduled snapshot analyzed 472 complete Qwen four-workflow issue
sets (seed 1). File Top1: MORPH 42.8%, no-forgetting 43.2%, fixed-reset 42.2%,
stateless-summary 52.5%. These completion-selected, exploratory comparisons
include any previously inspected cases and do not establish generalization.
They currently show no MORPH advantage. The compact paired report and scores
are stored locally under `experiments/pilot/results/existing-analysis/`.

The dedicated local half-hour pilot tracker collects small reports/status;
the existing full tracker remains installed and links to the pilot page.
See [pilot progress](pilot_progress.md) and
[pilot implementation](../../experiments/pilot/README.md). Verification:
117 existing unit/integration tests passed; three new tests cover deterministic
selection, preservation of original shard/settings, and paired denominators.
All 14 pilot/tracker tests passed after the reporting change; shell syntax,
Python compilation and whitespace checks passed.

## October 24, 20:22 UTC — pilot inference active; interim comparison collected

Both original full-study tasks finished, and pilot Qwen array **18105** is
now running tasks **22** and **24** on node2. Both loaded the pinned checkpoint,
completed their first MORPH conditions, and advanced to no-forgetting. Pilot
progress is **134/400** records. No traceback or new execution failure was
found; checkpoint loading messages and a dtype deprecation warning are benign.
DeepSeek **18106** and final reporting **18107** retain their dependencies.
The extended study remains held.

Scheduled CPU snapshot **18110** completed successfully. Its read-only report
validates completed records against frozen provenance and skips incomplete live
JSONL tails. Across **33 complete Qwen pilot issues**, file Top1 is 42.4% for
MORPH, no-forgetting and fixed-reset, and 48.5% for stateless-summary. The
partial sample currently shows no MORPH advantage; remaining cases and DeepSeek
are pending. See [interim pilot report](../../experiments/pilot/results/interim-analysis/report.md).
This snapshot is separate from final coverage validation and does not change
inference settings or the frozen subject selection. The half-hour tracker now
collects interim reports as well. All **121 unit/integration tests** passed,
including live-tail handling, and shell/whitespace checks passed.

## October 24, 20:56 UTC — pilot progress and refreshed partial results

The pilot advanced from 134 to **173/400** primary records. Qwen tasks
18105_22, _24, _25 and _26 have successful subset receipts (eight records
each). Tasks _27 and _29 are running; _31 remains queued. Inspected Qwen
stderr logs contain checkpoint loading/deprecation messages and no traceback.
DeepSeek 18106 still waits for Qwen, followed by final reporting 18107.
The extended-study scheduler holds remain in place.

Scheduled CPU snapshot **18115** completed successfully with 173 observed
primary records. On **42 complete Qwen pilot issues**, file Top1 is 40.5%
for MORPH, no-forgetting and fixed-reset, versus 47.6% for stateless-summary.
The descriptive repository bootstrap interval for MORPH minus summary is
[-17.1, +2.3] percentage points. This incomplete exploratory sample does not
establish an advantage for MORPH. The interim report and live pilot page were
refreshed; the installed half-hour monitor also refreshed successfully at
20:30 UTC. No inference, protocol or scheduler repair was needed.
