# MORPH-FL

Model-driven fault hypothesis search with evidence-preserving strategic forgetting. The [research proposal](docs/MORPH-FL_Research_Proposal.md) defines the hypotheses; the [implementation map](docs/ARCHITECTURE.md) traces its conceptual algorithms and T1–T7 transformations to source and tests.

The Python implementation includes typed behavioral/system/hypothesis/evidence models, AST dependency analysis and local def-use, investigation selection, static and registered container probes, scoped support/contradiction updates, independent investigator contexts, adaptive forgetting, diverse portfolios, budget enforcement and abstention. Fourteen policy conditions cover the proposed ablations and controlled baselines.

```bash
python3 -m pip install -e '.[dev,analysis]'
python3 -m unittest discover -s tests -v
ruff check src tests
ruff format --check src tests
bash hpc/scripts/selftest.sh
```

GPU inference and dataset preparation use optional `inference` and `data` dependencies. On Alliance clusters, use the module/wheelhouse workflow in the [Nibi guide](hpc/docs/hpc-guide.md). See [CONTRIBUTING.md](CONTRIBUTING.md) for package boundaries and scientific invariants.

A [prospective full Lite + Verified study](experiments/full/README.md) now defines four pinned BF16 models, three seeds, full primary comparisons, component/budget/recovery side studies, and a staged Nibi pipeline capped at four concurrent H100s. See [live submission status](experiments/full/status.json); a submitted smoke is not a completed full evaluation.

**Evaluation status:** local 7B/30B comparisons include pinned Agentless/RGFL component adaptations, six additional prospectively selected SWE-bench Lite cases, context-sensitivity controls and longer reset diagnostics. Results are mixed or unfavorable to a consistent MORPH-FL advantage; the stateless summary remains competitive and cheaper. See the [measurement tables](experiments/baselines/results/report.md) and [RQ1–RQ3 discussion](experiments/baselines/results/research_questions.md). Labels are unreviewed patch-change proxies. A Nibi two-case BF16 runtime run completed main/scoring/collection, but setup preflight lacks a completion record and one case has no valid hypotheses; its [validation is partial](experiments/baselines/results/nibi_smoke/README.md). No large benchmark or dynamic-container validation is established.

The [TSE research draft](docs/TSE/README.md) includes a [compiled paper](docs/TSE/morph-fl.pdf), motivated definitions and pseudocode, generated result figures/tables, and three internal AI reviewer reports with revision responses. Its claims remain limited to the measured exploratory evidence.

For paper writing, use [the five executable algorithm definitions](docs/ALGORITHMS.md) and [claim-alignment matrix](docs/CLAIM_ALIGNMENT.md). A separately versioned [reset-policy sensitivity study](experiments/alignment/README.md) tests exposed parameters on a known development issue; no calibrated, globally optimal threshold is claimed.

The `hpc/` scheduling, audit and collection tools were scaffolded using [ai4se4ai-lab/use-hpc](https://github.com/ai4se4ai-lab/use-hpc). Keep credentials outside this repository.

Local DGXSpark development and held-out comparisons use the installed Qwen coder 7B/30B Ollama models. See [the local protocol](experiments/local/README.md) and [pilot measurements](experiments/local/results/report.md). The adapter uses Ollama’s [raw generation and structured output API](https://docs.ollama.com/api/generate), pins model/tokenizer provenance and rejects cloud-backed entries. Intermediate regressions are retained alongside improved versions; statistical improvement is not assumed.
