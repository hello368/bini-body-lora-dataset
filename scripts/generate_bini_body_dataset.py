#!/usr/bin/env python3
import argparse
import json
import random
import shutil
import time
import urllib.request
from pathlib import Path


BASE_PROMPT = (
    "bk_bini_teen, 17 year old Korean male high school student, clearly male "
    "teenage boy, slim and slightly undernourished, fragile physique, messy "
    "black hair, large dark eyes, tired eyes, subtle eye bags, pale skin, lonely "
    "and emotionally restrained expression, black Korean male school uniform "
    "blazer, white dress shirt, dark tie, long black school trousers, black "
    "dress shoes, medical orthopedic leg braces on both legs, both leg braces "
    "must be visible, medical support devices, not robotic prosthetics, "
    "realistic proportions, teenager not child, not muscular, not heroic, "
    "vulnerable and realistic, cinematic realistic anime, high detail, "
    "masterpiece, best quality, character consistency, solo character, full "
    "body, head to toe visible whenever possible, masculine teenage face, no "
    "skirt, no shorts, no bare thighs"
)

NEGATIVE_PROMPT = (
    "female, girl, schoolgirl, skirt, dress, shorts, bare thighs, child, young "
    "boy, toddler, chibi, cute child, robot leg, cybernetic leg, prosthetic "
    "replacement, amputee, one leg brace only, missing leg brace, wheelchair, "
    "cane, armpit crutches, muscular adult, old man, beard, bad anatomy, extra "
    "limbs, extra arms, extra legs, cropped body, duplicate character, multiple "
    "people, text, watermark, logo"
)

CRUTCH_NEGATIVE_ADDITION = (
    "armpit crutches, wheelchair, cane, walking stick, weapon, robotic arms, "
    "extra arms, extra hands"
)

LEG_BRACES_ONLY_NEGATIVE_ADDITION = (
    "forearm crutches, armpit crutches, wheelchair, cane, walking stick, weapon, "
    "robotic arms, extra arms, extra hands"
)

