# Bini Body LoRA Training Report

## Production Training Policy

GitHub is the source of truth. ComfyUI is used for dataset generation, pose-controlled generation, evaluation images, contact sheets, and GitHub Pages review. Production LoRA training should run through AI Toolkit or Kohya/sd-scripts on RunPod.

## Trigger Strategy

- Face LoRA trigger: `bk_bini_teen`
- Body LoRA trigger: `bk_bini_body`
- Braces/Mobility LoRA trigger: `bk_bini_braces`

Do not use `bk_bini_teen` as the main trigger in Body LoRA captions.

## Experiments

| Experiment | Trigger | Dataset | Rank | Alpha | Steps | Text Encoder | Resolution |
| --- | --- | --- | ---: | ---: | --- | --- | ---: |
| `bk_bini_body_v1_conservative` | `bk_bini_body` | `datasets/bini_body_selected/` | 16 | 16 | 1200-1600 | off | 1024 |
| `bk_bini_body_v1_standard` | `bk_bini_body` | `datasets/bini_body_selected/` | 32 | 32 | 1800-2400 | off initially | 1024 |
| `bk_bini_braces_v1` | `bk_bini_braces` | visible braces/crutches subset | 16 or 32 | 16 or 32 | 1200-1800 | off | 1024 |

## Exclusions

Never train from:

- `needs_fix/`
- `rejected/`
- `datasets/bini_body_needs_fix/`
- `datasets/bini_body_rejected/`
- old candidate folders

## Current Status

Configuration scaffold is prepared. Run `python3 scripts/audit_bini_dataset.py` before launching any production training job.

