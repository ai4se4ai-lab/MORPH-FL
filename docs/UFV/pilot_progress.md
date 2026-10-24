# Fast pilot progress

Updated: 2026-10-24T21:00:01.739216+00:00 (UTC).

**The extended study is deferred.** Its pending jobs are held; existing full-run outputs are preserved. Pilot inference follows the two full-study tasks that were already running when the pilot was scheduled.

**Pilot:** 50 issues × Qwen/DeepSeek × one seed × four workflows = 400 primary records. 32k token budget and 16 rounds are unchanged. Previously inspected IDs were excluded before outcomes were read. Completed matching predictions are reused.

**Progress:** 176/400 primary records (coverage not yet complete).

[Existing paired comparison](../../experiments/pilot/results/existing-analysis/report.md) uses complete four-workflow issue sets from a completion-selected snapshot. Its exploratory estimates do not establish generalization.

[Interim pilot comparison](../../experiments/pilot/results/interim-analysis/report.md) reports a scheduled snapshot of the fixed 50-issue sample, with incomplete coverage shown explicitly.

[Pilot report](../../experiments/pilot/results/analysis/report.md) appears after inference. Per-case scores, descriptive repository bootstrap intervals and completeness metadata are preserved with the reports.

Remote pilot artifacts: `/home/babaei/morph-ufv/pilots/pilot-20261024`.

## Scheduler

```text
18107|morph-pilot-report|PENDING|(Dependency)
18106_0|morph-pilot-m1|PENDING|(Dependency)
18106_1|morph-pilot-m1|PENDING|(Dependency)
18106_2|morph-pilot-m1|PENDING|(Dependency)
18106_3|morph-pilot-m1|PENDING|(Dependency)
18106_4|morph-pilot-m1|PENDING|(Dependency)
18106_5|morph-pilot-m1|PENDING|(Dependency)
18106_6|morph-pilot-m1|PENDING|(Dependency)
18106_7|morph-pilot-m1|PENDING|(Dependency)
18106_9|morph-pilot-m1|PENDING|(Dependency)
18106_11|morph-pilot-m1|PENDING|(Dependency)
18106_12|morph-pilot-m1|PENDING|(Dependency)
18106_13|morph-pilot-m1|PENDING|(Dependency)
18106_14|morph-pilot-m1|PENDING|(Dependency)
18106_15|morph-pilot-m1|PENDING|(Dependency)
18106_17|morph-pilot-m1|PENDING|(Dependency)
18106_18|morph-pilot-m1|PENDING|(Dependency)
18106_19|morph-pilot-m1|PENDING|(Dependency)
18106_20|morph-pilot-m1|PENDING|(Dependency)
18106_21|morph-pilot-m1|PENDING|(Dependency)
18106_22|morph-pilot-m1|PENDING|(Dependency)
18106_24|morph-pilot-m1|PENDING|(Dependency)
18106_25|morph-pilot-m1|PENDING|(Dependency)
18106_26|morph-pilot-m1|PENDING|(Dependency)
18106_27|morph-pilot-m1|PENDING|(Dependency)
18106_29|morph-pilot-m1|PENDING|(Dependency)
18106_31|morph-pilot-m1|PENDING|(Dependency)
18105_31|morph-pilot-m0|RUNNING|node2
18105_27|morph-pilot-m0|RUNNING|node2
```

## Resume the extended study

The exact held job IDs are recorded remotely in `schedule.json` and `held-jobs.json`. Release those jobs with `scontrol release <job-id>` when ready. Pilot outputs remain separate; new pilot-only predictions must be imported and validated before they can count toward full-study completion.
