# Five-family protocol revision — 2026-10-20

**Living phase/experiment tracker:** [study_progress.md](study_progress.md) lists the full plan, reasons, completion evidence, result summaries and result locations, and refreshes automatically with the active monitor. The narrative below preserves historical reviews.

**Current review status:** the active run is `ufv-full-v12-20261020-01`.
All five in-run model gates passed (six records each). Retrieval has reached
**1,287/1,414 unique records (91.0%)** at the October 20, 12:44:40 UTC audit.
No new inference failure signatures were found, and all frozen source hashes
match. Primary and side studies remain waiting on retrieval; no retrieval
completion receipt exists yet. Scientific completeness and benchmark performance
remain pending. The active v12 protocol is unchanged; local v13 resume fixes
and the launcher fallback are for future deployments.

The earlier run IDs and failures below are historical; they do not describe the
active full v12 run.

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

The local protocol is now `morph-full-five-families-v12`, with updated hashes for
the scoring/analysis changes. Model selection, budgets, sampling and workflows
are unchanged. The prior tracked protocol is recoverable at base commit
`7710a0b097e04092773464592f3b7e26d3b1d77b`. This revision has **not** been deployed
to the running UFV tree. Changing a frozen protocol on a resumable run changes
its signature; use a separate deployment/run for the revised protocol or analyze
a preserved result copy with the corrected analysis code.

### Verification

- 90 unit tests passed, including new reuse and partial-analysis regressions.
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

Local validation remains 90 unit tests and two integration tests passing, with
lint, source-hash and shell-syntax checks passing. Successful GPU gates remain
the outstanding condition before another full experiment can be considered ready.

### Follow-up: validate every preflight workflow

The v5 real GPU gate confirms Qwen succeeds: its four structured workflows
produced 5/4/4/7 valid hypotheses respectively, and both adapted external
workflows generated tokens. DeepSeek generated 855 MORPH output tokens over two
attempts but returned prose on both; it stopped at the round limit rather than
the old smoke budget. All four DeepSeek structured workflows lacked hypotheses,
while its Agentless/RGFL adaptations did produce outputs. Budget correction
therefore permits retries but does not establish structured-output compliance.

A further gate weakness was corrected locally in v6. Receipts now require:

- Exactly one record for each of the six primary workflows on one subject.
- The pinned model ID/revision, seed 1, main track and 32,000-token budget.
- Nonzero input/output token counts for every workflow.
- Valid hypotheses for each of MORPH, continuous context, fixed reset and
  stateless summary; external text workflows are not required to emit this schema.

Receipts include per-workflow token/hypothesis counts. Regression coverage rejects
missing/duplicated workflows, an external workflow with no generation, a failed
structured comparator even when MORPH succeeds, and wrong budget/model revision.
The new validator was also applied locally to recovered **real** v5 predictions:
Qwen passes all checks; DeepSeek fails. This does not rerun or relabel those records
under v6. Existing GPU jobs and their frozen source/protocol remain unchanged.

All model-wide prompt/schema changes remain prospective until tested uniformly.
No prose is converted into fabricated hypotheses and no failed model is silently
dropped from the five-family study. The original full experiment still has zero
study records. Full evaluation remains gated on successful model validation.

### Follow-up: malformed outer JSON and later v5 models

The real v5 CodeLlama attempt generated 1,846 tokens across two MORPH calls but
returned prose describing the input/output schema rather than localization JSON;
no valid hypotheses resulted. Mistral generated 1,891 tokens and also produced
no valid MORPH hypotheses. Its raw second response contained an intended
hypothesis list, but used invalid JSON placeholders/comments and list-valued
paths. These are not valid structured outputs and were not repaired into results.

The prior parser tried decoding at every opening brace. On malformed outer
responses it could return a syntactically valid nested `behavior` object,
obscuring the actual malformed-container error. The local v7 parser now scans
complete outer object candidates while respecting strings/escapes, requires a
hypothesis list, and rejects malformed/truncated containers without rescuing
nested fragments. Valid fenced JSON and surrounding prose remain supported.
Regression coverage includes the observed placeholder pattern, truncated outer
responses, nested wrappers, and a valid response following metadata.

