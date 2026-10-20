"""Split full arrays by model so small checkpoints reserve only one A30."""
import copy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
path = root / 'hpc/config/experiments.json'
config = json.loads(path.read_text())
heavy = {'model_preflight', 'main', 'ablations', 'budgets', 'misdirection', 'policy'}
if not any(s['name'] in heavy for s in config['stages']):
    raise SystemExit('Full configuration already split; refusing to rewrite it')
names = {s['name']: [s['name'] + '_m' + str(i) for i in range(4)]
         if s['name'] in heavy else [s['name']] for s in config['stages']}
stages = []
for source in config['stages']:
    clones = range(4) if source['name'] in heavy else [None]
    for model in clones:
        stage = copy.deepcopy(source)
        stage['depends'] = [dict(stage=name, type=d.get('type', 'afterok'))
                            for d in source.get('depends', []) for name in names[d['stage']]]
        if model is not None:
            stage['name'] = names[source['name']][model]
            stage.pop('matrix_from', None)
            stage['array_throttle'] = 1 if model in (1, 2) else 2
            stage['matrix'] = dict(stage.get('matrix', {}), model=[model])
            stage['resources'].update(gpus='nvidia_a30:3' if model in (1, 2) else 'nvidia_a30:1',
                                      mem='88G' if model in (1, 2) else '40G')
            if model:
                stage['depends'].append(dict(stage=names[source['name']][model - 1], type='afterany'))
        stages.append(stage)
config['stages'] = stages
path.write_text(json.dumps(config, indent=2) + '\n')
