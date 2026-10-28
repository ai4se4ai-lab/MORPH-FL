# Fast pilot progress

Updated: 2026-10-28T04:32:11.530608+00:00 (UTC).

**The extended study is deferred.** Its pending jobs are held; existing full-run outputs are preserved. Pilot inference follows the two full-study tasks that were already running when the pilot was scheduled.

**Pilot:** 50 issues × Qwen/DeepSeek × one seed × four workflows = 400 primary records. 32k token budget and 16 rounds are unchanged. Previously inspected IDs were excluded before outcomes were read. Completed matching predictions are reused.

**Progress:** 400/400 primary records (complete, coverage verified).

[Completed pilot results and interpretation](pilot_results.md). The extended study remains deferred pending output-quality diagnosis.

**By model:** Qwen 200/200; DeepSeek 200/200. Counts show written records; the final report validates full coverage.

[Existing paired comparison](../../experiments/pilot/results/existing-analysis/report.md) uses complete four-workflow issue sets from a completion-selected snapshot. Its exploratory estimates do not establish generalization.

[Interim pilot comparison](../../experiments/pilot/results/interim-analysis/report.md) reports a scheduled snapshot of the fixed 50-issue sample, with incomplete coverage shown explicitly. Latest snapshot: 2026-10-25T01:58:03.730854+00:00; 400/400 records.

[Output-quality review](pilot_quality_review.md) documents the DeepSeek empty-hypothesis and invalid-response diagnostics separately from scheduler health.

[Pilot report](../../experiments/pilot/results/analysis/report.md) contains the final comparison. Per-case scores, descriptive repository bootstrap intervals and completeness metadata are preserved with the reports.

Remote pilot artifacts: `/home/babaei/morph-ufv/pilots/pilot-20261024`.

## Scheduler

```text
No pilot jobs queued or running.
```

## Resume the extended study

The exact held job IDs are recorded remotely in `schedule.json` and `held-jobs.json`. Release those jobs with `scontrol release <job-id>` when ready. Pilot outputs remain separate; new pilot-only predictions must be imported and validated before they can count toward full-study completion.
