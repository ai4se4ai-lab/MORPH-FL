# Full Lite + Verified evaluation (prospective)

**Status:** five-family revision prepared after the original end-to-end smoke passed. New checkpoints require per-model GPU preflights; no full-run results are claimed. The user selected complete SWE-bench Lite (300) and Verified (500) first. Other ecosystems remain a subsequent implementation effort. Original exploratory measurements and the paper remain available unchanged.

## Frozen design

- Five pinned instruction checkpoints from distinct families: Qwen2.5-Coder 7B, DeepSeek-Coder 6.7B, CodeLlama 7B, Mistral NeMo 12B, IBM Granite 3.1 8B. [Study-backed selection](models.md); exact HF revisions in [pins.json](pins.json).
- BF16 Transformers on full H100 80 GB, common native context limit 16,384, temperature 0.2, top-p 0.95, top-k 50, max output 1,536, seeds 1/2/3. Smoke uses a20GB MIG allocation for the7B checkpoint; full model cells use80GB H100s. These are new conditions, not renamed Ollama quantizations. GPU-residency check forbids silent CPU offload. No JSON-constrained decoder is claimed.
- Primary: all unique issues from the two pinned test splits, six workflows, 32,000 input+output tokens, up to 16 rounds. Workflows: MORPH-FL, continuous context, fixed reset, stateless summary, restricted Agentless and RGFL component adaptations. The external tree cap is 12,000 from the outset, not selected after seeing these results; complete upstream embedding/repair pipelines remain absent.
- Deterministic BM25/graph controls run once per unique issue, not once per model/seed.
- Side sample: first 100 unique issues selected by repository round-robin, within-repository SHA-256 order of `morph-full-side-v1:` plus public ID, **without reading labels or outputs**. The same subjects support eight component controls, budget curves at 16k/32k/48k, disclosed misdirection, and reset windows 3/4/5 with the optional 15% gate. The 32k curve point comes from primary runs, not a redundant rerun.
- Misdirection selects BM25 rank 2 without labels, records the clue as unverified, and later checks whether it was proxy-wrong and actually became the first valid-round leader before counting a proxy recovery. All clue outcomes remain reported.
- Duplicate IDs shared by Lite and Verified execute once per condition, provided revision/report/patch consistency checks pass. Each benchmark is summarized separately; overlap is reported and never treated as independent replication.
- Resume signatures freeze model/data/source/protocol. Completed records append+fsync and skip; partial final JSON lines can be repaired. Incomplete coverage is reported as PARTIAL.

The main result is still patch-proxy localization, **not human-adjudicated root cause**. Calibration is unavailable because confidence is null. Dynamic benchmark reproductions and human causal/explanation labels remain missing and cannot be manufactured by a larger static run. RQ coverage distinguishes those gaps explicitly.

## Scale and resource envelope

At most 800 distinct inputs: main 72,000 LLM records; side studies 34,500; IR 1,600 = **108,100 records upper bound**. Actual primary count falls with benchmark overlap. There are 10 stage submissions and 733 full task cells: 480 main; 60 each for ablations, budgets, misdirection and policy; five model downloads, five per-model preflights, data, retrieval and collection. Heavy study tracks run sequentially, with at most four concurrent full H100s; lightweight MIG work is separate.

Each heavy task requests 12 hours and at most two requeues, resuming completed cases. Initial main/side allocation ceilings total 8,640 full-H100 hours; this is a reservation ceiling, not a measured cost estimate. Two requeues can triple it. A defensible throughput estimate comes from the smoke/per-model preflight, and the user can constrain the prospective design before full submission. Smoke retains all ten stages with one selected model/seed/shard and one issue per study track; every workflow interface is exercised. Per-stage 15-minute limits are ceilings, not a claim of 150 minutes expected runtime.

## Storage and deployment

Packed pre-fix Python snapshots avoid inode amplification. Compute jobs extract one case into node-local temporary storage. Hypothesis graphs are deduplicated by hash, and prompt/evidence directories are packed per completed case with archive digests and original-root mappings. Analysis reads compact outputs without executing the models or benchmark code. Weights/caches/work use scratch; collection copies durable tables/figures/audits and packed raw records to project storage. No downloads, installs or model execution run on the login node.

New deployment: `/project/def-mbabaei/mbabaei/MORPH-FL-full-v5`; previous deployments are preserved. Account: `def-mbabaei_gpu`. The skill template was reused (`scaffold.sh` reported all existing files retained). See [HPC guide](../../hpc/docs/hpc-guide.md).

## Commands

```bash
bash hpc/scripts/selftest.sh
python3 hpc/slurm/submit.py --dry-run --smoke
python3 hpc/slurm/submit.py --smoke
# Only after genuine smoke validation:
python3 hpc/slurm/submit.py
bash hpc/status.sh RUN_ID
```

Do not poll Slurm faster than once per minute. No automatic paper claim changes occur on scheduler exit alone. The final analysis includes completeness, per-benchmark CSVs, paired repository-cluster intervals, reset retention, recovery eligibility, and measured plots. Paper updates must use complete non-smoke results and retain explicit missing-evidence statements.

## Collect and update the paper

```bash
bash hpc/scripts/collect-full.sh /project/def-mbabaei/mbabaei/MORPH-FL-full-v5 RUN_ID
# Only complete, non-smoke outputs can pass this guard:
bash hpc/scripts/collect-full.sh /project/def-mbabaei/mbabaei/MORPH-FL-full-v5 RUN_ID --update-paper
```

The exporter checks full300/500 coverage, five models, six primary workflows and three seeds before adding measured tables/figures and a source-hashed full-results subsection. It rejects incomplete/smoke data. Abstract, discussion and causal claims must then be revised against the actual outcomes and the remaining evidence gaps; a table exporter is not a substitute for that scientific assessment.

The historical v4 smoke `am-smoke-20261019-161100` passed all15 steps. Its compute-node continuation failed before any submission due to site Slurm plugin incompatibility. The replacement five-family graph is submitted from the login node; benchmark execution remains gated on all five model preflights. See `status.json` for current job IDs.

The full benchmark may include the previously inspected pilot subjects listed in `prior_cases.json`; it must not be described as an untouched holdout. Main logical-token means refer to completed attempts. Interrupted/retried work is additionally reflected in the preserved audit/Slurm accounting and must be included in system-level cost interpretation.

## Model-family revision

The original four-model full run `am-20261019-195744` completed setup only. Its eight pending experiment/collection stage jobs were cancelled before inference when the user requested five distinct families. Sources and setup artifacts remain preserved. The five-family deployment is v5; the successful v4 all-stage smoke remains historical runtime evidence, and v5 gates every checkpoint independently before benchmark execution. Primary multiplicity family now contains 50 comparisons. Completed source archives are reused by hard link and verified on a GPU node; they are never relabeled as new measurements.
