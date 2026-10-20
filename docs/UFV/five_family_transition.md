# Five-family protocol revision — 2026-10-20

User request: replace three Qwen checkpoints with five models from five distinct
families, prioritizing established software-engineering and fault-localization use.

The original run am-20261019-191308 is superseded. Its model jobs were cancelled;
only identical pinned benchmark preparation job 17836 continues for reuse. The
original deployment, downloaded models, smoke outputs, protocol and logs remain
archived. No full primary inference result had been used to choose the new models.

New run: ufv-fivefam-20261020-01, 34 submissions, 733 cells; collect job 17901.
New isolated deployment: /home/babaei/projects/MORPH-FL-ufv-fivefam-20261020.
The local protocol, pins, model matrices, native-context guard, GPU allocation and
result-export completeness guard now cover the five selected model families.

See experiments/full/models.md for primary-source evidence, licenses and explicit
limits of exact-checkpoint versus family-level fault-localization evidence.
Granite 3.1 replaces the initially considered Granite 3.0 because the latter's
4,096 native context tokens cannot support the common 16,384-token study limit.

The previous smoke remains runtime evidence. All five models have mandatory real
inference gates in the new graph; new-family success is not presumed.

The tokenizer-only check found the Transformers Mistral regex warning.
`fix_mistral_regex=True` is now pinned for Mistral before any new-family inference.
The pre-correction manifest/protocol are preserved, and the final protocol/model
selection are copied into the run config and result tree.