Granite's v5 MORPH record contains two valid hypotheses on its second round
(7,588 input / 1,999 output tokens), after an invalid first response. This is
individual-workflow evidence, not yet a claim that its complete six-workflow
gate passed. The corrected budget demonstrably permits a second attempt; it
still does not make DeepSeek/CodeLlama/Mistral schema-compliant.

The v7 parser and v6 all-workflow guard are local revisions. Running v5 jobs,
source hashes, prompts and archived predictions remain unchanged. No additional
GPU jobs or full-study continuation were submitted during this check.

### Final v5 GPU validation status — October 20, 05:45:04 UTC

All five jobs are terminal and all 30 workflow predictions (five models × six
workflows) were collected under
`hpc/logs/ufv-review-v5-20261020/collected`. These are separate preflight records,
not additions to the planned 99,544 study records. Applying the local stricter
all-workflow validator to their original v5 records gives:

| Model | MORPH hypotheses | All-workflow check | Main failure/evidence |
|---|---:|---|---|
| Qwen | 5 | PASS | Four structured workflows valid; external workflows generated tokens |
| DeepSeek | 0 | FAIL | Prose in both MORPH attempts |
| CodeLlama | 0 | FAIL | Schema descriptions rather than localization JSON |
| Mistral | 0 | FAIL | Malformed outer JSON/echoed input state |
| Granite | 2 | PASS | Valid hypotheses on second round; all four structured workflows valid |

Granite's structured hypothesis counts are 2/2/2/4, and both external workflows
also generated tokens. Its improvement over the failed 6k gate is real inference
evidence under the revised 32k gate; it does not imply benchmark accuracy or
superiority. Three failed model gates still prevent the five-family full study.
No failed checkpoint was removed or relabeled successful.

The local test suite now passes 90 unit tests and two integration tests. Lint,
source hashes and whitespace checks pass. The parser correction is tested locally;
it has not been silently applied to the frozen remote v5 deployment.

### Uniform output-task revision and v8 GPU validation

The v5 evidence establishes that the remaining failures include models explaining
the schema, echoing the input state and returning prose. To address that failure
mode, every structured workflow now receives the same explicit `task` instruction
inside its user request, in addition to the existing system/role instructions.
It asks for actual localization rather than a schema explanation, names the six
required root fields, requires string file paths and real numbered-source quotes,
and forbids prose, input-state copies, comments and ellipsis placeholders.
It permits an empty hypothesis list when there is no grounded proposal. This is
a prompt revision, not constrained decoding or conversion of prose into hypotheses.

The task does not assume MDE memory fields are present, so the plain-report
`no_mde` ablation can use it too. Existing source payloads and isolation policies
are preserved. All five model families and all structured variants receive the
same instruction. External adaptations retain their own text interfaces.
The models, seeds, sampling, budgets, native context and study record counts
are unchanged. Tests remain 90 unit and two integration checks passing.

The revised frozen snapshot is
`/home/babaei/projects/MORPH-FL-review-v8-20261020`; results are isolated under
`/home/babaei/morph-ufv/runs/ufv-review-v8-20261020-01/results`. Remote source
hashes, reused data coverage and checkpoint IDs/revisions were verified before
submission. Previous deployments, results and failed generations were preserved.

| Model | v8 validation job | A30 GPUs |
|---|---:|---:|
| Qwen | 17913 | 1 |
| DeepSeek | 17914 | 1 |
| CodeLlama | 17915 | 2 |
| Mistral | 17916 | 2 |
| Granite | 17917 | 1 |

These five jobs execute serially with one-hour per-job ceilings and `afterany`
dependencies. Each uses the stricter six-workflow gate, 32k cumulative budget,
one issue and two rounds. Submission does not imply success. No automatic full
continuation is installed. The once-per-minute local monitor and terminal
collection live under `hpc/logs/ufv-review-v8-20261020/`; do not duplicate it.
The original 99,544-record full experiment remains incomplete.

### v8 progress and semantic-validation fixes — October 20

