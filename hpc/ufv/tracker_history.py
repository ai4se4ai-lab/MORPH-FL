"""Persistent publication history and diagnostic incidents for the study tracker."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def summary(state):
    tracker = state.get('tracker', {})
    return dict(records={k: v.get('completed', 0) for k, v in tracker.get('progress', {}).items()
                         if not k.startswith('preflight__')},
                stages={v['name']: [v.get('successful_steps', 0), len(v.get('failures', []))]
                        for v in tracker.get('stages', [])},
                receipts={k: [v.get('complete'), v.get('records')] for k, v in tracker.get('receipts', {}).items()},
                active=state.get('active'), completeness=tracker.get('completeness'),
                collected_locally=state.get('collected_locally'),
                analysis=tracker.get('analysis_overviews', {}),
                status_labels='Active single-cell replacement attempts are labeled RECOVERY RUNNING; historical failures retained.',
                maintenance=tracker.get('runtime_maintenance'),
                recovery=tracker.get('maintenance_recovery'),
                recovery_io=state.get('recovery_io'))


def refresh(state, output, history_path, *, now=None, force=False, monitor_error=None):
    """Observe incidents every poll; publish at 30 minutes, or on explicit/final refresh."""
    try:
        from .study_tracker import render_document
    except ImportError:
        from study_tracker import render_document
    now = now or utc_now()
    history_path, output = Path(history_path), Path(output)
    history = json.loads(history_path.read_text()) if history_path.exists() else dict(refreshes=[], failures={})
    failures = history['failures']
    tracker = state.get('tracker', {})
    events = list(tracker.get('failure_events', []))
    for error in tracker.get('errors', []):
        events.append(dict(kind='metadata', detail=error))
    if monitor_error:
        events.append(dict(kind='monitor', detail=monitor_error,
                           log=str(history_path.parent / 'monitor.log')))
    current = set()
    for event in events:
        key = hashlib.sha256(json.dumps([state['run'], {k: v for k, v in event.items() if k not in ('resolved', 'tail')}], sort_keys=True).encode()).hexdigest()[:16]
        current.add(key)
        if key not in failures:
            failures[key] = dict(id=key, run=state['run'], first_seen=now, **event)
        failures[key].update({k: v for k, v in event.items() if k != 'tail' or not failures[key].get('tail')})
        failures[key]['last_seen'] = now
        failures[key]['status'] = 'RESOLVED (later successful step)' if event.get('resolved') else 'OPEN'
    # A failed poll cannot establish that remote incidents recovered.
    if not monitor_error:
        for key, incident in failures.items():
            if incident.get('run') == state['run'] and key not in current and incident.get('kind') in ('monitor', 'metadata'):
                incident['status'] = 'RESOLVED (successful subsequent poll)'
    previous_time = history['refreshes'][-1]['utc'] if history['refreshes'] else None
    elapsed = (datetime.fromisoformat(now.replace('Z', '+00:00')) - datetime.fromisoformat(previous_time.replace('Z', '+00:00'))).total_seconds() if previous_time else 1800
    publish = bool(tracker) and (force or elapsed >= 1800 or not output.exists())
    if publish:
        current_summary = summary(state)
        old = history.get('summary', {})
        changes = []
        if not old:
            changes.append('Initial tracked refresh; previous document refresh history was not recorded.')
        else:
            before, after = sum(old.get('records', {}).values()), sum(current_summary['records'].values())
            changes.append(f'Study records {before:,} → {after:,} ({after-before:+,}).')
            for category in ('stages', 'receipts', 'active', 'completeness', 'collected_locally', 'analysis', 'maintenance', 'recovery', 'status_labels', 'recovery_io'):
                if old.get(category) != current_summary.get(category):
                    if isinstance(current_summary[category], dict):
                        changed = sorted(k for k in set(old.get(category) or {}) | set(current_summary[category])
                                         if (old.get(category) or {}).get(k) != current_summary[category].get(k))
                        changes.append(category + ': ' + ', '.join(changed) + '.')
                    else:
                        changes.append(category + ': ' + str(current_summary[category]) + '.')
        incident_state = {k: v['status'] for k, v in failures.items()}
        changed_incidents = [k for k, v in incident_state.items() if history.get('incident_state', {}).get(k) != v]
        if changed_incidents:
            changes.append('New/changed failure records: ' + ', '.join(changed_incidents) + '.')
        if monitor_error:
            changes.append('Remote refresh failed; phase table retains last successful snapshot.')
        entry = dict(utc=now, run=state['run'], snapshot_utc=state.get('checked_utc'),
                     changes=' '.join(changes), reason=('Final collection' if state.get('collected_locally') else 'Cron 30-minute refresh' if state.get('monitor_mode') == 'cron' else 'Explicit refresh') if force else 'Scheduled 30-minute refresh')
        history['refreshes'].append(entry)
        history['summary'], history['incident_state'] = current_summary, incident_state
        rendered = dict(state, publication=dict(utc=now, history_path=str(history_path), **history))
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = output.with_suffix(output.suffix + '.tmp')
        tmp.write_text(render_document(rendered))
        tmp.replace(output)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = history_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(history, indent=2) + '\n')
    tmp.replace(history_path)
    return publish
