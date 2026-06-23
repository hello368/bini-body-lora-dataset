#!/usr/bin/env python3
import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path


BASE_PROMPT = (
    "bk_bini_teen, bk_bini_body, 17 year old Korean male high school student, "
    "slim fragile body, narrow shoulders, black Korean male school uniform, "
    "white dress shirt, dark tie, long black trousers, black dress shoes, "
    "bilateral orthopedic leg braces, realistic anime, cinematic lighting, "
    "high-end Korean webtoon quality, full body, solo character"
)

NEGATIVE_PROMPT = (
    "female, girl, schoolgirl, skirt, dress, shorts, bare thighs, child, young "
    "boy, chibi, cute child, muscular adult, old man, beard, robot leg, "
    "cybernetic leg, prosthetic replacement, amputee, wheelchair, cane, armpit "
    "crutches, one leg brace only, missing leg brace, bad anatomy, extra limbs, "
    "cropped body, duplicate character, multiple people, text, watermark, logo"
)

PROMPTS = [
    "front full body standing, black male school uniform, long black trousers, bilateral orthopedic leg braces",
    "back full body standing, black male school uniform, long black trousers",
    "left side full body, long black trousers, bilateral orthopedic leg braces",
    "right side full body, long black trousers, bilateral orthopedic leg braces",
    "3/4 front full body, lonely expression",
    "walking slowly in school hallway, full body, leg braces visible",
    "walking outside school, full body, leg braces visible",
    "sitting at classroom desk, leg braces partially visible",
    "standing beside classroom desk, full body",
    "looking out classroom window, full body",
    "slowly climbing stairs, holding rail, leg braces visible",
    "descending stairs carefully, holding rail, leg braces visible",
    "resting on stair landing, exhausted, leg braces visible",
    "standing with forearm crutches, full body, both leg braces visible",
    "walking with forearm crutches in school hallway, full body, both leg braces visible",
    "rainy night, standing under rain, full body",
    "walking home at night, full body",
    "crossing empty street at night, full body",
    "forced smile, full body",
    "holding back tears, full body",
    "determined expression, full body",
    "emotionally exhausted, full body",
    "lonely expression in empty classroom, full body",
    "school rooftop at sunset, full body",
    "library, standing quietly, full body",
    "sports field, standing alone, full body",
    "bus stop with forearm crutches, full body",
    "classroom with forearm crutches beside desk, full body",
    "bedroom, sitting on bed, leg braces visible",
    "mirror scene, forced smile, full body",
]

SEEDS = [
    20260623001, 20260623002, 20260623003, 20260623004, 20260623005,
    20260623006, 20260623007, 20260623008, 20260623009, 20260623010,
    20260623011, 20260623012, 20260623013, 20260623014, 20260623015,
    20260623016, 20260623017, 20260623018, 20260623019, 20260623020,
    20260623021, 20260623022, 20260623023, 20260623024, 20260623025,
    20260623026, 20260623027, 20260623028, 20260623029, 20260623030,
]


def request_json(url, payload=None, timeout=30):
    if payload is None:
        return json.loads(urllib.request.urlopen(url, timeout=timeout).read())
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def wait_for_comfy(base_url):
    for _ in range(120):
        try:
            request_json(f"{base_url}/system_stats", timeout=5)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("ComfyUI did not become ready")


def wait_for_output(base_url, prompt_id):
    for _ in range(600):
        time.sleep(2)
        history = request_json(f"{base_url}/history/{prompt_id}", timeout=10)
        if prompt_id not in history:
            continue
        item = history[prompt_id]
        if item.get("status", {}).get("status_str") == "error":
            raise RuntimeError(json.dumps(item.get("status"), indent=2))
        files = []
        for output in item.get("outputs", {}).values():
            for image in output.get("images", []):
                files.append(image["filename"])
        if files:
            return files
    raise TimeoutError(f"Timed out waiting for {prompt_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    parser.add_argument("--workflow", default="/workspace/flux-lora/ComfyUI/workflows/bini_dark_korean_webtoon_test.json")
    parser.add_argument("--comfy-output", default="/workspace/flux-lora/ComfyUI/output")
    parser.add_argument("--repo-root", default="/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora")
    parser.add_argument("--body-lora", default="bk_bini_body/bk_bini_body_v1_conservative.safetensors")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--steps", type=int, default=30)
    args = parser.parse_args()

    if len(PROMPTS) != 30 or len(SEEDS) != 30:
        raise RuntimeError("Expected 30 prompts and 30 seeds")

    repo_root = Path(args.repo_root)
    out_dir = repo_root / "evaluation" / "bk_bini_body_v1_conservative"
    out_dir.mkdir(parents=True, exist_ok=True)

    wait_for_comfy(args.comfy_url)
    base_workflow = json.loads(Path(args.workflow).read_text())
    comfy_output = Path(args.comfy_output)
    manifest = []

    for i, prompt in enumerate(PROMPTS, 1):
        final_prompt = f"{BASE_PROMPT}, {prompt}"
        workflow = json.loads(json.dumps(base_workflow))
        workflow["4"]["inputs"]["text"] = final_prompt
        workflow["5"]["inputs"]["text"] = NEGATIVE_PROMPT
        workflow["6"]["inputs"]["width"] = args.width
        workflow["6"]["inputs"]["height"] = args.height
        workflow["7"]["inputs"]["noise_seed"] = SEEDS[i - 1]
        workflow["10"]["inputs"]["steps"] = args.steps
        workflow["13"]["inputs"]["filename_prefix"] = f"bk_bini_body_v1_conservative_eval_{i:03d}"
        workflow["14"]["inputs"]["lora_name"] = args.body_lora
        workflow["14"]["inputs"]["strength_model"] = 0.85
        workflow["14"]["inputs"]["strength_clip"] = 0.85

        print(f"GENERATE conservative eval {i:03d}: {prompt}", flush=True)
        response = request_json(f"{args.comfy_url}/prompt", {"prompt": workflow})
        generated = wait_for_output(args.comfy_url, response["prompt_id"])
        dst = out_dir / f"bk_bini_body_v1_conservative_eval_{i:03d}.png"
        shutil.copy2(comfy_output / generated[0], dst)
        (out_dir / f"bk_bini_body_v1_conservative_eval_{i:03d}.txt").write_text(final_prompt + "\n", encoding="utf-8")
        manifest.append({"index": i, "seed": SEEDS[i - 1], "file": str(dst), "prompt": final_prompt})
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"SAVED {dst}", flush=True)

    print(f"DONE {len(manifest)} conservative evaluation images", flush=True)


if __name__ == "__main__":
    main()
