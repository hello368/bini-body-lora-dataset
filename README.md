# Bini Body LoRA Production Dataset

Production dataset and review gallery for Bini Body LoRA development.

## Contents

- `datasets/bini_body_selected/`: production Body LoRA training candidates
- `datasets/bini_body_gold/`: manually promoted gold set
- `datasets/bini_body_needs_fix/`: excluded from training
- `datasets/bini_body_rejected/`: excluded from training
- `images/`: final selected gallery images for GitHub Pages
- `captions/`: legacy selected captions
- `training/configs/`: AI Toolkit/Kohya experiment configs
- `training/ai_toolkit/`: AI Toolkit production trainer notes
- `training/kohya/`: Kohya/sd-scripts production trainer notes
- `evaluation/body_lora_tests/`: fixed evaluation prompt set
- `evaluation/comparison_grids/`: checkpoint comparison sheets
- `reviews/`: audit, training, and evaluation reports

## Trigger Strategy

- Face LoRA trigger: `bk_bini_teen`
- Body LoRA trigger: `bk_bini_body`
- Braces/Mobility LoRA trigger: `bk_bini_braces`

Do not use `bk_bini_teen` as the main trigger in Body LoRA captions.

## Production Workflow

1. Keep GitHub as the source of truth.
2. Use ComfyUI for dataset generation, pose-controlled generation, evaluation, contact sheets, and Pages review.
3. Use AI Toolkit or Kohya/sd-scripts on RunPod for actual LoRA training.
4. Train Body LoRA only from `datasets/bini_body_selected/` or manually promoted `datasets/bini_body_gold/`.
5. Do not train on `needs_fix/`, `rejected/`, `datasets/bini_body_needs_fix/`, or `datasets/bini_body_rejected/`.

## Audit

Run before training:

```bash
python3 scripts/audit_bini_dataset.py
```

## Training Experiments

- `bk_bini_body_v1_conservative`
- `bk_bini_body_v1_standard`
- `bk_bini_braces_v1`
