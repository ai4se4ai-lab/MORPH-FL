# Five-family protocol revision — 2026-10-20

**Current review status:** the original full run ended with zero study records.
The corrected v5 preflights are now running in a separate deployment; Qwen job
17908 started real inference with the 32,000-token budget. Jobs 17909–17912 wait
in sequence. No new gate pass or full-study result is claimed. See the final
section for deployment and monitoring details.

User request: replace three Qwen checkpoints with five models from five distinct
families, prioritizing established software-engineering and fault-localization use.

The original run am-20261019-191308 is superseded. Its model jobs were cancelled;
only identical pinned benchmark preparation job 17836 continues for reuse. The
original deployment, downloaded models, smoke outputs, protocol and logs remain
archived. No full primary inference result had been used to choose the new models.

New run: ufv-fivefam-20261020-01, 34 submissions, 733 cells; collect job 17901.
New isolated deployment: /home/babaei/projects/MORPH-FL-ufv-fivefam-20261020.
The local protocol, pins, model matrices, native-context guard, GPU allocation and
result-export completeness guard now cover the five selected model families.

See experiments/full/models.md for primary-source evidence, licenses and explicit
limits of exact-checkpoint versus family-level fault-localization evidence.
Granite 3.1 replaces the initially considered Granite 3.0 because the latter's
4,096 native context tokens cannot support the common 16,384-token study limit.

The previous smoke remains runtime evidence. All five models have mandatory real
inference gates in the new graph; new-family success is not presumed.

The tokenizer-only check found the Transformers Mistral regex warning.
`fix_mistral_regex=True` is now pinned for Mistral before any new-family inference.
The pre-correction manifest/protocol are preserved, and the final protocol/model
selection are copied into the run config and result tree.

## Local experiment review — 2026-10-20

The latest local collector snapshot, checked at **04:10:12 UTC on October 20**,
reports `done=true` but **scientific completeness is false: 0/99,544 planned
study records are present**. The run ended without a full evaluation. This
supersedes the earlier 03:54 saved observation that showed pending work.

Archived step logs show Qwen passed all six preflight workflows. DeepSeek,
CodeLlama, Mistral and Granite completed their workflow calls but failed the
explicit check for a valid MORPH-FL hypothesis. DeepSeek's archived prediction
shows 4,168 input tokens, 438 output tokens, an invalid JSON response, and then
a budget stop under the 6,000-token smoke ceiling. This establishes a formatting
failure for that attempt; it does not establish the same cause for all models.
The available prediction archive contains only the first two models because
collection ran before the later preflights finished. Their terminal step logs
are available, but their full prediction diagnostics need recollection.

The collection analysis correctly reported all records missing, but its stage
then failed because `analysis/summary.csv` did not exist for zero records. This
is fixed locally: analysis writes a header-only summary and preserves PARTIAL
status. A regression verifies it also clears a previously populated summary.

Fresh SSH authentication failed during the prior review. Remote repairs,
recollection and genuine GPU reruns remain unverified. The local fixes do not
resolve the four model inference-gate failures; those require inspecting full
responses and validating any shared prompt/protocol revision in a new run.
The gates must remain enabled. No model output or success claim was fabricated.

### What is being evaluated

The question is whether MORPH-FL's evidence-preserving hypothesis search and
context resets improve localization under a shared token budget. The main
comparison includes continuous context (`no_forgetting`), fixed resets,
stateless summaries, and restricted Agentless/RGFL adaptations. The latter do
not implement those projects' complete upstream pipelines.

The five pinned models are Qwen2.5-Coder 7B, DeepSeek-Coder 6.7B, CodeLlama 7B,
Mistral NeMo 12B, and Granite 3.1 8B. All use native Transformers BF16 inference,
a 16,384-token context limit, temperature 0.2, top-p 0.95, top-k 50 and an output
ceiling of 1,536 tokens per call. Primary investigations have a cumulative
32,000 input-plus-output-token ceiling and at most 16 rounds. A cumulative
investigation budget can exceed the context limit because it spans multiple calls.

The prepared benchmark union is reported as 707 issues: 300 Lite plus 500
Verified minus 93 shared IDs. Shared issues execute once per condition and
contribute to both benchmark summaries. The two summaries are therefore
correlated, rather than independent replications.

| Track | Subjects | Conditions per model/seed | Planned records |
|---|---:|---:|---:|
| Primary | 707 | 6 workflows | 63,630 |
| Component ablations | 100 | 8 controls | 12,000 |
| Additional budgets | 100 | 4 workflows × 16k/48k | 12,000 |
| Misdirection | 100 | 4 workflows | 6,000 |
| Reset policy | 100 | windows 3/4/5, 15% gate | 4,500 |
| Deterministic retrieval | 707 | BM25 and graph, once each | 1,414 |
| **Total** | | | **99,544** |

