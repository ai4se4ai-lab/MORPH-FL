# MORPH-FL: Does Forgetting Help?

Research code and saved evaluation artifacts for **Does Forgetting Help? Studying Context Reset Policies in LLM Fault Localization**, submitted to the [Journal of Systems and Software (JSS)](https://www.sciencedirect.com/journal/journal-of-systems-and-software).

Read the [paper PDF](docs/JSS/main.pdf), [LaTeX source](docs/JSS/main.tex), and [paper artifact guide](docs/JSS/README.md).

MORPH-FL investigates whether resetting an LLM's investigation context helps fault localization. It combines source retrieval, structured fault hypotheses, recorded evidence, and context reset policies to rank suspect files and functions from a bug report and a pre-fix repository snapshot. The four evaluated workflows are full adaptive (`morph`), continuous (`no_forgetting`), fixed reset (`fixed_reset`), and observation-only (`stateless_summary`). Observation-only uses compact observations as memory, omits dialogue and several model-state fields, and disables pruning; its historical artifact name does not mean an LLM-written summary.

**Start here:** with Node.js 22+, run `node docs/JSS/scripts/analyze_completed_study.mjs` from the repository root to check all six paper result tables against the saved study scores. No GPU, Python installation, model weights, or API key is required. The Python examples below rebuild the original collection report and demonstrate localization on one SWE-bench case.

## Available results

The paper reports a fully collected, exploratory study of **50 issues from 12 repositories**, two models, four workflows, and seed 1: **400 primary predictions plus 100 deterministic retrieval controls**. Subjects come from the deduplicated union of SWE-bench Lite and Verified, balancing repositories after excluding thirteen previously inspected development IDs. Both models use BF16, a 32,000 input-plus-output token ceiling, and at most 16 attempts. The same issues are used across models and workflows; they are not 100 independent bugs. Selection is recorded in [pilot.json](experiments/pilot/results/pilot.json). Original paths retain the name `pilot` for provenance.

| Model | Workflow | File Top-1 | File Top-5 | Function Top-1 | Mean tokens | Mean resets |
|---|---|---:|---:|---:|---:|---:|
| Qwen2.5-Coder 7B | Full adaptive | 42% | 72% | 16.7% | 28,257 | 0.18 |
| Qwen2.5-Coder 7B | Continuous | 42% | 74% | 16.7% | 27,573 | 0.00 |
| Qwen2.5-Coder 7B | Fixed reset | 42% | 76% | 14.6% | 29,114 | 1.04 |
| Qwen2.5-Coder 7B | Observation-only | 50% | 78% | 22.9% | 29,325 | 0.00 |
| DeepSeek-Coder 6.7B | Full adaptive | 40% | 70% | 0% | 29,197 | 0.60 |
| DeepSeek-Coder 6.7B | Continuous | 40% | 70% | 0% | 27,912 | 0.00 |
| DeepSeek-Coder 6.7B | Fixed reset | 40% | 70% | 0% | 29,553 | 1.44 |
| DeepSeek-Coder 6.7B | Observation-only | 40% | 72% | 12.5% | 29,920 | 0.00 |

File metrics use 50 eligible issues; function metrics use 48. BM25 and graph retrieval each achieve 40% file Top-1, 70% Top-5, and 86% Top-10; they do not produce function rankings. Token means count input plus output for completed attempts and exclude interrupted work.

Full adaptive, continuous, and fixed reset have **identical per-issue file Top-1 hit indicators** for each model; this does not mean their complete rankings are identical. Observation-only has the highest observed function Top-1 for both models and file Top-1 for Qwen. Adaptive resets affect **8/50 Qwen runs and 29/50 DeepSeek runs** without additional file Top-1 hits over continuous context. DeepSeek retains final hypotheses in **6/50 full adaptive runs versus 47/50 observation-only runs**; empty pools return retrieval file order and no hypothesis-derived function ranking.

These exploratory results do not establish equivalence or a general benefit from forgetting. Observation-only bundles several configuration changes, and a known duplicated-ambiguity prompt-growth defect affects the frozen richer views. Both constrain causal interpretation. Mean elapsed times for observation-only versus full adaptive are 140.3 versus 93.6 seconds with Qwen and 111.5 versus 55.0 seconds with DeepSeek.

Inspect the [final pilot report](experiments/pilot/results/analysis/report.md), [per-case scores](experiments/pilot/results/analysis/scores.csv), [retrieval controls](experiments/pilot/results/analysis/controls.json), [saved independent verification](experiments/pilot/results/analysis/final-verification.json), and [interpretation and diagnostics](docs/UFV/pilot_results.md).

The repository also contains an **earlier, partial full-study snapshot** under [docs/evaluation_assets](docs/evaluation_assets/). Its different cohorts, six inference workflows, and three-seed Qwen averages are **not inputs to the submitted paper's empirical tables**. The five-model full-study protocol describes a larger design, not a completed evaluation. The JSS paper reports only the bounded two-model study above.

## Reproduce the JSS paper's tables

With **Node.js 22 or later**, run from the repository root:

```bash
node docs/JSS/scripts/analyze_completed_study.mjs
```

Expected output:

```json
{"status":"passed","primary":400,"controls":100,"issues":50,"repositories":12,"tables":6}
```

The analyzer checks every issue/model/workflow/seed key, eligibility, token accounting, saved means, the 100 controls, reset exposure, and paired hit/pool changes. It verifies deterministic reconstruction of these six files under [docs/JSS/generated](docs/JSS/generated/):

| Generated file | Paper results |
|---|---|
| `subjects.tex` | Repository composition and function eligibility |
| `ranking.tex` | File/function Top-k and MRR |
| `paired.tex` | Paired Top-1 discordances, differences, and saved intervals |
| `process.tex` | Reset exposure and final hypothesis pools |
| `cost.tex` | Mean total/output tokens and elapsed seconds |
| `funnel.tex` | DeepSeek response and hypothesis diagnostics |

It writes [completed-study-audit.json](docs/JSS/validation/completed-study-audit.json) with input and manuscript digests. Saved bootstrap endpoints are read from the original report; this command does not recompute them or freshly validate raw prediction signatures. To regenerate the table files, use `node docs/JSS/scripts/analyze_completed_study.mjs --write`.

The tables are inlined in the single-file manuscript, [main.tex](docs/JSS/main.tex). Regenerating `generated/*.tex` does not update those inlined copies; intentional result changes must also be reflected there. With a LaTeX installation providing `pdflatex` and `bibtex`, build the paper from PowerShell:

```powershell
./docs/JSS/build.ps1
```

See [the JSS artifact guide](docs/JSS/README.md) for build details. The Python workflow below separately reconstructs the original report and its bootstrap intervals from saved scores.

## Installation

Use Python **3.11 or later** and Git. Run commands from the repository root. The examples below use Bash on Linux/macOS or WSL; Python scripts also run on Windows. GPU reproduction uses the documented Linux/Slurm environment.

```bash
git clone --branch paper/tse-manuscript-20261020 https://github.com/ai4se4ai-lab/MORPH-FL.git
cd MORPH-FL
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m morph_fl --help
```

In Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`. The base package is sufficient to rebuild the pilot report from saved scores. Install extras as needed:

```bash
# Download benchmark data and generate the earlier snapshot's plots:
python -m pip install -e ".[data,analysis]"
# Local BF16 GPU inference (install a CUDA-compatible PyTorch build):
python -m pip install -e ".[inference,data]"
```

Dependencies and optional backends are declared in [pyproject.toml](pyproject.toml). Initial dataset/model downloads require network access; inference uses locally downloaded weights. GPU memory requirements depend on the checkpoint; the measured pilot used one NVIDIA A30 per Qwen/DeepSeek task. CPU-only report rebuilding needs no model weights, GPU, or provider API key.

## Quickly reproduce the saved pilot report

This rebuilds tables, means, and descriptive repository-cluster bootstrap intervals from the committed **400 per-case score records**, without running models or overwriting the saved evidence. Run this Bash block after installation:

```bash
python - <<'PY'
import csv
import json
from pathlib import Path
from experiments.pilot.manage import report

source = Path("experiments/pilot/results/analysis")
with (source / "scores.csv").open(newline="") as stream:
    records = list(csv.DictReader(stream))
numeric = ("seed", "top1", "top5", "function_top1", "tokens",
           "end_to_end_seconds", "resets")
for row in records:
    row.update({key: float(row[key]) if row[key] else None for key in numeric})
    row["eligible"] = row["eligible"] == "True"
assert len(records) == 400
output = Path("artifacts/reproduced-pilot")
report(records, output, "50-issue two-model pilot")
assert json.loads((output / "summary.json").read_text()) == json.loads(
    (source / "summary.json").read_text())
assert (output / "report.md").read_text() == (source / "report.md").read_text()
print(f"Reproduced saved summary and report exactly: {output}")
PY
```

For PowerShell, save the Python body as `reproduce_pilot.py` in the repository root and run `python reproduce_pilot.py`. Output is `artifacts/reproduced-pilot/report.md`, `summary.json`, and a copy of the score rows used by the report. This checks aggregation against the stored results; it does not independently re-score raw model predictions or repeat the saved provenance verification.

To rebuild the **earlier partial snapshot** from its compact predictions and evaluator labels:

```bash
python -m pip install -e ".[analysis]"
python docs/evaluation_assets/build_report.py
```

This writes `docs/EVALUATION_RESULTS_REPORT.md`, summary/effect CSVs, cohort lists, and PNG/SVG plots under `docs/evaluation_assets/`. It regenerates existing assets in place. Its snapshot is fixed; running this command does not collect newer cluster results. See [snapshot provenance](docs/evaluation_assets/snapshot/snapshot.json) and [matched cohorts](docs/evaluation_assets/cohorts.json).

## Quickly run fault localization

The following CPU example downloads one pinned SWE-bench Lite test case and its pre-fix source, runs BM25, and scores its file ranking:

```bash
python -m pip install -e ".[data]"
python -m morph_fl prepare --out artifacts/quick/data --limit 1 --revision 6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2
python -m morph_fl run --cases artifacts/quick/data/cases.jsonl --out artifacts/quick/bm25.jsonl --variant bm25 --limit 1
python -m morph_fl score --predictions artifacts/quick/bm25.jsonl --labels artifacts/quick/data/labels.jsonl --out artifacts/quick/bm25-scores.csv
```

Replace `bm25` with `graph` and use a different output filename for the other deterministic control. Preparation writes agent inputs to `cases.jsonl` and separate evaluator-only patch labels to `labels.jsonl`; labels are passed only to scoring.

For an adaptive-reset demonstration on a CUDA GPU, download the pinned Qwen checkpoint and run:

```bash
python -m pip install -e ".[inference,data]"
python -m morph_fl download-model --model Qwen/Qwen2.5-Coder-7B-Instruct --revision c03e6d358207e414f1eca0bb1891e29f1db0e242 --out artifacts/models/qwen2.5-coder-7b
python -m morph_fl run --cases artifacts/quick/data/cases.jsonl --out artifacts/quick/morph.jsonl --variant morph --model artifacts/models/qwen2.5-coder-7b --seed 1 --budget 32000 --rounds 16 --limit 1
python -m morph_fl score --predictions artifacts/quick/morph.jsonl --labels artifacts/quick/data/labels.jsonl --out artifacts/quick/morph-scores.csv
```

Use `--variant no_forgetting`, `fixed_reset`, or `stateless_summary` with separate output paths to explore the alternatives. Runs save predictions, configuration signatures, and evidence artifacts; compatible completed cases are skipped on resume. A one-case run may never trigger a reset.

**The CLI example demonstrates the current implementation.** Its generic Transformers adapter has different generation settings from the frozen study runner, and current source includes post-pilot corrections. Matching model, seed, rounds, and budget alone does not reproduce the measured pilot. Use the frozen inference workflow below for that purpose.

## Repeat the measured inference experiment

The measurement configuration is recorded in [pilot.json](experiments/pilot/results/pilot.json), [model and dataset pins](experiments/full/pins.json), and the [full protocol](experiments/full/protocol.json). The pilot uses model indices 0 and 1:

| Checkpoint | Pinned revision |
|---|---|
| `Qwen/Qwen2.5-Coder-7B-Instruct` | `c03e6d358207e414f1eca0bb1891e29f1db0e242` |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | `e5d64addd26a6a1db0f9b863abf6ee3141936807` |

The frozen runner uses BF16, a 16,384-token native context limit, temperature 0.2, top-p 0.95, top-k 50, and at most 1,536 generated tokens per call. The per-case 32,000-token budget includes input and output across calls. The pilot retains the original full-run case order and 32-shard assignment, then filters to its 50 selected IDs and four workflows.

Exact historical reproduction requires artifacts **not distributed in this Git checkout**: the frozen v12 deployment and environment, prepared full-run cases/labels and source snapshots, pinned model weights, and the raw predictions/configurations, evidence archives, import records, and completion receipts. Historical absolute paths in manifests identify the original deployment; they are not portable download locations. The committed compact snapshot is from the earlier partial study and is not a substitute for the pilot's raw records.

With the original frozen deployment and prepared pilot results restored, the supported commands are:

```bash
# Run from the frozen deployment with its environment and prepared result directory.
# Repeat for model 0 and 1 and each applicable original shard 0..31.
python -m experiments.pilot.manage run --results /path/to/pilot-results --model 0 --shard 0

# Aggregate completed predictions, then independently validate coverage/provenance.
python -m experiments.pilot.manage analyze --results /path/to/pilot-results
python -m experiments.pilot.finalize --results /path/to/pilot-results
```

`manage prepare --source /path/to/full-results --results /path/to/new-pilot-results` prepares a separate pilot directory from validated full-run artifacts, selects subjects, and imports compatible predictions. It is not a standalone downloader. Run GPU work and preparation in appropriate compute allocations; see the [pilot workflow](experiments/pilot/README.md), [UFV environment and scheduling](hpc/ufv/README.md), and [full-study workflow](experiments/full/README.md).

The runners deliberately reject changed protocol/source identities and incompatible resume settings. Preserve the measured deployment and outputs. Use a new versioned protocol and output directory for experiments with current source; changing a recorded hash does not make a rerun a reproduction of the historical measurement. Full inference is stochastic, so rebuilding saved analyses is the direct route to the reported numbers; new GPU runs also depend on the original software/hardware environment.

## Evaluation scope

- Ground truth consists of **unreviewed reference-patch file/function proxies**. Results measure localization, not repair success or human-adjudicated root cause.
- Top-k counts whether any target occurs in the first k deduplicated predictions. MRR uses the first target's reciprocal rank. Empty completed predictions remain misses; empty label sets are ineligible separately for files and functions.
- Pilot comparisons use the same completed eligible issues across all four workflows. The report uses 2,000 repository-cluster bootstrap draws with a fixed seed; intervals are exploratory and unadjusted for multiple comparisons.
- The pilot is one-seed exploratory evidence and can reuse previously generated full-run predictions. Outcome-informed changes need separate validation on untouched cases.
- Agentless and RGFL conditions in the broader study are restricted component adaptations. They do not reproduce the complete published systems; see [baseline scope](experiments/baselines/README.md).

## Repository map

| Path | Purpose |
|---|---|
| [src/morph_fl](src/morph_fl/) | CLI, inference adapters, source analysis, hypothesis search, evidence handling, and metrics |
| [experiments/pilot](experiments/pilot/) | Completed two-model study orchestration, verification, and saved results |
| [docs/JSS](docs/JSS/) | Submitted paper, six-table reconstruction, and LaTeX build |
| [experiments/full](experiments/full/) | Larger study design, pinned inputs, GPU runner, and analysis |
| [docs/evaluation_assets](docs/evaluation_assets/) | Earlier compact prediction snapshot and report/figure builder |
| [experiments/local](experiments/local/) | Earlier small Ollama development/test workflow |
| [experiments/baselines](experiments/baselines/) | Restricted Agentless/RGFL adaptations and historical controls |
| [experiments/alignment](experiments/alignment/) | Reset-policy alignment experiments |
| [hpc](hpc/) | Cluster setup, Slurm workflows, and collection tools |
| [tests](tests/) | Unit and integration checks |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture and implementation guide |

For development, install `python -m pip install -e ".[dev]"` and run `python -m unittest discover -s tests`. Contribution guidance is in [CONTRIBUTING.md](CONTRIBUTING.md).

## License and paper

The project uses the [MIT license](LICENSE). Vendored baseline components retain their accompanying licenses and [source manifest](src/morph_fl/baselines/vendor/manifest.json).

Paper: **Does Forgetting Help? Studying Context Reset Policies in LLM Fault Localization**. Submitted to the **Journal of Systems and Software**; publication metadata and a DOI can be added when available.
