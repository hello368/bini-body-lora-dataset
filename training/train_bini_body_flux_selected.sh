#!/usr/bin/env bash
set -euo pipefail

BASE=/workspace/flux-lora
COMFY="$BASE/ComfyUI"
KOHYA="$BASE/kohya_ss"
TRAIN_ROOT=/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora
TRAIN_DATA="$TRAIN_ROOT/training/selected_dataset"
OUT_DIR="$TRAIN_ROOT/output"
LOG_DIR="$TRAIN_ROOT/logs"
MODEL_NAME=bini_body_flux_lora_selected_v1

mkdir -p "$OUT_DIR" "$LOG_DIR" "$COMFY/models/loras/bk_bini_body"

python3 "$TRAIN_ROOT/scripts/prepare_selected_training_dataset.py" --root "$TRAIN_ROOT"

pair_count="$(find "$TRAIN_DATA" -maxdepth 1 -name 'bini_body_*.png' | wc -l)"
caption_count="$(find "$TRAIN_DATA" -maxdepth 1 -name 'bini_body_*.txt' | wc -l)"
if [ "$pair_count" -ne 100 ] || [ "$caption_count" -ne 100 ]; then
  echo "Expected 100 selected images and captions in $TRAIN_DATA, got images=$pair_count captions=$caption_count" >&2
  exit 1
fi

if find "$TRAIN_DATA" -maxdepth 1 \( -name 'bini_body_00[1-9].*' -o -name 'bini_body_01[0-9].*' -o -name 'bini_body_02[0-5].*' -o -name 'bini_body_036.*' -o -name 'bini_body_041.*' -o -name 'bini_body_048.*' \) | grep -q .; then
  echo "Rejected or needs_fix files found in selected training dataset." >&2
  exit 1
fi

if [ -f "$COMFY/comfy.pid" ]; then
  pid="$(cat "$COMFY/comfy.pid" || true)"
  if [ -n "${pid:-}" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" || true
    sleep 5
  fi
fi

cd "$KOHYA"
source venv/bin/activate
cd sd-scripts

export HF_HUB_DISABLE_XET=1

python flux_train_network.py \
  --pretrained_model_name_or_path "$BASE/training/models/flux1-dev-fp8-bfl-training.safetensors" \
  --clip_l "$COMFY/models/clip/clip_l.safetensors" \
  --t5xxl "$COMFY/models/clip/t5xxl_fp8_e4m3fn.safetensors" \
  --ae "$COMFY/models/vae/ae.safetensors" \
  --train_data_dir "$TRAIN_DATA" \
  --output_dir "$OUT_DIR" \
  --logging_dir "$LOG_DIR" \
  --output_name "$MODEL_NAME" \
  --caption_extension .txt \
  --resolution 1024,1024 \
  --enable_bucket \
  --min_bucket_reso 512 \
  --max_bucket_reso 1536 \
  --bucket_reso_steps 64 \
  --train_batch_size 1 \
  --max_train_steps 2400 \
  --learning_rate 8e-5 \
  --optimizer_type AdamW8bit \
  --network_module networks.lora_flux \
  --network_dim 16 \
  --network_alpha 16 \
  --mixed_precision bf16 \
  --save_precision bf16 \
  --gradient_checkpointing \
  --cache_latents \
  --cache_latents_to_disk \
  --cache_text_encoder_outputs \
  --cache_text_encoder_outputs_to_disk \
  --fp8_base \
  --sdpa \
  --timestep_sampling flux_shift \
  --model_prediction_type raw \
  --guidance_scale 1.0 \
  --seed 20260622 \
  --save_every_n_steps 400 \
  --save_last_n_steps 3 \
  --max_data_loader_n_workers 1

cp "$OUT_DIR/$MODEL_NAME.safetensors" "$COMFY/models/loras/bk_bini_body/$MODEL_NAME.safetensors"
