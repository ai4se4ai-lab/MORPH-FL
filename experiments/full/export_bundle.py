"""Export complete non-smoke TeX/tables for review at final collection."""

import argparse
from pathlib import Path

from experiments.full.paper_update import export_bundle

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True)
    p.add_argument("--template", required=True)
    a = p.parse_args()
    export_bundle(Path(a.results), Path(a.template))
