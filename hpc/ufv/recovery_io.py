"""Read only /proc metadata for the active retrieval recovery; run on its node."""
import json
import os
from pathlib import Path


def inspect_process(proc, results):
    """Identify the exact run and distinguish checkpoint compaction from a read scan."""
    expected = str(Path(results)/'predictions/retrieval__m0__s1__p0.jsonl')
    try:
        args = (proc/'cmdline').read_bytes().split(b'\0')
        args = [v.decode(errors='replace') for v in args if v]
        if not ('experiments.full.suite' in args and '--results' in args and '--track' in args):
            return None
        if args[args.index('--results')+1] != str(results) or args[args.index('--track')+1] != 'retrieval':
            return None
        reader = writer = None
        size = 0
        for fd in (proc/'fd').iterdir():
            try:
                target = os.readlink(fd)
                fields = dict(line.split(':',1) for line in (proc/'fdinfo'/fd.name).read_text().splitlines() if ':' in line)
                position = int(fields.get('pos','0').strip())
                if target == expected:
                    reader = position
                    size = fd.stat().st_size
                elif target.startswith(expected+'.') and target.endswith('.tmp'):
                    writer = position
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
        rss = next((line.split(':',1)[1].strip() for line in (proc/'status').read_text().splitlines() if line.startswith('VmRSS:')), None)
        result = dict(pid=int(proc.name), phase='COMPACTING' if writer is not None else 'CHECKPOINT READ / RESUME',
                      memory_rss=rss, processed_bytes=reader, source_bytes=size)
        if writer is not None and reader is not None and size:
            result.update(fraction=min(1, reader/size), compact_output_bytes=writer)
        return result
    except (FileNotFoundError, PermissionError, ProcessLookupError, IndexError):
        return None


def inspect_node(results):
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
        except FileNotFoundError:
            continue
        result = inspect_process(proc, results)
        if result:
            return result
    return dict(phase='No matching retrieval process observed')


if __name__ == '__main__':
    print(json.dumps(inspect_node('/home/babaei/morph-ufv/runs/ufv-full-v12-20261020-01/results')))