The 06:15 UTC saved observation shows Qwen and Mistral passing all six workflows,
DeepSeek and CodeLlama finished without passing, and Granite still running.
Mistral has one valid MORPH hypothesis and three stateless-summary hypotheses:
the common explicit-task revision improves its output compliance on this case.
This is preflight evidence, not a benchmark accuracy measurement.

DeepSeek's MORPH calls produce a clarification request and then an empty
hypothesis list. CodeLlama's first MORPH response has four entries with null
mechanisms/predictions; all are correctly rejected, and its second response is
prose. Their stateless-summary variants produce two and one valid hypotheses
respectively. The remaining blocker therefore depends on workflow/session
behavior as well as the model; it is not a complete inability to generate JSON.
No gate is relaxed and neither failed checkpoint is removed from the design.

The review found two additional malformed-response hazards and fixed them locally:

- The controller now rejects non-list `invariants` and `ambiguities` before
  behavioral extraction. A JSON `null` in these fields previously could crash
  extraction and terminate a task, rather than be recorded as an invalid response.
- Synthesis now requires a nonempty prediction string or an object with a
  nonempty string description. Previously `str(None)` and `str(42)` could turn
  invalid values into superficially nonempty predictions. No missing prediction
  is fabricated. Regression coverage rejects null/numeric/list predictions,
  invalid description types and blank predictions.

Malformed calls continue to charge their actual input/output tokens. The local
v9 source hashes are updated, while the v8 remote snapshot remains unchanged.
All 92 unit tests and two integration tests pass, as do lint and whitespace checks.
No new GPU jobs or automatic full-study continuation were submitted in this pass.

### Completed v8 validation and checkpoint-revision guard

The October 20, 06:16 UTC terminal snapshot confirms collection of all five models'
six-workflow records. A local read-only audit applied the all-workflow validator
to each original record; its report is
`hpc/logs/ufv-review-v8-20261020/preflight-review.json`.

| Model | MORPH | Continuous | Fixed reset | Stateless | Gate |
|---|---:|---:|---:|---:|---|
| Qwen | 7 | 7 | 7 | 4 | PASS |
| DeepSeek | 0 | 0 | 0 | 2 | FAIL |
| CodeLlama | 0 | 0 | 0 | 1 | FAIL |
| Mistral | 1 | 1 | 1 | 3 | PASS |
| Granite | 1 | 1 | 1 | 1 | PASS |

Cells are valid hypothesis counts accumulated over two rounds, not accuracy.
The per-response cap remains four, so accumulated counts can exceed four.
Both external adaptations generated tokens for every model. Gate passes can
include invalid responses in another round; they establish that every workflow
ran and produced required valid output, not perfect model reliability.
DeepSeek and CodeLlama remain explicit failures in the five-family design.

A reporting issue was fixed locally: analysis previously checked model IDs in
coverage keys without verifying their checkpoint revisions. It now rejects LLM
records with missing/mismatched revisions before counting completeness. The
regression inserts a wrong-revision record into the partial-analysis fixture and
verifies rejection. Deterministic retrieval has no learned checkpoint to validate.
The local v10 protocol refreshes the changed analysis source hash; remote v8
predictions and its frozen protocol are untouched.

All 92 unit tests and two integration tests pass, along with lint, source-hash
and whitespace checks. No further GPU jobs were submitted. Three passing
families cannot substitute for the two failed families, and full execution
remains gated. No benchmark performance or favorable outcome is claimed.

### Instruction/data separation and v11 GPU validation

The v8 user request placed the explicit task inside its JSON input state. The
failed raw responses describe that JSON/schema or request clarification, despite
the task field. To make the task distinct from untrusted input data, the same
instruction now precedes a labeled `INPUT DATA (JSON)` block. The input payload,
roles, session history/forgetting, source visibility and token accounting remain
intact; the task wording, model pins and budgets are unchanged. This is a common
prompt-format revision for all structured variants and model families, not a
model-specific repair. The controller's behavioral/isolation tests pass with the
new framing. Success still requires real hypotheses from all required workflows.

