# bk_bini_body_v1_conservative Training Report

Date: 2026-06-23

## Status

- Training status: completed
- Evaluation status: completed
- Dataset audit: errors 0, warnings 0
- Evaluation generation errors: none found in evaluate.log

## Dataset

- Dataset path: `datasets/bini_body_selected/`
- Image count: 100
- Caption count: 100
- Main trigger: `bk_bini_body`
- Excluded folders: `needs_fix/`, `rejected/`, old candidates
- Caption check: 100 captions start with `bk_bini_body`
- Forbidden caption references checked: `bk_bini_teen`, `needs_fix`, `rejected`, `old candidates`

## Training Config

- Experiment: `bk_bini_body_v1_conservative`
- LoRA name: `bk_bini_body_v1_conservative`
- Trigger: `bk_bini_body`
- Rank: 16
- Alpha: 16
- Learning rate: 8e-5
- Resolution: 1024
- Text encoder training: off (`--network_train_unet_only`)
- Save checkpoint every: 250 steps
- Total steps: 1600
- Final average loss: 0.249

## RunPod

- Pod ID: `csy6qel1p70mey`
- GPU: NVIDIA RTX A6000
- Hourly cost: $0.49/hr
- Public URL during run: `https://csy6qel1p70mey-8188.proxy.runpod.net`

## Outputs

- Remote output directory: `/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora/training/outputs/bk_bini_body_v1_conservative/`
- Final LoRA: `/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora/training/outputs/bk_bini_body_v1_conservative/bk_bini_body_v1_conservative.safetensors`
- ComfyUI LoRA copy: `/workspace/flux-lora/ComfyUI/models/loras/bk_bini_body/bk_bini_body_v1_conservative.safetensors`
- Step checkpoint: `bk_bini_body_v1_conservative-step00001500.safetensors`
- Checkpoints saved: 2

The `.safetensors` files are not committed to GitHub.

## Evaluation

- Evaluation output: `evaluation/bk_bini_body_v1_conservative/`
- Evaluation images: 30
- Evaluation prompts: 30 matching `.txt` files
- Contact sheet: `contact_sheets/bk_bini_body_v1_conservative_eval.jpg`
- Evaluation trigger stack: `bk_bini_teen` + `bk_bini_body`

## Notes

- Conservative training was run first only. Standard and braces experiments were not started.
- The production dataset uses selected images only.
- `needs_fix/`, `rejected/`, and old candidate images were not used for training.
