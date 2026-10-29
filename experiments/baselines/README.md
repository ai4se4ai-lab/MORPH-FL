# Local upstream-baseline study

This directory evaluates **budget-constrained adaptations**, not exact reproductions of published results. Both use installed Ollama Q4_K_M Qwen2.5-Coder 7B and Qwen3-Coder 30B, temperature 0.2, context 16,384, case-derived seed 1, and a 16,000 input-plus-output token ceiling. MORPH-FL's source-only investigation and the external workflows use the same pre-fix snapshots, reports, production-Python scope, and tokenizer accounting. They choose different source contexts; external workflows retain upstream free-text decoding, while MORPH-FL uses structured JSON decoding. This is a same-model/budget comparison, not an identical-tool ablation.

## Source and adaptation provenance

Repositories were cloned to ignored `artifacts/upstream/`. Exact upstream commits and selected source hashes are in `src/morph_fl/baselines/vendor/manifest.json`; MIT licenses accompany the vendored components. Prompts were extracted from Python ASTs without executing provider API wrappers. Agentless's source compressor is copied unchanged. Provider calls, dataset orchestration, parsing, budget handling and experiment persistence are local adaptations.

- **Agentless**, `OpenAutoCoder/Agentless`, commit `5ce5888b9f149beaace393957a55ea8ee46c9f71`: upstream repository-tree file prompt → up to five files → upstream compressed skeletons of the first three → upstream element prompt. We evaluate files and exact qualified functions; class-only output is not silently expanded into every method. Embedding/hybrid retrieval, fine-grained line localization, repair and validation are outside this condition.
- **RGFL**, `MelikaSepidband/RGFL`, commit `62195e66579c5c99add5a715d36a57e2b202419f`: the above file selection → original per-file reasoning prompts for up to three candidates → original file ranking prompt → Agentless element shortlist → original reasoning prompts for up to three selected functions → original element ranking prompt. The original embedding retrieval is omitted. This is a restricted reasoning component comparison; it is not the full published RGFL system. Original candidates omitted by the reranker remain at the end of the ranking, and no gold-dependent fallback is used.

All paths and qualified functions are checked against the pre-fix source. Unsafe upstream `eval` parsing is replaced by matching against known paths. Truncation removes context from the end to meet each declared stage allocation; every original/shown character count, exact prompt, response and actual token charge is logged. Remaining global budget can prevent later stages. Abstention, invalid predictions and budget exhaustion stay in the denominator. No model output is executed.

## Three distinct experimental tracks

1. `protocol.json`: 24 new baseline case-runs on the original three development and three reused test cases. Original MORPH-FL/control records are reused without rerunning or tuning them. The old test cases are no longer fresh validation.
2. `fresh_protocol.json`: six previously unused repositories; first six in lexical order, then minimum public-ID hash per repository. Two upstream adaptations, MORPH-FL, stateless summary, BM25 and graph controls use both models. This is 72 case-runs, including 24 repeated deterministic IR records, not 72 independent bugs. Two rounds isolate short-budget workflow performance and do not establish forgetting effectiveness.
3. `mechanism_protocol.json`: one original development case, both models, four reset/memory conditions, eight rounds and 48,000 tokens. This diagnoses reset execution and costs. It does not measure general incorrect-lead recovery or isolate all MDE components.

Dataset revision: `6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2`. Labels are **unreviewed patch-change proxies**, separate from all inference inputs. Case-level eligibility is explicit. Public-benchmark pretraining contamination is not ruled out.

## Reproduction

```bash
python -m pip install -e '.[baselines,local-eval,analysis,dev]'
PYTHONPATH=src python experiments/baselines/run.py
PYTHONPATH=src python experiments/baselines/prepare_fresh.py
PYTHONPATH=src python experiments/baselines/extended.py
PYTHONPATH=src python experiments/baselines/report.py
```

The original pilot snapshots/parquet files must first exist as described in `experiments/local/README.md`. Scripts check frozen source hashes before inference; source archives preserve the measured implementation. Never update a protocol hash to relabel old predictions. The six fresh IDs are locked before snapshot/label preparation. Raw predictions with full prompts remain in ignored `artifacts/baselines/`. Compact predictions, scores, source manifests, figures and discussion are published here. No cloud API credentials are required.

The baseline timer starts after initial repository indexing; MORPH-FL includes its structural analysis. Both exclude dataset downloads and installation. These different timer boundaries, cache/load states and execution times preclude end-to-end speed comparisons. Logical token counts are the primary cost measure; dollars are unavailable for this local machine.

Function-metric caveat: the upstream element prompt permits classes and global variables as valid outputs. This study counts only exact qualified functions for function Top-k, so class-only output may be a useful coarse localization while receiving zero on this strict metric. These function scores are not equivalent to the upstream papers' element-coverage metrics.

## Post-hoc context sensitivity

The original 2,600-token file-selection allowance truncated the tree on four fresh cases and hid target directory entries on three. `full_tree_protocol.json` declares an additional control after observing this limitation: the same baselines may use up to 12,000 tokens for file selection, with the same overall 16,000-token ceiling and all other caps unchanged. This may leave less budget for later reasoning/element stages. `full_tree.py` supplies a documented investigator subclass for that single change, without modifying the frozen source modules. Its separate script hash is recorded. Results are labeled `agentless_fulltree` and `rgfl_fulltree` under `fresh_sensitivity`; both original and expanded profiles remain reported. These are post-hoc comparisons on reused cases, not an additional independent test set. No MORPH-FL tuning accompanies them.

After the main sequence completes, run `PYTHONPATH=src python experiments/baselines/full_tree.py`, then `report.py`, `verify.py`, `export.py`, `visibility.py` and `figures.py` in this directory. Verification checks cell coverage, model digests, budget accounting and reset observation retention. Full transcripts are retained locally; compact exports omit repository source text.

## Reproducing historical results after an algorithm extension

The alignment extension changes the working `src/` hash. Historical benchmark scripts deliberately reject that source. Extract the measured archive into an isolated directory and point both Python imports and source validation at it:

```bash
mkdir -p artifacts/baselines/revisions/measured
# Use the exact archive named in source-versions/manifest.json.
tar -xzf experiments/baselines/source-versions/baselines-29ec0345852c.tar.gz \
    -C artifacts/baselines/revisions/measured
MORPH_FL_SOURCE=artifacts/baselines/revisions/measured/src \
PYTHONPATH=artifacts/baselines/revisions/measured/src \
    python experiments/baselines/run.py
```

Use the same two environment variables for `extended.py`; use the frozen `PYTHONPATH` for `full_tree.py`. The sensitivity runner itself is SHA-pinned by its protocol and has not been rewritten. Existing completed cells are reused, not relabeled with the extension's source. Changing generation settings, source or datasets requires a new output directory and a new protocol.
