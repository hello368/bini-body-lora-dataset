#!/usr/bin/env bash
set -euo pipefail

BASE=/workspace/flux-lora
COMFY="$BASE/ComfyUI"
KOHYA="$BASE/kohya_ss"
TRAIN_ROOT=/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora
TRAIN_DATA="$TRAIN_ROOT/datasets/bini_body_selected"
KOHYA_TRAIN_PARENT="$TRAIN_ROOT/training/kohya_conservative"
KOHYA_TRAIN_DATA="$KOHYA_TRAIN_PARENT/1_bk_bini_body"
OUT_DIR="$TRAIN_ROOT/training/outputs/bk_bini_body_v1_conservative"
LOG_DIR="$TRAIN_ROOT/training/logs/bk_bini_body_v1_conservative"
MODEL_NAME=bk_bini_body_v1_conservative

mkdir -p "$OUT_DIR" "$LOG_DIR" "$COMFY/models/loras/bk_bini_body" "$KOHYA_TRAIN_DATA"

python3 "$TRAIN_ROOT/scripts/audit_bini_dataset.py"

pair_count="$(find "$TRAIN_DATA" -maxdepth 1 -name 'bini_body_*.png' | wc -l)"
caption_count="$(find "$TRAIN_DATA" -maxdepth 1 -name 'bini_body_*.txt' | wc -l)"
if [ "$pair_count" -ne 100 ] || [ "$caption_count" -ne 100 ]; then
  echo "Expected 100 production selected images and captions in $TRAIN_DATA, got images=$pair_count captions=$caption_count" >&2
  exit 1
fi

if rg -I 'bk_bini_teen|needs_fix|rejected|old candidates' "$TRAIN_DATA"/*.txt >/dev/null; then
  echo "Body training captions must not use face trigger or excluded partition words." >&2
  exit 1
fi

if [ "$(rg -I '^bk_bini_body' "$TRAIN_DATA"/*.txt | wc -l)" -ne 100 ]; then
  echo "Expected every production caption to start with bk_bini_body." >&2
  exit 1
fi

find "$KOHYA_TRAIN_DATA" -maxdepth 1 -type l -delete
for image_path in "$TRAIN_DATA"/bini_body_*.png; do
  base_name="$(basename "$image_path" .png)"
  ln -sf "$image_path" "$KOHYA_TRAIN_DATA/$base_name.png"
  ln -sf "$TRAIN_DATA/$base_name.txt" "$KOHYA_TRAIN_DATA/$base_name.txt"
done

if [ "$(find "$KOHYA_TRAIN_DATA" -maxdepth 1 -name 'bini_body_*.png' | wc -l)" -ne 100 ]; then
  echo "Expected 100 images in Kohya train folder $KOHYA_TRAIN_DATA" >&2
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
export TOKENIZERS_PARALLELISM=false

python flux_train_network.py \
  --pretrained_model_name_or_path "$BASE/training/models/flux1-dev-fp8-bfl-training.safetensors" \
  --clip_l "$COMFY/models/clip/clip_l.safetensors" \
  --t5xxl "$COMFY/models/clip/t5xxl_fp8_e4m3fn.safetensors" \
  --ae "$COMFY/models/vae/ae.safetensors" \
  --train_data_dir "$KOHYA_TRAIN_PARENT" \
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
  --max_train_steps 1600 \
  --learning_rate 8e-5 \
  --optimizer_type AdamW8bit \
  --network_module networks.lora_flux \
  --network_dim 16 \
  --network_alpha 16 \
  --network_train_unet_only \
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
  --seed 20260623 \
  --save_every_n_steps 250 \
  --save_last_n_steps 6 \
  --max_data_loader_n_workers 1

cp "$OUT_DIR/$MODEL_NAME.safetensors" "$COMFY/models/loras/bk_bini_body/$MODEL_NAME.safetensors"
