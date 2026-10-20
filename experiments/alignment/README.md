# Paper-alignment extension and policy sensitivity

The supplied Gemini transcript suggests normalized thresholds and a five-algorithm specification. The implementation extension exposes the actual historical PPF rule as configuration, records diagnostic values for every valid round, and supports an optional minimum fraction of the original token budget before resets. The historical defaults preserve the old trigger decisions; a new fractional gate is not silently applied to old results.

The canonical method and differences from the sketch are in `docs/ALGORITHMS.md` and `docs/CLAIM_ALIGNMENT.md`. They describe actual lexical/path diversity, heuristic probe utility, limited dependency neighborhoods, role-separated sequential dialogues, scoped observations and cumulative accounting. Mathematical semantic-memory guarantees, graph-edit distance, entropy optimization and calibrated confidence are not claimed.

`protocol.json` freezes a development-only sensitivity experiment before inference: the previously studied pydicom-901 issue, both installed 7B/30B models, windows 3/4/5, eight rounds, 48,000 tokens and a 15% original-budget gate. Other thresholds remain the declared historical defaults. This provides an operational check across settings; it does not calibrate parameters on an independent validation set or demonstrate generalization. Full source and archive hashes are in `source-versions/manifest.json`.

```bash
PYTHONPATH=src python experiments/alignment/run.py
PYTHONPATH=src python experiments/alignment/report.py
```

The source hash check refuses to attach old measurements to changed code. Exact reproduction uses the archived source, with the same dataset snapshots and pinned model digests. Raw records, full context artifacts and observations remain in `artifacts/alignment/`; compact tables, all round-level reset decisions and verification manifests are collected in `results/`. No gold label is supplied to inference. Do not select the best window from this diagnostic and report that result as held-out benchmark improvement.


For a configured CLI run, pass `--reset-policy experiments/alignment/reset-policy.example.json` to `morph-fl run`. The example sets the experimental 15% gate; omitting the option uses the historically equivalent zero-fraction default. All selected settings enter the resume signature and audit so changed policies cannot silently resume an old cell.