LLM tracks use five models and three seeds. Preflight records are separate.
The 32k budget-curve point reuses primary records on the same 100 side subjects.
The side sample is selected using repository round-robin and public-ID hashes,
without consulting labels or model outputs. There are 34 scheduler submissions
covering 733 cells; cells contain multiple issue/condition records.

### Execution and interpretation

UFV reserves one A30 for Qwen/DeepSeek/Granite and two for CodeLlama/Mistral.
The code requires all model parameters to reside on GPU. Model groups execute
serially; small-model arrays allow two concurrent cells. Each model has a real
six-workflow preflight stage before the main stage dependencies can succeed.
The preflight's explicit validity check requires generated tokens and a valid
MORPH hypothesis; it does not guarantee useful rankings for every workflow.

Inputs are public issue reports and archived pre-fix Python files. Patches supply
separate evaluator-only localization labels. Outputs measure file Top-1/5/10,
MRR, function localization, tokens, timing and search/reset behavior. Paired
comparisons average seeds within cases and account for repository clusters;
the primary File Top-1 comparison family uses Holm adjustment. Misdirection
recovery requires both a proxy-wrong clue and evidence that the first valid
leader actually followed it.

These remain static, unreviewed patch-proxy measurements. They cannot establish
human-adjudicated root causes, executable reproduction/probe validity, calibrated
confidence, or superiority to complete upstream Agentless/RGFL systems. Prior
pilot subjects may be included, so this is not an untouched holdout. Scheduler
completion is distinct from scientific completeness and favorable outcomes.

### Issues fixed locally

1. **Empty prediction cells crashed scoring.** A cell interrupted before its
   first completed case could leave an empty JSONL; the generic scorer rejected the empty input and stopped analysis.
   Scoring now skips the empty cell and removes its cached score CSV. Partial
   analysis still reports the missing planned records.
2. **Unrelated cached scores could contaminate analysis.** Analysis previously
   loaded every CSV in `scores`, including files whose prediction inputs had
   been removed. It now reads only scores associated with current non-preflight
   prediction files. Regression coverage includes empty and orphaned scores.
3. **Dataset reuse trusted manifest counts.** The reuse script now checks actual
   benchmark membership sizes and uniqueness, union/overlap counts, exact
   case/label coverage, matching source/label revisions and archive existence
   before creating its link. Archive SHA-256 verification remains in the runner.
4. **Paper export could accept duplicated workflows.** The guard now verifies
   every exact model/workflow pair, the 32k primary budget, and three records per
   benchmark case in addition to the existing seed/subject checks. Regression
   tests reject missing workflows disguised by duplicates, incomplete record
   counts, and incorrect budgets. Full-directory scoring also removes orphaned
   CSVs so downstream collection cannot consume those obsolete tables.
5. **Resume could trust mismatched completed records.** The full runner now
   checks each record against the current case report digest, source archive
   digest, repository/revision, model identity/revision, seed and run signature.
   It also rejects duplicate records, unplanned conditions and records outside
   the selected shard before skipping completed work or writing resume settings.
   Regression tests exercise valid resume and each rejection class.

The local protocol is now `morph-full-five-families-v5`, with updated hashes for
the scoring/analysis changes. Model selection, budgets, sampling and workflows
are unchanged. The prior tracked protocol is recoverable at base commit
`7710a0b097e04092773464592f3b7e26d3b1d77b`. This revision has **not** been deployed
to the running UFV tree. Changing a frozen protocol on a resumable run changes
its signature; use a separate deployment/run for the revised protocol or analyze
a preserved result copy with the corrected analysis code.

### Verification

- 88 unit tests passed, including new reuse and partial-analysis regressions.
- Two integration tests passed, covering collection and lossless storage.
- `hpc/scripts/selftest.sh` passed full/smoke graph and shell/static checks.
- Ruff passed on changed Python files; the protocol source-hash check passed.
- Tests ran in an isolated `/tmp` environment with libcst 1.8.6, matching the
  recorded UFV runtime. NumPy 2.3.5 was used because the newer wheel required CPU
  instructions unavailable on this local host.

GPU inference and full scientific outcomes were not rerun locally. The archived
UFV validation reports 15 tests and all five tokenizer/context checks passing;
that evidence does not substitute for completed per-model inference gates.

### Follow-up: collection ordering and failed-output diagnostics

Two additional issues were fixed after inspecting the archived preflight logs:

- Collection depended on downstream study jobs, which could become terminal
  through dependency failure before all preflights had finished. The collection
  stage now explicitly waits `afterany` for `model_preflight`. UFV model splitting
  expands this into dependencies on all five per-model gates. Regression checks
  verify every dependency. The existing gates remain strict.
- Native structured parsing discarded malformed generated text. The backend now
  carries that text in a typed parsing failure, and the controller stores it as
  a hashed evidence artifact with the failure's role and step. Invalid structured
  responses also retain their raw text. Failed calls still consume their actual
  tokens; parsing and model behavior are unchanged. A regression verifies the
  stored bytes, digest, and token accounting.

