"""Pinned, native Transformers backend for the prospective BF16 HPC study.

Separate from the historical Ollama/BF16 adapters: no historical result is relabeled.
Both structured and free-text workflows share the same weights and sampling.
"""

import json
import os
from types import SimpleNamespace

from morph_fl.inference.local import BudgetExceeded


def decode_object(text):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char == "{":
            try:
                value, _ = decoder.raw_decode(text[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    raise ValueError("No valid JSON object in generated output")


class NativeModel:
    def __init__(self, path, spec, seed=1, context=16384, temperature=0.2):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if not torch.cuda.is_available():
            raise RuntimeError("HPC inference requires an allocated GPU")
        self.hf_tokenizer = AutoTokenizer.from_pretrained(
            path, local_files_only=True, **spec.get("tokenizer_kwargs", {})
        )
        placement = {}
        if os.environ.get("MORPH_MULTI_GPU") == "1" and torch.cuda.device_count() > 1:
            placement = dict(
                device_map="auto",
                max_memory={i: "22GiB" for i in range(torch.cuda.device_count())},
            )
        self.model = AutoModelForCausalLM.from_pretrained(
            path,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
            low_cpu_mem_usage=True,
            **placement,
        )
        if not placement:
            self.model = self.model.to("cuda")
        self.model.eval()
        if self.model.config.max_position_embeddings < context:
            raise RuntimeError("Model native context is below the common study context")
        self.context = context
        self.temperature = temperature
        self.input_tokens = self.output_tokens = 0
        self.text_mode = False
        self.metadata = dict(
            **spec,
            backend="transformers",
            dtype="bfloat16",
            context=self.context,
            temperature=temperature,
            output_limit=1536,
            top_p=0.95,
            top_k=50,
            json_constraint=False,
            gpu_names=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            device_map={k: str(v) for k, v in getattr(self.model, "hf_device_map", {}).items()},
        )
        # The pinned upstream adapter expects tokenizers' .encode(...).ids API.
        self.tokenizer = SimpleNamespace(
            encode=lambda value, **kw: SimpleNamespace(ids=self.hf_tokenizer.encode(value, **kw))
        )
        self.set_seed(seed)
        if any(parameter.device.type != "cuda" for parameter in self.model.parameters()):
            raise RuntimeError("Model parameters are not fully resident on GPU")

    def set_seed(self, seed):
        from transformers import set_seed

        set_seed(seed)

    def render(self, messages):
        return self.hf_tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

    def ask(self, messages, remaining, max_new=1536):
        import torch

        inputs = self.hf_tokenizer(
            self.render(messages), return_tensors="pt", add_special_tokens=False
        ).to("cuda")
        count = inputs.input_ids.shape[1]
        maximum = min(max_new, remaining - count, self.context - count)
        if maximum < 64:
            raise BudgetExceeded("Context or cumulative token limit")
        with torch.inference_mode():
            result = self.model.generate(
                **inputs,
                max_new_tokens=maximum,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=self.temperature,
                pad_token_id=self.hf_tokenizer.eos_token_id,
            )
        generated = result[0, count:]
        self.input_tokens += count
        self.output_tokens += len(generated)
        text = self.hf_tokenizer.decode(generated, skip_special_tokens=True)
        return ({"text": text} if self.text_mode else decode_object(text)), text