The v11 frozen deployment is
`/home/babaei/projects/MORPH-FL-review-v11-20261020`; results are separate at
`/home/babaei/morph-ufv/runs/ufv-review-v11-20261020-01/results`. Source hashes,
data reuse coverage and model IDs/revisions were checked before submission.
No earlier deployment or prediction record was overwritten.

| Model | v11 job | A30 GPUs |
|---|---:|---:|
| Qwen | 17918 | 1 |
| DeepSeek | 17919 | 1 |
| CodeLlama | 17920 | 2 |
| Mistral | 17921 | 2 |
| Granite | 17922 | 1 |

The jobs run serially, with one-hour per-job ceilings. At the saved 07:15:58 UTC
observation on October 20, Qwen was running and the other four were pending;
no gate receipts were present. Only preflights were submitted. The local monitor
under `hpc/logs/ufv-review-v11-20261020/` polls once per minute and collects terminal
metadata/predictions. Full-study submission is not automatic.

A provenance omission was also corrected locally: `prior_cases.json` now includes
`astropy__astropy-12907`, whose responses have repeatedly been inspected while
revising the runtime/prompts. Later benchmark summaries including that issue
must disclose this prior exposure. The frozen v11 snapshot predates that metadata
correction; its source/protocol were not edited after submission. Previous failed
attempts remain evidence, and the 707-case union must not be called an untouched
holdout. All 92 unit tests and two integration tests pass, along with lint and
source-hash checks. GPU success for v11 remains unverified at this observation.

### Completed v11 validation and v12 field-type clarification

The October 20, 07:43:09 UTC snapshot confirms all v11 jobs finished and all 30
workflow records were collected. Four models pass. Valid structured-hypothesis
counts are:

| Model | MORPH | Continuous | Fixed reset | Stateless | Gate |
|---|---:|---:|---:|---:|---|
| Qwen | 5 | 5 | 5 | 4 | PASS |
| DeepSeek | 1 | 1 | 1 | 1 | PASS |
| CodeLlama | 1 | 1 | 1 | 0 | FAIL |
| Mistral | 2 | 1 | 1 | 3 | PASS |
| Granite | 1 | 1 | 1 | 1 | PASS |

Both external workflows generated tokens for every model. DeepSeek's successful
structured output follows the common instruction/data separation; it is real
runtime evidence, not measured benchmark performance. CodeLlama's remaining
failure is its stateless-summary output: both attempts emit a hypothesis, but
use null/object `invariants` and `ambiguities` instead of lists. Those responses
are correctly rejected under the existing type checks.

Inspection identified an ambiguity in the task: “Use null for unknown behavior
fields” did not distinguish nullable scalars from required lists. The v12 common
task now explicitly permits string/null only for expected/observed/trigger,
requires string lists for invariants/ambiguities (empty [] when unknown), and
requires a list for causal_chain. Validation is not relaxed and no model output
is normalized or fabricated. All models receive the same clarification.

The new frozen deployment is
`/home/babaei/projects/MORPH-FL-review-v12-20261020`, with separate results at
`/home/babaei/morph-ufv/runs/ufv-review-v12-20261020-01/results`.
Source hashes, dataset coverage and checkpoint IDs/revisions were verified before
submission. Corrected prior-exposure metadata was also copied into the run logs.

| Model | v12 job | A30 GPUs |
|---|---:|---:|
| Qwen | 17923 | 1 |
| DeepSeek | 17924 | 1 |
| CodeLlama | 17925 | 2 |
| Mistral | 17926 | 2 |
| Granite | 17927 | 1 |

The jobs execute serially with one-hour per-job ceilings and unchanged 32k/one
issue/two-round six-workflow gates. The local once-per-minute monitor and terminal
collector are under `hpc/logs/ufv-review-v12-20261020/`. No full-study continuation
is scheduled. All 92 unit tests and two integration tests pass; lint and source
hash checks pass. V12 real inference results remain pending at submission.

### All five v12 gates passed; corrected full study submitted

The October 20, 08:11:09 UTC terminal snapshot confirms all five v12 preflights
passed and all 30 workflow records were collected. A local audit checked all six
conditions for every pinned checkpoint, verified the receipt's per-workflow
counts and protocol hash, and confirmed BF16 backend metadata in every record.
The audit is `hpc/logs/ufv-review-v12-20261020/preflight-review.json`.

