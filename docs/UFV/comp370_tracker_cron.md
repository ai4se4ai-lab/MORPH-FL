# Independent tracker on comp370

Installed and verified on October 20, 2026. The Codex workspace is already on
**comp370**, at `/home/majid/projects/MORPH-FL`; there is no separate local/server
checkout to synchronize in this setup. Windows, VS Code, SSH sessions and this
chat can disconnect without stopping cron.

The `majid` user crontab contains:

```cron
*/30 * * * * /bin/bash /home/majid/projects/MORPH-FL/hpc/ufv/cron_tracker.sh # MORPH-FL study tracker
```

Checks and document publications occur at minutes **00 and 30** of every hour.
The machine timezone controls cron; document timestamps are UTC. Each invocation
makes one check, logs incidents, refreshes the document, and exits. `flock`
prevents overlap. A check that observes terminal jobs also collects compact final
artifacts. Later invocations continue checking; remove the entry when monitoring
is no longer needed. The former continuous monitor was stopped to avoid duplicate
polls and history writers. The wrapper respects the one-minute scheduler polling
limit when manually invoked immediately after another check.

## Files and operation

- Document: `/home/majid/projects/MORPH-FL/docs/UFV/study_progress.md`.
- Wrapper: `hpc/ufv/cron_tracker.sh`; single-check implementation: `watch_collect.py --once`.
- Snapshot/status/history/log: `hpc/logs/ufv-full-v12-20261020/` (`study-progress.json`, `status.json`, `tracker-history.json`, `monitor.log`).
- Previous crontab backup: `hpc/logs/ufv-full-v12-20261020/crontab.before-tracker.txt`. Other cron entries were preserved.
- Cron service was verified active; Python 3.14.4 and `/usr/bin/flock` are available.

A dedicated SSH identity, `~/.ssh/ufv_tracker_ed25519`, was generated on comp370.
Its public key is authorized with `restrict` on the Slurm `babaei` account;
`~/.ssh/config` selects it for `slurm.soc.ufv.ca`. Its private key remains on
comp370. Password-free access was verified without a forwarded agent. Tracker
setup does not modify the frozen experiment deployment or Slurm jobs.

Inspect or run manually:

```bash
crontab -l
systemctl is-active cron
bash /home/majid/projects/MORPH-FL/hpc/ufv/cron_tracker.sh
tail -n 20 /home/majid/projects/MORPH-FL/hpc/logs/ufv-full-v12-20261020/monitor.log
```

Cron survives logout and restarts with the server's cron service. Comp370 must
remain powered on and able to reach Slurm. Connection failures preserve the last
successful remote snapshot, are recorded as incidents, and retry next time.
Failure detection is now every **30 minutes**, rather than the former continuous
monitor's one-minute checks. Slurm accounting is disabled on UFV, which limits
scheduler-only failure visibility; step failures and available logs are retained.

Final collection excludes large graph/evidence archives retained on UFV. The
server currently has about 31 GB free; collection can fail if available space is
insufficient, in which case inspect the incident and log before retrying.

## October 20 runtime recovery

A temporary five-minute cron callback now checks the retrieval recovery receipt
and restores the stopped experiment graph only after exact full retrieval
coverage is established. It removes its own cron entry after successful
submission; the ordinary 30-minute reporting schedule remains. See the
[repair report](runtime_recovery_20261020.md) for the source manifest, stopped
jobs, preserved results and verification evidence.


At **19:17 UTC on October 20**, retrieval recovery completed and all 26 remaining
stages were submitted. The temporary recovery callback removed its own entry;
only the regular 30-minute tracker cron remains. Retrieval receipt: 1,414 records;
new primary arrays: 17980–17984; new final collection: 18007.