PROMPTS = [
    # 20 standing/reference images
    "full body front view, standing naturally, neutral expression, white background, male character sheet, long black trousers, both leg braces visible",
    "full body back view, standing naturally, white background, male character sheet, long black trousers, both leg braces visible",
    "full body left side view, male character sheet, long black trousers, both leg braces visible",
    "full body right side view, male character sheet, long black trousers, both leg braces visible",
    "full body 3/4 front left view, male character sheet, long black trousers, both leg braces visible",
    "full body 3/4 front right view, male character sheet, long black trousers, both leg braces visible",
    "standing, both medical orthopedic leg braces clearly visible, full body, long black trousers",
    "full body lower stance reference, medical orthopedic leg braces clearly visible on both legs over long black school trousers",
    "looking down at his leg braces, full body, long black trousers, both leg braces visible",
    "holding notebook quietly, full body, long black trousers, both leg braces visible",
    "empty classroom after school, standing alone, full body, long black trousers, both leg braces visible",
    "standing beside classroom desk, full body, long black trousers, both leg braces visible",
    "standing at bus stop, full body, long black trousers, both leg braces visible",
    "standing alone in hallway, full body, long black trousers, both leg braces visible",
    "looking at classroom door, full body, long black trousers, both leg braces visible",
    "waiting quietly near stairs, full body, long black trousers, both leg braces visible",
    "evening hallway lighting, full body, long black trousers, both leg braces visible",
    "school corridor at sunset, full body, long black trousers, both leg braces visible",
    "standing outside school gate, full body, long black trousers, both leg braces visible",
    "standing in classroom, full body, long black trousers, both leg braces visible",
    # 10 walking images
    "walking slowly in school hallway, full body, long black trousers, both leg braces visible, careful gait",
    "walking outside school, full body, long black trousers, both leg braces visible, careful gait",
    "walking through school corridor, full body, long black trousers, both leg braces visible, careful gait",
    "walking home at night, full body, long black trousers, both leg braces visible, careful gait",
    "walking past classroom windows, full body, long black trousers, both leg braces visible, careful gait",
    "walking across school courtyard, full body, long black trousers, both leg braces visible, careful gait",
    "walking along quiet street, full body, long black trousers, both leg braces visible, careful gait",
    "walking in rainy evening, full body, long black trousers, both leg braces visible, careful gait",
    "walking toward bus stop, full body, long black trousers, both leg braces visible, careful gait",
    "walking through empty hallway, full body, long black trousers, both leg braces visible, careful gait",

    # 8 sitting images
    "sitting at classroom desk, leg braces visible over long black trousers, clearly male teenage boy",
    "studying alone in classroom, seated, leg braces visible, long black trousers, clearly male teenage boy",
    "looking out classroom window, seated, leg braces visible, long black trousers",
    "sitting on bed, leg braces visible on both legs, long black trousers",
    "studying late at night, seated, leg braces visible on both legs, long black trousers",
    "looking at old photograph, seated, long black trousers, both leg braces visible",
    "sitting on stair landing, exhausted, leg braces visible on both legs, long black trousers",
    "sitting alone in school hallway, leg braces visible on both legs, long black trousers",

    # 5 stairs images
    "slowly climbing stairs, holding rail, leg braces visible on both legs, long black trousers",
    "descending stairs carefully, holding rail, leg braces visible on both legs, long black trousers",
    "resting on stair landing, exhausted, leg braces visible on both legs, long black trousers",
    "holding stair rail, full body, long black trousers, both leg braces visible",
    "reaching top of staircase, full body, long black trousers, both leg braces visible",

    # 5 emotional images
    "forced smile, full body, long black trousers, both leg braces visible, clearly male teenage boy",
    "holding back tears, full body, long black trousers, both leg braces visible, clearly male teenage boy",
    "lonely expression, full body, long black trousers, both leg braces visible, clearly male teenage boy",
    "emotionally exhausted, full body, long black trousers, both leg braces visible, clearly male teenage boy",
    "standing alone in dark bedroom, full body, long black trousers, both leg braces visible, restrained sadness",

    # 2 forearm crutch images
    "using a pair of forearm crutches, both leg braces visible, careful posture, full body, long black trousers, standing in school corridor",
    "using a pair of forearm crutches, both leg braces visible, careful posture, full body, long black trousers, walking slowly outside school",
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
    for _ in range(360):
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
    parser.add_argument("--output-dir", default="/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora/images")
    parser.add_argument("--comfy-output", default="/workspace/flux-lora/ComfyUI/output")
    parser.add_argument("--lora-name", default="bk_bini_teen/bini_flux_lora_v1.safetensors")
    parser.add_argument("--lora-strength", type=float, default=0.78)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--stop-index", type=int, default=50)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    workflow_path = Path(args.workflow)
    output_dir = Path(args.output_dir)
    comfy_output = Path(args.comfy_output)
    output_dir.mkdir(parents=True, exist_ok=True)

    wait_for_comfy(args.comfy_url)
    base_workflow = json.loads(workflow_path.read_text())

    manifest = []
    for index, scene in enumerate(PROMPTS, 1):
        if index < args.start_index or index > args.stop_index:
            continue

        png_path = output_dir / f"bini_body_{index:03d}.png"
        txt_path = output_dir / f"bini_body_{index:03d}.txt"
        uses_crutches = "forearm crutches" in scene
        scene_prompt = scene
        if uses_crutches:
            final_prompt = f"{BASE_PROMPT}, {scene_prompt}"
            negative_prompt = f"{NEGATIVE_PROMPT}, {CRUTCH_NEGATIVE_ADDITION}"
        else:
            final_prompt = f"{BASE_PROMPT}, {scene_prompt}"
            negative_prompt = f"{NEGATIVE_PROMPT}, {LEG_BRACES_ONLY_NEGATIVE_ADDITION}"

        if png_path.exists() and txt_path.exists() and not args.overwrite:
            print(f"SKIP {index:03d} existing {png_path}", flush=True)
            manifest.append(
                {
                    "index": index,
                    "prompt": final_prompt,
                    "negative": negative_prompt,
                    "mobility": "leg_braces_and_forearm_crutches" if uses_crutches else "leg_braces_only",
                    "file": str(png_path),
                }
            )
            continue

        workflow = json.loads(json.dumps(base_workflow))
        workflow["4"]["inputs"]["text"] = final_prompt
        workflow["5"]["inputs"]["text"] = negative_prompt
        workflow["6"]["inputs"]["width"] = args.width
        workflow["6"]["inputs"]["height"] = args.height
        workflow["7"]["inputs"]["noise_seed"] = random.randint(1, 2**63 - 1)
        workflow["10"]["inputs"]["steps"] = args.steps
        workflow["13"]["inputs"]["filename_prefix"] = f"bini_body_gen_{index:03d}"
        workflow["14"]["inputs"]["lora_name"] = args.lora_name
        workflow["14"]["inputs"]["strength_model"] = args.lora_strength

        print(f"GENERATE {index:03d}: {scene_prompt}", flush=True)
        response = request_json(f"{args.comfy_url}/prompt", {"prompt": workflow})
        prompt_id = response["prompt_id"]
        generated = wait_for_output(args.comfy_url, prompt_id)
        src = comfy_output / generated[0]

        shutil.copy2(src, png_path)
        txt_path.write_text(final_prompt + "\n", encoding="utf-8")

        item = {
            "index": index,
            "prompt": final_prompt,
            "negative": negative_prompt,
            "mobility": "leg_braces_and_forearm_crutches" if uses_crutches else "leg_braces_only",
            "file": str(png_path),
            "source": str(src),
        }
        manifest.append(item)
        (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"SAVED {png_path}", flush=True)

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"DONE {len(manifest)} files in {output_dir}", flush=True)


if __name__ == "__main__":
    main()
