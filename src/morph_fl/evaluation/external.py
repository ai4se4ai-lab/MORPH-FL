import json
from pathlib import Path


def import_agentless(source, cases, out):
    public = {
        r["instance_id"]: r
        for r in (json.loads(line) for line in Path(cases).read_text().splitlines() if line.strip())
    }
    rows = []
    for line in Path(source).read_text().splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        case = public[raw["instance_id"]]
        paths = raw["found_files"]
        if not isinstance(paths, list) or not all(
            isinstance(p, str) and not p.startswith("/") and ".." not in Path(p).parts
            for p in paths
        ):
            raise ValueError("Invalid Agentless found_files")
        rows.append(
            dict(
                instance_id=case["instance_id"],
                repo=case["repo"],
                revision=case["revision"],
                ranking=list(dict.fromkeys(paths)),
                variant="agentless_external_unmatched",
                seed=0,
                input_tokens=None,
                output_tokens=None,
                seconds=None,
                resets=None,
                duplicate_probes=None,
                abstained=not paths,
            )
        )
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(r) + "\n" for r in rows))
