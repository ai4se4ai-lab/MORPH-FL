"""Placement must preserve BF16 and reject any silent CPU/disk offload."""
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from experiments.full.inference import NativeModel


class PlacementTests(unittest.TestCase):
    def load(self, count, devices):
        model = MagicMock()
        model.config.max_position_embeddings = 16384
        model.parameters.return_value = [SimpleNamespace(device=SimpleNamespace(type=d)) for d in devices]
        model.to.return_value = model
        model.hf_device_map = {'layers': 0}
        loader = MagicMock(return_value=model)
        cuda = SimpleNamespace(is_available=lambda: True, device_count=lambda: count,
                               get_device_name=lambda i: 'A30')
        torch = SimpleNamespace(cuda=cuda, bfloat16='bf16')
        transformers = SimpleNamespace(AutoModelForCausalLM=SimpleNamespace(from_pretrained=loader),
                                       AutoTokenizer=MagicMock(), set_seed=MagicMock())
        with patch.dict(sys.modules, torch=torch, transformers=transformers):
            NativeModel('/weights', {})
        return loader, model

    @patch.dict(os.environ, MORPH_MULTI_GPU='1')
    def test_shards_without_changing_precision(self):
        loader, model = self.load(3, ['cuda', 'cuda'])
        self.assertEqual(loader.call_args.kwargs['device_map'], 'auto')
        self.assertEqual(loader.call_args.kwargs['torch_dtype'], 'bf16')
        self.assertEqual(len(loader.call_args.kwargs['max_memory']), 3)
        model.to.assert_not_called()

    @patch.dict(os.environ, MORPH_MULTI_GPU='1')
    def test_rejects_cpu_offload(self):
        with self.assertRaisesRegex(RuntimeError, 'fully resident'):
            self.load(3, ['cuda', 'cpu'])

    @patch.dict(os.environ, MORPH_MULTI_GPU='0')
    def test_original_single_gpu_placement(self):
        loader, model = self.load(1, ['cuda'])
        self.assertNotIn('device_map', loader.call_args.kwargs)
        model.to.assert_called_once_with('cuda')
