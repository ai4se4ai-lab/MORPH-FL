"""Validate each pinned family's native context and multi-turn chat interface."""
import argparse
import json
from pathlib import Path

from transformers import AutoConfig, AutoTokenizer

p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
models = json.loads((root / 'experiments/full/pins.json').read_text())['models']
checks = []
messages = [dict(role='system', content='Return localization hypotheses as JSON.'),
            dict(role='user', content='Locate the fault in a Python function.'),
            dict(role='assistant', content='{"hypotheses": []}'),
            dict(role='user', content='Consider the next observation.')]
for spec in models:
    config = AutoConfig.from_pretrained(spec['id'], revision=spec['revision'])
    if config.max_position_embeddings < 16384:
        raise ValueError('Insufficient native context: ' + spec['id'])
    tokenizer = AutoTokenizer.from_pretrained(
        spec['id'], revision=spec['revision'], **spec.get('tokenizer_kwargs', {})
    )
    rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    if not rendered or len(tokenizer.encode(rendered)) < 5:
        raise ValueError('Empty chat rendering: ' + spec['id'])
    checks.append(dict(model=spec['id'], revision=spec['revision'], native_context=config.max_position_embeddings, multi_turn=True, tokenizer_kwargs=spec.get('tokenizer_kwargs', {})))
    print(json.dumps(checks[-1]), flush=True)
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(json.dumps(dict(checks=checks, complete=True), indent=2)+'\n')
