# Active UFV five-family study

The [living phase tracker](../../docs/UFV/study_progress.md) updates every 30 minutes (with a persistent refresh change log and failure diagnostics)
from the active monitor's read-only metadata snapshot. Its table covers each
experiment, rationale, receipt-backed status, result overview and output paths.
Edit `hpc/ufv/study_tracker.py` to change the generated plan; manual edits to the
generated Markdown are overwritten. The snapshot is saved as
`hpc/logs/ufv-full-v12-20261020/study-progress.json`. No active compute code or
scientific settings are changed by this reporting feature.

**Active corrected run:** `ufv-full-v12-20261020-01`, deployment
`/home/babaei/projects/MORPH-FL-full-v12-20261020`, collection job **18007** (replaces 17962).
All five in-run GPU gates passed. Retrieval recovery **17979** completed with
**1,414/1,414 verified records** after depth-safe AST traversal and streaming
resume fixes. The compact prediction file is about 41 MiB; full graphs remain
on UFV. The continuation submitted all 26 remaining stages at 19:17 UTC on
October 20. Primary arrays are **17980–17984**, with two Qwen tasks running in
17980; final collection is **18007**. Existing side-study records are retained
for resume. The temporary recovery cron removed itself; half-hour reporting
continues. See [repair evidence](../../docs/UFV/runtime_recovery_20261020.md)
and the [living tracker](../../docs/UFV/study_progress.md) for current results.

The identifiers below describe the preserved, failed original run.

Run: `ufv-fivefam-20261020-01`
Host: `babaei@slurm.soc.ufv.ca`
Deployment: `/home/babaei/projects/MORPH-FL-ufv-fivefam-20261020`
Work: `/home/babaei/morph-ufv`
Full result collection job: **17901**
Runtime/unit/tokenizer validation job: **17907** (final tokenizer correction check; 17905 passed the unit tests)

The 34 submissions cover 733 cells. The exact five-family checkpoint commits,
selection evidence, licenses, and checkpoint-versus-family caveats are documented
in [models.md](../../experiments/full/models.md) and
[pins.json](../../experiments/full/pins.json). The models are Qwen2.5-Coder 7B,
DeepSeek-Coder 6.7B, CodeLlama 7B, Mistral NeMo 12B, and Granite 3.1 8B.

Benchmarks remain complete SWE-bench Lite (300) and Verified (500), with 707
unique issues. Seeds 1/2/3, six main workflows, BF16, context 16,384, sampling,
32k primary budgets, side studies, and all coverage checks are retained. The 707-case union implies 99,544 planned study records, excluding separate
preflight records. Every
model must pass a real six-workflow inference preflight before primary inference.
A model whose native context is too short now fails explicitly.

The superseded run `am-20261019-191308` remains in the original
`MORPH-FL-ufv-20261020` deployment. Its model jobs were cancelled on the user's
model-diversity request. Dataset preparation **17836** continues unchanged;
new data job **17867** depends on its successful completion and verifies dataset
pins and full 300/500 membership before linking the prepared inputs. Old pinned
weights are reused only when both checkpoint name and revision match. The
existing Ollama job 17664 is preserved. Old run artifacts are not deleted.

Runtime preparation stays in GPU jobs: the cached PyTorch 2.6/CUDA 12.4 SIF,
additional Python dependency tar, and Git toolchain tar live in
`/home/babaei/morph-ufv/runtime`. Each experiment extracts dependencies into its
own node-local /tmp. No model execution, environment building, or data preparation
runs on the login host. Submissions must run on the login host: compute nodes'
Slurm client configuration is not readable by this account.

CodeLlama and Mistral reserve two A30s and 64G RAM per task; Qwen, DeepSeek and
Granite reserve one A30 and 40G. Small-model arrays permit two concurrent cells;
model groups execute serially. All parameters must remain on GPU. No CPU offload
or quantization is substituted. Large evidence/graph archives remain on shared
UFV storage, because the local volume had only 31GB free at deployment.

The prior 25-record end-to-end smoke is complete and archived locally under
`hpc/logs/ufv-20261020/ufv-smoke-20261020-01`. It validates the pipeline/runtime;
it does not establish successful inference for newly added checkpoints. The new
per-model gates provide that evidence. No smoke result is promoted to a full result.

Monitoring and collection:

```bash
python3 -u hpc/ufv/watch_collect.py \
  --deployment /home/babaei/projects/MORPH-FL-full-v12-20261020 \
  --run-id ufv-full-v12-20261020-01 \
  --destination hpc/logs/ufv-full-v12-20261020
```

The active monitor is the half-hour cron described below; use
`bash hpc/ufv/cron_tracker.sh` for a single manual refresh with the same lock.
The continuous command above is an alternative and must not run alongside cron.
Cron publishes the study document every 30 minutes (and on final collection), saves `status.json`, and transfers terminal logs, tables,
figures, predictions and metadata with an SSH tar stream. Remote rsync is absent.
Graphs/evidence archives remain remote; their paths and sizes are inventoried.
A scheduler-terminal run may still be scientifically incomplete: consult
`scientific_completeness`, not only `done`. Active collection job 18007 analyzes
coverage; no success or favorable-outcome claim follows from job submission.

Paper export/typesetting remains disabled on UFV because docs/TSE is absent from
this checkout. The exporter itself now validates all five pinned model identities.

Mistral NeMo uses the pinned Transformers tokenizer option
`fix_mistral_regex=True`. The pre-correction protocol and manifest are preserved
in the run log; the final selection/protocol are copied to both config and results.

The tracker stores persistent refresh history and failure incidents in
`hpc/logs/ufv-full-v12-20261020/tracker-history.json`. Each publication adds a
row to the document’s final change-log table, including publications with no
progress. Failures are observed on each poll and appear in the document at its
next refresh, with attempt identity, commands, exit codes and log evidence.
The monitor must remain running and SSH access must remain available; failed
connections retain the last successful remote snapshot and are logged as incidents.

Active monitoring now uses the `majid` crontab on comp370, at minutes 00 and 30.
The continuous monitor has been stopped. See [installed cron setup](../../docs/UFV/comp370_tracker_cron.md)
for paths, authentication, operation, and limitations.
