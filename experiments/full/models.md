# Five-family model selection (2026-10-20)

The user requested five distinct families before any inference in the superseded four-model full run. That run's pending experiment jobs were cancelled; its completed setup and original protocol remain preserved. Exact checkpoint revisions are in `pins.json`. All five run native BF16 instruction checkpoints, not Ollama quantizations, under identical budgets and three seeds. This is a family-diversity comparison, not a claim to select the five strongest contemporary models.

| Family | Pinned checkpoint | Evidence and qualification |
|---|---|---|
| Qwen | Qwen/Qwen2.5-Coder-7B-Instruct | COSMosFL evaluates Qwen2.5-Coder 7B for fault localization. PROBE (EMSE 2026) also evaluates the code-model family. |
| DeepSeek | deepseek-ai/deepseek-coder-6.7b-instruct | PInG's ICSE 2025 artifact explicitly uses this instruction checkpoint for code generation/refinement. Direct localization evidence is weaker than for the other families. |
| CodeLlama | codellama/CodeLlama-7b-Instruct-hf | COSMosFL evaluates CodeLlama 7B in its preliminary fault-localization comparison. Its study uses Ollama 4-bit weights; BF16 instruction-checkpoint equivalence is not claimed. |
| Mistral | mistralai/Mistral-Nemo-Instruct-2407 | COSMosFL evaluates Mistral NeMo 12B and includes it in its final localization ensemble. Quantization and task setup differ here. |
| IBM Granite | ibm-granite/granite-3.1-8b-instruct | COSMosFL evaluates Granite **3.0** 8B, not this 3.1 successor. Family-level localization evidence supports inclusion; exact-checkpoint FL evidence is not established. |

Primary sources: [COSMosFL author manuscript, Section III-B](https://coinse.github.io/publications/pdfs/Cho2025aa.pdf), [PInG official artifact](https://github.com/NecoraNyaru/PInG), [PROBE EMSE](https://doi.org/10.1007/s10664-026-10904-5).

COSMosFL studies seven SLMs on 353 Defects4J bugs. Its final ensemble contains four models, including two Llama versions; we use five distinct families on SWE-bench localization instead. One study establishes precedent, not widespread adoption of every checkpoint. Granite 3.1 is an explicit successor substitution. No unverified TSE/EMSE/ICSE venue attribution is made for COSMosFL.

These are open-weight checkpoints. Qwen, Mistral NeMo and Granite list Apache-2.0 licenses; CodeLlama lists the Llama 2 community license and DeepSeek uses its model license. They should not collectively be described as OSI-approved open-source models. Each selected repository is publicly downloadable without a gated HF access workflow at verification time.

The native chat template and native context cap are recorded by the inference backend. Every new checkpoint must pass the GPU-residency and valid-hypothesis preflight before benchmark inference is released. Failure is reported rather than silently replacing a model or converting missing hypotheses into successful localization.
