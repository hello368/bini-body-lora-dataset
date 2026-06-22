# Bini Body LoRA Final Selected Training Set

Selected full-body training dataset for the `bk_bini_teen` character.

## Contents

- `images/`: final selected training images only
- `captions/`: matching `.txt` captions for final selected images only
- `training/selected_dataset/`: Kohya-ready sidecar dataset generated from selected images only
- `training/bini_body_flux_selected_config.toml`: selected-only training settings
- `training/train_bini_body_flux_selected.sh`: RunPod/Kohya FLUX LoRA training command
- `needs_fix/` and `rejected/`: review history only; do not train from these folders

## Character Trigger

`bk_bini_teen`

## Selected Training IDs

026-035, 037-040, 042-047, 049-080

## Training Rule

Use only `images/`, `captions/`, or the generated `training/selected_dataset/`.
Do not train on `needs_fix/` or `rejected/`.

Prepare the sidecar training folder:

```bash
python3 scripts/prepare_selected_training_dataset.py
```

Run FLUX LoRA training on RunPod:

```bash
bash training/train_bini_body_flux_selected.sh
```

## Notes

- Generated with the existing Bini Face LoRA.
- Intended for Bini Body LoRA training.
- Captions include the trigger and selected body/uniform/leg-brace descriptors.