| Model | MORPH | Continuous | Fixed reset | Stateless | Gate |
|---|---:|---:|---:|---:|---|
| Qwen | 7 | 7 | 6 | 8 | PASS |
| DeepSeek | 2 | 2 | 2 | 1 | PASS |
| CodeLlama | 1 | 1 | 1 | 2 | PASS |
| Mistral | 2 | 2 | 2 | 4 | PASS |
| Granite | 1 | 1 | 1 | 1 | PASS |

Counts are accumulated valid hypotheses over two rounds, not file accuracy.
Both external adaptations also generated tokens for every model. Preflight
success establishes these interfaces on one previously inspected issue; it does
not establish full-coverage success, reset effectiveness or benchmark superiority.

The corrected full study now uses a separate deployment:

- Deployment: `/home/babaei/projects/MORPH-FL-full-v12-20261020`.
- Run: `ufv-full-v12-20261020-01`.
- Results: `/home/babaei/morph-ufv/runs/ufv-full-v12-20261020-01/results`.
- Frozen protocol SHA-256:
  `3afba2e46e120a3e35fc585e16ab9ddd474605ec93a5294abd8c618ad740f076`.
- Data job: 17928; model assets: 17929; per-model gates: 17930–17934.
- Retrieval: 17935; primary model arrays: 17937–17941.
- Side tracks: 17942–17961; final collection: 17962.

The full deployment copies the exact v12 inference source/protocol that passed
all five GPU gates. UFV configuration leaves that protocol byte-identical. The
resolved 34-stage/733-cell graph passes validation, full/smoke dry runs, shell
syntax and compilation checks. Dataset preparation reuses the verified pinned
inputs rather than rebuilding snapshots; assets reuse weights only on matching
IDs/revisions. The five inference gates are repeated within this full run before
any primary jobs may start. All earlier runs and downloaded assets are preserved.
Protocol, pins and prior-exposure metadata are copied into both frozen run config
and result roots. Site preparation/dry-run/submission receipts are preserved in
`hpc/logs/full-preparation` inside the full deployment.

The planned study remains 99,544 records: primary 63,630; ablations 12,000;
additional budgets 12,000; misdirection 6,000; policy 4,500; retrieval 1,414.
These are planned counts, not observed results. Heavy tracks remain sequential
with per-model one/two-A30 placement and small-model arrays throttled to two.
Each heavy cell retains a 12-hour ceiling and at most two requeues. The 8,640
initial heavy task-hour ceiling is a reservation limit, not measured cost; GPU
counts and retries must be included in actual accounting.

At the saved 08:18:35 UTC observation on October 20, dataset reuse had succeeded,
model assets were active and downstream inference remained pending. Scientific
completeness was unavailable. The detached once-per-minute full collector has
status/log/PID files under `hpc/logs/ufv-full-v12-20261020/`; do not launch another.
It transfers terminal results and separately records scientific completeness.
The local 30-minute review timer remains active for continuing checks.

Local validation remains 92 unit tests and two integration tests passing. No full
benchmark accuracy, causal-root validity, calibrated confidence or scientific
completion is inferred from submission or successful preflights.

### Full-run progress audit — October 20, 08:46:12 UTC

The actual full run has now completed dataset/asset reuse and all five in-run
preflights (17930–17934) successfully. The retrieval job 17935 is active; the
primary arrays and side studies wait on their declared dependencies. Inspection
of terminal job receipts and error logs found no failed jobs at this check.

The read-only live audit found 15 newline-complete retrieval records out of
1,414 planned retrieval records. No primary/side-study records were present in
that snapshot. It checked every observed study record's run signature against
its frozen cell settings, the protocol digest, repository/revision, report hash,
source archive digest metadata and duplicate condition keys. All passed. It also
verified all five in-run gate receipts reference the expected frozen protocol.
The report is `hpc/logs/ufv-full-v12-20261020/progress-review.json`.

