"""Offline GPU inference with exact tokenizer-based budget accounting."""

import json


class BudgetExceeded(Exception):
    pass


class InvalidModelResponse(ValueError):
    """A failed structured response whose original generation remains auditable."""

    def __init__(self, message, raw):
        super().__init__(message)
        self.raw = raw


class LocalModel:
    def __init__(self, path, seed):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

        if not torch.cuda.is_available():
            raise RuntimeError("Real inference requires a GPU allocation")
        set_seed(seed)
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            path, local_files_only=True, torch_dtype=torch.bfloat16
        ).to("cuda")
        self.input_tokens = self.output_tokens = 0

    def set_seed(self, seed):
        from transformers import set_seed

        set_seed(seed)

    def ask(self, messages, remaining, max_new=1536):
        import torch

        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        count = inputs.input_ids.shape[1]
        maximum = min(max_new, remaining - count, self.model.config.max_position_embeddings - count)
        if maximum < 64 or count + maximum > self.model.config.max_position_embeddings:
            raise BudgetExceeded()
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=maximum,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = output[0, count:]
        self.input_tokens += count
        self.output_tokens += len(generated)
        text = self.tokenizer.decode(generated, skip_special_tokens=True)
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start : end + 1]), text
