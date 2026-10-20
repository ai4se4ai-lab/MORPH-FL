# Active UFV five-family study

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
python3 -u hpc/ufv/watch_collect.py
# For another run, use --deployment PATH --run-id ID --destination LOCAL_PATH.
```

The existing detached collector PID is in
`hpc/logs/ufv-fivefam-20261020/monitor.pid`; do not launch a duplicate.
It polls once/minute, saves `status.json`, and transfers terminal logs, tables,
figures, predictions and metadata with an SSH tar stream. Remote rsync is absent.
Graphs/evidence archives remain remote; their paths and sizes are inventoried.
A scheduler-terminal run may still be scientifically incomplete: consult
`scientific_completeness`, not only `done`. Collection job 17901 always analyzes
coverage; no success or favorable-outcome claim follows from job submission.

Paper export/typesetting remains disabled on UFV because docs/TSE is absent from
this checkout. The exporter itself now validates all five pinned model identities.

Mistral NeMo uses the pinned Transformers tokenizer option
`fix_mistral_regex=True`. The pre-correction protocol and manifest are preserved
in the run log; the final selection/protocol are copied to both config and results.
