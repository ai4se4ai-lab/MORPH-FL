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
