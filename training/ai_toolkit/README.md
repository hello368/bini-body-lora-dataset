# AI Toolkit Training

Use AI Toolkit as a production trainer for FLUX LoRA experiments. ComfyUI is reserved for dataset generation, evaluation image generation, contact sheets, and visual review.

Production inputs:

- Body LoRA: `datasets/bini_body_selected/` or promoted `datasets/bini_body_gold/`
- Braces LoRA: filtered subset where braces/crutches are clearly visible

Do not train from `needs_fix/`, `rejected/`, `datasets/bini_body_needs_fix/`, or `datasets/bini_body_rejected/`.

Triggers:

- Face LoRA: `bk_bini_teen`
- Body LoRA: `bk_bini_body`
- Braces/Mobility LoRA: `bk_bini_braces`

