UFV deployment for the authorized Lite + Verified full study

Remote: babaei@slurm.soc.ufv.ca
Deployment: /home/babaei/projects/MORPH-FL-ufv-20261020
Work/results: /home/babaei/morph-ufv
Smoke: ufv-smoke-20261020-01 (model assets 17812; repaired stages 17824–17832)
Runtime preparation: 17822 (replaces cancelled dependency attempt 17810); hardware probe: 17809
Validated full-run continuation: 17833 (replaces 17821 after the missing-Git smoke failure)
Git runtime packaging: 17823

The runtime is a Singularity SIF built in a GPU batch allocation, with additional
Python dependencies packed as one tar and extracted into each job's local /tmp.
No model/environment setup or experiment computation runs on the login host.
The existing deployment and Ollama job 17664 remain intact.

The BF16 weights, pinned revisions, sampling, contexts, subjects, workflows,
seeds and budgets are unchanged. GPU hardware differs from the prospective Nibi
H100 design and is recorded in prediction metadata. Small models use one A30;
large models shard across three A30s with a strict GPU-residency check. No CPU
offload or quantization is silently substituted. Full model groups run serially
and preserve all 587 cells across 28 scheduler submissions. Small-model arrays
allow two concurrent tasks. Smoke uses one A30 per task, up to three tasks.
The full preflights must still demonstrate actual large-model feasibility.

Only results collection is configured. Manuscript compilation/export was removed
from this site configuration because this checkout lacks the docs/TSE template.
The scientific completeness and inference gates remain active.

The one-shot continuation refuses full submission unless every smoke step,
actual valid inference, exact output coverage and nonempty collected tables pass.
It records the full run ID and jobs in the smoke's full_continuation.json.
No smoke result is a full-study result.

Local monitoring/collection:

    python3 -u hpc/ufv/watch_collect.py

It checks at most once per minute and copies terminal smoke/full run logs and
collected tables, figures, predictions and metadata into hpc/logs/ufv-20261020/.
Bulky graphs/evidence archives remain in the complete remote result tree, because
the local volume had only 31GB available at deployment. Artifact sizes and the
remote result path are recorded in status.json.
It requires the SSH ControlMaster established by the user. Do not launch duplicate
watchers. A terminal scheduler state does not establish scientific completeness;
inspect results/analysis/completeness.json and failed steps before reporting.
