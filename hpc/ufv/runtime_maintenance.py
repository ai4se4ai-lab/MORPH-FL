"""Validate explicitly recorded runtime repairs without changing the scientific protocol."""
import hashlib
import json
from pathlib import Path


def digest(path):
    checksum = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(chunk)
    return checksum.hexdigest()


def verify_sources(root, spec):
    root = Path(root)
    path = root / 'experiments/full/runtime_maintenance.json'
    maintenance = json.loads(path.read_text()) if path.exists() else None
    if maintenance:
        if maintenance['protocol_sha256'] != digest(root / 'experiments/full/protocol.json'):
            raise ValueError('Maintenance protocol identity differs')
        for relative, change in maintenance['files'].items():
            if change.get('original_sha256') != spec['source_files'].get(relative):
                raise ValueError('Maintenance original identity differs: ' + relative)
            if digest(root / relative) != change['sha256']:
                raise ValueError('Maintenance source differs: ' + relative)
    for relative, expected in spec['source_files'].items():
        change = (maintenance or {}).get('files', {}).get(relative)
        if digest(root / relative) != (change['sha256'] if change else expected):
            raise ValueError('Frozen source differs: ' + relative)
    return maintenance
