# Five-family model selection (2026-10-20)

The revised study uses exactly five independently trained model families from five
organizations. Exact checkpoint commits and UFV GPU requests are in `pins.json`.
Selection uses published software-engineering evidence and available A30 hardware;
it is not a claim that these are the newest or universally strongest models.

| Family / checkpoint | Evidence and its scope | License |
|---|---|---|
| Alibaba Qwen: `Qwen/Qwen2.5-Coder-7B-Instruct` | COSMosFL explicitly evaluates Qwen2.5-Coder 7B for method-level fault localization on Defects4J. | Apache-2.0 |
| DeepSeek: `deepseek-ai/deepseek-coder-6.7b-instruct` | PInG uses this exact checkpoint for code generation/refinement. MLM4DNN evaluates it in DNN repair without supplied bug locations. This is related repair/debugging evidence, not evidence of widespread standalone file/function-localization use. | DeepSeek model license (custom) |
| Meta CodeLlama: `codellama/CodeLlama-7b-Instruct-hf` | COSMosFL evaluates CodeLlama 7B for fault localization. The PLofLBFL artifact explicitly lists the 7B instruction checkpoint for novice-program localization. | Llama 2 community license (custom) |
| Mistral: `mistralai/Mistral-Nemo-Instruct-2407` (12B) | COSMosFL evaluates Mistral NeMo 12B for fault localization. | Apache-2.0 |
| IBM Granite: `ibm-granite/granite-3.1-8b-instruct` | COSMosFL includes Granite 3.0 8B. We use its 3.1 8B successor because 3.0 has only 4,096 native context tokens; 3.1 supports the common 16,384-token study limit. This is family-level evidence, not evaluation of this exact checkpoint in that paper. | Apache-2.0 |

Primary sources:

- [COSMosFL author paper](https://coinse.github.io/publications/pdfs/Cho2025aa.pdf) and [artifact](https://github.com/coinse/cosmosfl).
- [PLofLBFL author artifact](https://github.com/Xucranger/PLofLBFL).
- [PInG official artifact](https://github.com/NecoraNyaru/PInG).
- [MLM4DNN author paper / publisher](https://doi.org/10.1145/3715716).
- [Granite 3.1 official model card](https://huggingface.co/ibm-granite/granite-3.1-8b-instruct).
- [Mistral NeMo official model card](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407).

All five checkpoints are publicly downloadable without gated access at verification.
They are open-weight models; the custom DeepSeek and Llama licenses must not be
presented as Apache/OSI licenses. Published use establishes relevant research
precedent, not a measured claim that all five checkpoints are widely used for FL.
COSMosFL used different quantization and task conditions; its scores are not ours.

BF16, sampling, seeds, token budgets, workflows and benchmark subjects remain
unchanged. CodeLlama and Mistral NeMo reserve two A30s; the other models reserve
one. Per-model real-inference preflights gate the primary and side studies. The
old three-Qwen design and its outputs remain archived in the original deployment;
its model jobs were cancelled, with only identical benchmark preparation retained.

Runtime tokenizer validation on UFV supports all five native chat templates and
contexts. Mistral NeMo explicitly uses `fix_mistral_regex=True` for Transformers
4.57.6; this correction is pinned and recorded before any five-family inference.