This is a live snapshot, not final collection or the scientific completeness
report. Partially written final lines were excluded from this audit and were not
edited. Completed-record persistence/requeue behavior remains enabled. The frozen
full source, protocol, graph and running jobs were not changed; no new issue
required a code or protocol revision in this pass. Existing tests remain the
previously verified 92 unit and two integration checks.

### Retrieval checkpoint memory hazard and verified maintenance

The October 20, 09:15:21 UTC live health check found 294 unique retrieval progress
keys out of 1,414 expected and verified every frozen source hash. It measured
22,951,606,892 bytes of raw retrieval predictions (about 23 GB decimal), exceeding
the retrieval task's 16 GB RAM allocation. Raw graph payloads are packed only at
cell completion in v12, while interrupted-tail repair and resume read the entire
prediction file into memory. A later checkpoint resume therefore risks an OOM
before it can skip completed work. Filesystem-wide free space is not a substitute
for the process RAM limit or a user-quota check.

To preserve the frozen scientific protocol while addressing the active run:

- `scontrol requeuehold 17935` succeeded, stopping the writer and holding its
  requeue. The full graph retains the same job ID and dependencies.
- Slurm accepted `TimeLimit=12:00:00` for the held retrieval restart, replacing its
  original two-hour scheduler ceiling. Token/round budgets and case selection
  are unchanged. This operational override is recorded separately from config.
- Maintenance job 17966 has one A30, 32 GB RAM and a two-hour ceiling. It streams
  the stopped cell, preserves/removes only an interrupted final fragment, packs
  graphs with the existing lossless content-addressed format, then restores and
  hashes every logical record to compare before/after content and counts.
- A local callback releases job 17935 only if the verified receipt reports exact
  equality and the original v12 protocol hash still matches. On missing or failed
  verification the job stays held. Main studies cannot start while retrieval is
  held. Source/model files and prior completed inference outputs are not hot-patched.

The worker copy, allocation, hold actions and final receipt are preserved in the
remote run's `maintenance/` directory. Local callback status/log/PID are under
`hpc/logs/ufv-full-v12-20261020/checkpoint-maintenance/`. This is an additional
maintenance allocation outside the 34 scientific stages. Its actual resources
and the interrupted retrieval attempt must be included in system-level cost
accounting; scheduler retries and maintenance are not free completed-case tokens.
At this review's checkpoint the packing job is still running, so losslessness
and resumed execution are pending verification rather than claimed outcomes.

The local future-run fix streams interrupted-tail checks and resume provenance
validation, holding only one record at a time plus completed-condition keys.
The active v12 source remains frozen. The new `hpc/ufv/compact_checkpoint.py`
maintenance tool has regressions for exact model restoration, preservation of
an interrupted tail, and refusal to repair completed-record corruption. All 94
unit tests and two integration tests pass; lint and source hashes pass. The local
future protocol is v13; the running full experiment remains on v12.

### Verified retrieval recovery — October 20, 09:46:03 UTC

Maintenance job 17966 completed successfully, and the callback released retrieval
job 17935 at 09:44:20 UTC only after checking the verified packing receipt and
original v12 protocol digest. The production before/after audit reports:

- Complete records before/after: **315 / 315**.
- Canonical logical SHA-256 before/after:
  `c053cd8b53f45507a53c703aa3674cac33b1bedaf19f833e0e24f30186d538a2`.
- Interrupted-tail repair: **none**; no bytes or records required removal.
- Prediction JSONL: **24,584,113,527 → 10,991,094 bytes**.
- New content-addressed graph archives: **157**. The complete graph store,
  including its existing artifact, contains 158 archives totaling 305,643,414
  compressed bytes. Graph payloads were externalized, not discarded.

This is a full logical-content comparison, not only a row-count comparison.
Model restoration is included in the canonical fingerprints. Hold, scheduler
limit override, packing and release receipts remain in the remote run's
`maintenance/` directory; the local callback stores the verified receipt in
`hpc/logs/ufv-full-v12-20261020/checkpoint-maintenance/status.json`.

