# Fast exploratory pilot

The October 24 pilot retains the active UFV deployment's frozen v12 inference
code, pinned BF16 Qwen/DeepSeek checkpoints, 32k token budget, 16 rounds and
seed 1. It selects 50 issues by deterministic repository-balanced hash order,
excluding `previously_inspected` IDs, before opening predictions or labels.
Four workflows produce 400 planned primary records: MORPH, no-forgetting,
fixed-reset and stateless-summary. Retrieval outputs are reused separately.
The extended study's pending jobs are held; running tasks finish normally.

See [live progress](../../docs/UFV/pilot_progress.md),
[initial paired report](results/existing-analysis/report.md), and
[frozen subject selection](results/pilot.json).
The initial report uses completed four-workflow Qwen issue sets from the full
run, including any previously inspected cases. Completion order can bias this
snapshot. The 50-issue pilot is exploratory too; neither report is an untouched
confirmation set. Labels are unreviewed patch-change proxies.

`manage.py prepare` runs inside a scheduled CPU allocation using the frozen
deployment's Python environment. It validates full-run signatures and source
identities, streams a bounded snapshot of prediction files, saves input byte
limits/digests, and imports matching predictions into separate pilot files.
Signatures are retained; artifact references point back to preserved originals.
The original case order and 32-shard assignment remain intact. `manage.py run`
only filters cases/workflows around the frozen runner, so new predictions can
later be explicitly validated and imported into the extended study. A pilot
receipt certifies its subset only, never completion of a full-study cell.

`hpc/ufv/pilot_schedule.py` records reversible scheduler holds and submissions.
Qwen runs before DeepSeek, at most two tasks at once; final CPU report collection
checks exact coverage and exits unsuccessfully if records are missing. The
local `hpc/ufv/pilot_tracker.py` refreshes metadata and small reports every
30 minutes, independently of an interactive session. Large prediction/evidence
files remain on UFV. No model generation or preparation runs on its login node.

`snapshot.py` creates an interim report inside a scheduled CPU allocation.
It bounds each read to the file's initial byte size, skips an unfinished final
record, validates completed prediction provenance using the frozen runner, and
reports exact observed/missing pilot keys. Its `interim-analysis` output stays
separate from final analysis and is collected by the tracker. It represents
the snapshot time, rather than a continuously recomputed accuracy estimate.

Reports compare workflows on the same completed eligible issues, include
file/function accuracy, completed-case costs, reset counts and descriptive
repository-cluster bootstrap intervals. These intervals are exploratory and
unadjusted for multiple comparisons. Interrupted-attempt costs are excluded.
If pilot outcomes motivate method changes, retain untouched cases for later
confirmation rather than treating a favorable rerun as independent evidence.