These corrections make the next run diagnosable and prevent premature final
collection. They do not establish that four failed models can satisfy the current
schema or budget. Their genuine inference gates must pass before a full run can
be considered ready. The local v4 protocol refreshes changed source hashes;
no remote deployment, GPU rerun, or successful inference is claimed.

### Recovered preflight evidence

The existing SSH ControlMaster connection subsequently provided read-only access.
All five models' predictions were recovered separately in
`hpc/logs/ufv-fivefam-20261020/late-preflight-predictions.tar.gz`, preserving the
original early collection archive. No GPU work or remote source edit was performed.

| Model | Input tokens | Output tokens | Valid MORPH hypotheses | First-call finding |
|---|---:|---:|---:|---|
| Qwen | 3,558 | 1,095 | 4 | Valid hypotheses |
| DeepSeek | 4,168 | 438 | 0 | No parseable JSON object |
| CodeLlama | 4,199 | 667 | 0 | No parseable JSON object |
| Mistral | 3,667 | 1,073 | 0 | Echoed report object; hypothesis list absent |
| Granite | 3,898 | 1,536 | 0 | Echoed report object; hypothesis list absent |

Every MORPH preflight stopped at the context/cumulative-budget check before its
second generation. Granite reached the per-call output ceiling; that alone does
not establish the cause of its echo. Invalid raw generations for DeepSeek and
CodeLlama were discarded by the old backend and cannot be recovered from these
prediction records.

The controller previously used an empty default for a missing `hypotheses` key.
It now requires that key to contain a list and records missing-list report echoes
as invalid responses, with their raw artifact. An explicit empty list remains
permitted. Regression coverage verifies the distinction. This corrects validity
accounting but does not make the failed models produce usable hypotheses. Any
prompt or budget revision still requires a fresh, common protocol and real GPU
validation, retaining these failed attempts as evidence.

### Follow-up: preflight budget mismatch

The real-inference preflight inherited the ordinary smoke's 6,000-token ceiling,
although its purpose is to gate a 32,000-token study. The recovered records show
all five MORPH attempts stopped before a second generation, leaving no chance
to obtain a valid response after the first invalid/irrelevant output.

The v5 local protocol separates the two envelopes: per-model preflight uses the
primary 32,000-token cumulative ceiling, still on one issue, with two rounds and
six workflows; ordinary smoke tracks retain their 6,000-token limits. Primary
budgets, model prompts, sampling, case selection and study record counts are
unchanged. The gate still requires actual generated tokens and valid MORPH
hypotheses. No constrained decoding, heuristic hypothesis fabrication or
model-specific retry is introduced.

Preflight mode is included in resume settings, and prior 6k records are rejected
under the new 32k conditions. Gate receipts now record budget and protocol hash.
A regression verifies the separate budgets and rejection of old-budget resume
records. The revised gate has not been GPU-validated or deployed remotely; a
larger preflight envelope alone does not guarantee schema compliance or success.

### Isolated GPU validation of the corrections

The v5 source snapshot was deployed separately to
`/home/babaei/projects/MORPH-FL-review-v5-20261020`. Its frozen source hashes were
verified on the remote host before submission. Results go to
`/home/babaei/morph-ufv/runs/ufv-review-v5-20261020-01/results`.
The original five-family deployment and failed run were not edited.

The data-reuse validator passed against the existing complete prepared inputs.
Each reused checkpoint's model ID and revision were checked against the new
deployment's pins. Only weight directories are linked; preflight predictions,
receipts and evidence are written into the new result tree.

| Model | GPU preflight job | A30 GPUs |
|---|---:|---:|
| Qwen | 17908 | 1 |
| DeepSeek | 17909 | 1 |
| CodeLlama | 17910 | 2 |
| Mistral | 17911 | 2 |
| Granite | 17912 | 1 |

Jobs execute serially via `afterany` dependencies, so a failed model does not
prevent diagnostics for the next one. Each has a one-hour wall-time ceiling.
Only these five preflights were submitted; no automatic full-study continuation
was installed. The job entry point is `hpc/ufv/review_preflight.sh`, which requires
a Slurm allocation and uses the existing container/runtime dependencies.

At the saved 05:12:51 UTC check on October 20, Qwen was running and the other
four jobs were pending. Its live log confirms a genuine MORPH call with budget
32,000. All five receipts were still absent at that observation, so neither
inference-gate success nor completion is inferred from job startup.

A detached local monitor checks once per minute and retrieves terminal logs,
prediction records, progress files and gate receipts. Its PID, script, output
and status are under `hpc/logs/ufv-review-v5-20261020/`; do not start a duplicate.
Large evidence/graph archives remain in the isolated remote result tree.
This monitor reports **preflight status only**, never full-study completeness.

Local validation remains 88 unit tests and two integration tests passing, with
lint, source-hash and shell-syntax checks passing. Successful GPU gates remain
the outstanding condition before another full experiment can be considered ready.
