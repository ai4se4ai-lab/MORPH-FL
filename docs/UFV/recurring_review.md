# Recurring experiment review

The local user timer `morph-fl-review.timer` queues this exact message every
30 minutes in the existing Codex conversation:

> check full experiment and tell me details of this and fix any issues

The entry point is `hpc/ufv/schedule_review.py`. It calls the installed
`codex queue` command with the conversation UUID, preserving the review context.
The timer queues work; acceptance is not proof that the review has finished.
Review results appear in that Codex conversation. The scheduler itself does not
submit experiment jobs or change scientific results.

The user service and timer are installed at:

- `~/.config/systemd/user/morph-fl-review.service`
- `~/.config/systemd/user/morph-fl-review.timer`

The service uses absolute paths for the repository and Codex executable. A lock
prevents overlapping enqueue commands; failed delivery is logged, and delivery
timeouts are not immediately retried because acceptance could be ambiguous.
Status and delivery history are in `hpc/logs/recurring-review/` (ignored by Git).

Inspect the next scheduled run and the latest delivery:

```bash
systemctl --user list-timers morph-fl-review.timer --all
cat hpc/logs/recurring-review/status.json
journalctl --user -u morph-fl-review.service -n 20
```

Stop future deliveries:

```bash
systemctl --user disable --now morph-fl-review.timer
```

Restart the schedule:

```bash
systemctl --user enable --now morph-fl-review.timer
```

Request an additional review immediately:

```bash
systemctl --user start morph-fl-review.service
```

The host, user systemd manager, Codex executable, account login and repository
must remain available. Stopping the timer does not cancel messages already
accepted into the conversation. No separate agent is spawned by this script.

Codex command documentation:
[queue a message in an existing session](https://learn.chatgpt.com/docs/cli/reference#codex-queue).
