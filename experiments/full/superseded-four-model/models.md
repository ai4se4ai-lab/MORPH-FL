# Prospective model selection, verified 2026-10-19

Models are pinned in `pins.json`. Nibi uses original instruction checkpoints in BF16, **not Ollama quantizations**. Names alone are not evidence of a best model. The aim is two competitive dense/MoE code configurations, continuity with the pilot, and an independent-family historical control.

| Checkpoint | Role | Verified SE-study evidence | Limits of the evidence |
|---|---|---|---|
| Qwen/Qwen2.5-Coder-7B-Instruct | Small code-model/pilot continuity | [PROBE, EMSE 2026](https://doi.org/10.1007/s10664-026-10904-5) evaluates Qwen2.5-Coder 7B and 14B. | Code generation study; its quantization/settings are not ours. |
| Qwen/Qwen2.5-Coder-32B-Instruct | Strong dense code model | [FLAMES author paper, ICSE 2026](https://rest.mars-prod.its.unimelb.edu.au/server/api/core/bitstreams/90394387-3965-45fb-91da-d0d1c78da479/content) includes Qwen2.5-Coder-32B in program-repair comparisons; [ICSE 2026 interoperability study](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/209/Evaluating-the-effectiveness-of-LLM-based-interoperability) uses qwen2.5-coder:32b. | Different SE tasks; no claim that their success transfers to fault localization. |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | Newer MoE code configuration | [Falcão and Canedo, EMSE 31:184 (2026)](https://doi.org/10.1007/s10664-026-10919-y) includes qwen3-coder:30b-a3b-q4_K_M. | PII detection study, not fault localization; BF16 here differs from its quantization. |
| deepseek-ai/deepseek-coder-6.7b-instruct | Historical cross-family control | [PInG official ICSE 2025 artifact](https://github.com/NecoraNyaru/PInG) explicitly runs this checkpoint for code generation/refinement. | Not presented as a top current model; intentionally tests family robustness. |

No unverified TSE attribution is made. The user-supplied `docs/ollama-se.txt` is a candidate list, not verified venue evidence. StarCoder2 and base/completion checkpoints are omitted because this experiment needs instruction dialogues; Devstral is a reasonable follow-up but would add a fifth checkpoint and another tokenizer/runtime preflight. Its use in the same EMSE PII study does not establish superiority for this task.