The restarted job logs restart 1 and continues with record 316, then 317/318,
without rerunning the previous completed conditions. The live 09:46:03 UTC
progress audit verifies 318 unique condition keys out of 1,414 expected, with the
latest completed condition `django__django-13569 / graph`. Primary and side
studies still wait for retrieval's successful completion. No new failed jobs
were found in this review.

The running model source, sampling, source snapshots and scientific protocol
were not changed. The retrieval allocation now retains its accepted 12-hour
ceiling. Future v13 streaming fixes and their previously verified 94 unit/two
integration tests remain local; no new protocol revision or GPU allocation was
needed in this pass. Scientific completeness and full accuracy remain pending.

### Healthy retrieval progress — October 20, 10:14:43 UTC

Retrieval job 17935 is running and has advanced from the previous 318-record audit
to 576/1,414 unique completed conditions (40.7%). All progress keys remain unique;
the expected denominator remains 1,414. Error-log inspection found no traceback,
OOM, killed-process or job-error signatures, and all frozen inference source
hashes match the v12 protocol. Primary and side-study jobs remain correctly
pending on retrieval. Final scientific completeness is not yet available.

The current read-only audit is saved in
`hpc/logs/ufv-full-v12-20261020/live-health.json`. No new fault was substantiated,
so no code, source/protocol, scheduler or GPU allocation changes were made.

### Progress checkpoint — October 20, 10:44:41 UTC

Retrieval has advanced to 954/1,414 completed conditions (67.5%), up from 576 in
the previous review. Progress keys are unique, frozen source hashes match and
error-log scanning found no failure signatures. Primary/side-study dependencies
are still pending and scientific completeness is unavailable. The live audit was
atomically refreshed at `hpc/logs/ufv-full-v12-20261020/live-health.json`.
No code, protocol, scheduler or additional GPU changes were required.

### Progress checkpoint — October 20, 11:14:41 UTC

Retrieval job 17935 remains running with 1,187/1,414 unique completed conditions
(83.9%), up from 954 at the prior review. The expected denominator and frozen
source hashes are unchanged; error-log scanning found no failure signatures.
Primary and side-study jobs still wait for retrieval completion. The live audit
was refreshed atomically at `hpc/logs/ufv-full-v12-20261020/live-health.json`.
No new code, protocol, scheduler or GPU-allocation change was required.


### Full v12 health checkpoint — 2026-10-20 11:44:41 UTC

The live audit found 1,218 of 1,414 retrieval records (86.1%), with unique
progress keys, no detected failure signatures and matching frozen source hashes.
All five in-run gates succeeded. Retrieval job 17935 is still running; primary
and side jobs remain pending its successful completion. No completion receipt
or full scientific result is available yet. No additional runtime fix was
justified by this checkpoint. The raw audit is saved locally in
`hpc/logs/ufv-full-v12-20261020/live-health.json`.


### Full v12 health checkpoint — 2026-10-20 12:15:04 UTC

Retrieval reached 1,251/1,414 unique records (88.5%). All five preflight
receipts contain six completed records each. No new inference failure signatures
were detected, and every frozen source hash matches. Retrieval has no completion
receipt yet; the collector reports it running and downstream jobs pending.

The stderr audit also exposed a launcher warning: `scontrol` is unavailable
inside the container when `setup_distributed` sets `MASTER_ADDR`. This did not
prevent the single-node gates from passing. The local launcher now respects an
explicit master address, uses the hostname for a single-node job without
`scontrol`, and fails clearly for a multi-node job without either resolver. It
also returns success explicitly after successful single-node setup. Shell syntax
and direct checks of the single-node, explicit-address and missing-multi-node
resolver branches passed. This change is for future launches; the active frozen
deployment is unchanged.


### Full v12 health checkpoint — 2026-10-20 12:44:40 UTC

Retrieval advanced by 36 records since the 12:15 audit, reaching 1,287/1,414
unique progress keys (91.0%). All five preflight completion receipts remain
present, with six records each. The monitor reports retrieval job 17935 running
and downstream jobs pending. No retrieval completion receipt or completed
primary study is available yet. The source hash audit passed and no new inference
failure signatures were detected. No further runtime change was justified.
