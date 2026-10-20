# Development

Use Python 3.11 or newer. Install `python -m pip install -e '.[dev,analysis]'` in a local virtual environment. Optional inference and data extras install model/dataset dependencies; base package imports do not require a GPU or network.

Run `ruff check src tests`, `ruff format --check src tests`, `python -m unittest discover -s tests -v`, and `bash hpc/scripts/selftest.sh`. Unit tests cover scientific invariants; integration tests use explicitly synthetic cases to check CLI/scoring/collection plumbing. Keep benchmark findings separate from deterministic fixtures.

Application services belong in `src/morph_fl/application.py`; algorithms belong in their domain package. The CLI parses arguments and delegates. Keep labels and patch parsing inside `datasets/` and `evaluation/`; investigator contexts must contain only validated public-case fields, pre-fix source and observations. New inference backends should implement `inference.protocol.ModelBackend` and account for tokens even when output parsing fails.

Every supported transformation needs a meaningful test of its scientific contract. Source facts, derived dependencies and runtime observations must retain distinct epistemic status. A model's confidence or agreement between agents is not empirical evidence. No change may delete observation artifacts or reset incurred budgets when forgetting contexts.

Container procedures are an explicit experiment configuration. Do not add host shell execution for agent-generated commands. Run real model/data tests in GPU allocations on the cluster. Keep source versions used by queued/running experiments unchanged; deploy new versions into a separate directory and new run ID.
