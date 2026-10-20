import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hpc.scripts.hpclib import resolve, validate

ROOT = Path(__file__).resolve().parents[2]


class FiveFamilyTests(unittest.TestCase):
    def test_all_five_families_and_complete_resource_matrix(self):
        pins = json.loads((ROOT / 'experiments/full/pins.json').read_text())
        models = pins['models']
        self.assertEqual(len(models), 5)
        self.assertEqual(len({m['family'] for m in models}), 5)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for folder in ('hpc/ufv', 'hpc/config', 'experiments/full'):
                (target / folder).mkdir(parents=True)
            for name in ('hpc/ufv/full_config.py', 'hpc/config/experiments.json', 'experiments/full/pins.json'):
                shutil.copy(ROOT / name, target / name)
            subprocess.run([sys.executable, str(target / 'hpc/ufv/full_config.py')], check=True)
            config = resolve(json.loads((target / 'hpc/config/experiments.json').read_text()), False)
            self.assertFalse(validate(config))
            self.assertEqual(len(config['stages']), 34)
            self.assertEqual(sum(len(s['cells']) for s in config['stages']), 733)
            for index, model in enumerate(models):
                main = next(s for s in config['stages'] if s['name'] == f'main_m{index}')
                self.assertEqual(len(main['cells']), 96)
                self.assertEqual({c['model'] for c in main['cells']}, {index})
                self.assertEqual(main['resources']['gpus'], f"nvidia_a30:{model['ufv_gpus']}")
