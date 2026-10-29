#!/bin/bash
set -euo pipefail
root="${UFV_REPO_DIR:?Submit with --export=ALL,UFV_REPO_DIR=deployment_path}"
runtime=/home/babaei/morph-ufv/runtime
validation_dir=/tmp/morph-validate-$SLURM_JOB_ID
mkdir -p "$validation_dir/packages"
trap 'rm -rf "$validation_dir"' EXIT
tar -xf "$runtime/packages.tar" -C "$validation_dir/packages"
export SINGULARITYENV_PYTHONPATH="$root:$root/src:$validation_dir/packages"
singularity exec --nv --bind /home,/tmp "$runtime/pytorch.sif" /opt/conda/bin/python -c 'import torch, transformers; print("torch", torch.__version__, "cuda", torch.version.cuda, "transformers", transformers.__version__); print("GPU",torch.cuda.get_device_name(0),"BF16",torch.cuda.is_bf16_supported()); assert torch.cuda.is_available() and torch.cuda.is_bf16_supported()'
cd "$root"
singularity exec --nv --bind /home,/tmp "$runtime/pytorch.sif" /opt/conda/bin/python -m unittest tests.unit.test_full_study.FullStudyTests tests.unit.test_full_study.PaperPromotionTests tests.unit.test_full_study.FullAnalysisTests tests.unit.test_full_study.ProgressDenominatorTests tests.unit.test_full_study.FullContinuationTests tests.unit.test_full_inference_placement tests.unit.test_hpc_audit

export SINGULARITYENV_HF_HOME=/home/babaei/morph-ufv/cache/huggingface
singularity exec --nv --bind /home,/tmp "$runtime/pytorch.sif" /opt/conda/bin/python "$root/hpc/ufv/check_tokenizers.py" --out "$root/hpc/logs/fivefam-tokenizers.json"
