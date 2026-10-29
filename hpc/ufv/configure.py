"""Configure an isolated deployment for UFV; preserves the study's BF16 conditions."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
path = root / 'hpc/config/experiments.json'
config = json.loads(path.read_text())
config['project'] = 'morph-ufv'
heavy = {'model_preflight', 'main', 'ablations', 'budgets', 'misdirection', 'policy'}
for stage in config['stages']:
    resources = stage['resources']
    resources.update(gpus='nvidia_a30:3' if stage['name'] in heavy else 'nvidia_a30:1', partition='main', mem='88G' if stage['name'] in heavy else '16G')
    stage['array_throttle'] = 1
    if stage['name'] == 'data':
        stage['steps'] = [s for s in stage['steps'] if s['name'] != 'typeset_preflight']
    if stage['name'] == 'collect':
        stage['steps'] = [s for s in stage['steps'] if s['name'] not in {'paper_export', 'compile_paper'}]
config['smoke']['resources'] = {name: dict(gpus='nvidia_a30:1', cpus=4, mem='32G') for name in heavy}
config['smoke']['time'] = '02:00:00'
path.write_text(json.dumps(config, indent=2) + '\n')
(root / 'hpc/config/cluster.env').write_text('''ACCOUNT=babaei
MAIL_TYPE=NONE
MAX_REQUEUES=2
REQUEUE_SIGNAL_SECS=60
MODULES=""
SRC_DIRS=src
CODE_HASH_DIRS="src tests hpc/scripts experiments/full hpc/ufv"
WORK=/home/babaei/morph-ufv
RESULTS_DEST=""
GPU_MONITOR_SECS=60
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export HF_HOME="$WORK/cache/huggingface"
export XDG_CACHE_HOME="$WORK/cache"
export PIP_CACHE_DIR="$WORK/cache/pip"
export MORPH_MULTI_GPU=1
''')
protocol_path = root / 'experiments/full/protocol.json'
protocol = json.loads(protocol_path.read_text())
protocol.update(runtime_libcst='1.8.6', deployment_hardware='UFV A30 24GB; model-specific one/two GPU BF16 placement from pins.json')
protocol_path.write_text(json.dumps(protocol, indent=2) + '\n')
# UFV requires --gres rather than --gpus.
submit = root / 'hpc/slurm/submit.py'
submit.write_text(submit.read_text().replace('f"--gpus={r[\'gpus\']}"', 'f"--gres=gpu:{r[\'gpus\']}"'))
common = root / 'hpc/slurm/common.sh'
text = common.read_text()
start = text.index('    module purge', text.index('setup_python()'))
end = text.index('    pip freeze', start)
text = text[:start] + '''    export PYTHONPATH="$UFV_PACKAGES${PYTHONPATH:+:$PYTHONPATH}"
''' + text[end:]
common.write_text(text)
# Wrap the ordinary stage script in the immutable container runtime.
stage = root / 'hpc/slurm/stage.sh'
original = stage.with_name('stage-container.sh')
if not original.exists():
    stage.rename(original)
stage.write_text((root / 'hpc/ufv/stage.sh').read_text())
# The generic continuation takes its account from this site's configuration.
continuation = root / 'hpc/scripts/continue_full.py'
continuation.write_text(continuation.read_text().replace('"def-mbabaei_gpu",', '"babaei",').replace('    command = [', '    subprocess.run([sys.executable, str(hpc / "ufv/full_config.py")], check=True)\n    command = ['))
