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
    "teenage boy, slim fragile body, slightly undernourished, narrow shoulders, "
    "fragile posture, messy black hair, large dark tired eyes, subtle eye bags, "
    "pale skin, emotionally restrained lonely expression, black Korean male "
    "school uniform blazer, white dress shirt, dark tie, long black school "
    "trousers, black dress shoes, medical orthopedic leg braces on both legs, "
    "bilateral orthopedic leg braces over or around long black trousers, "
    "realistic anime, cinematic lighting, high-end Korean action webtoon "
    "quality, full body, solo character, character consistency, masterpiece, "
    "best quality"
)

CAPTION_BASE = (
    "bk_bini_teen, 17 year old Korean male high school student, slim fragile "
    "body, black male school uniform, long black trousers, bilateral orthopedic "
    "leg braces"
)

STRICT_RULE = (
    "long black trousers in every image, no shorts, no skirt-like silhouette, "
    "no bare legs, clearly male 17-year-old Korean high school student, avoid "
    "childlike proportions, avoid cute child face, avoid schoolgirl silhouette, "
    "both leg braces visible whenever legs are visible"
)

CRUTCH_PROMPT = (
    "using a pair of medical forearm crutches, careful posture, both leg braces "
    "visible, crutches are an addition not a replacement"
)

NEGATIVE_PROMPT = (
    "female, girl, schoolgirl, skirt, dress, shorts, bare thighs, child, young "
    "boy, toddler, chibi, cute child, muscular adult, old man, beard, robot leg, "
    "cybernetic leg, prosthetic replacement, amputee, one leg brace only, "
    "missing leg brace, wheelchair, cane, armpit crutches, bad anatomy, extra "
    "limbs, extra arms, extra legs, cropped body, duplicate character, multiple "
    "people, text, watermark, logo"
)

SCENES = [
    # 10 stairs scenes.
    ("stairs", "climbing a narrow school stairwell slowly, one hand on rail, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "descending concrete school stairs carefully, holding rail, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "paused halfway on stair landing, exhausted posture, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "standing at bottom of stairs looking upward, anxious expression, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "reaching the top step with restrained determination, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "side view climbing stairs with careful gait, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "back view on stairwell landing, lonely posture, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "evening school stairwell under fluorescent lights, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "rainy outdoor school steps, careful stance, full body, long black trousers, both orthopedic leg braces visible"),
    ("stairs", "sitting on stair landing recovering breath, legs visible, long black trousers, both orthopedic leg braces visible"),

    # 10 forearm crutch scenes.
    ("crutches", "walking through school corridor with forearm crutches, full body, long black trousers"),
    ("crutches", "standing alone at bus stop with forearm crutches, full body, long black trousers"),
    ("crutches", "crossing empty street at night with forearm crutches, full body, long black trousers"),
    ("crutches", "waiting near classroom door with forearm crutches, full body, long black trousers"),
    ("crutches", "moving slowly beside lockers with forearm crutches, full body, long black trousers"),
    ("crutches", "standing under rain with forearm crutches, full body, long black trousers"),
    ("crutches", "walking home under streetlights with forearm crutches, full body, long black trousers"),
    ("crutches", "careful posture beside stair rail with forearm crutches, full body, long black trousers"),
    ("crutches", "standing in quiet hospital corridor with forearm crutches, full body, long black trousers"),
    ("crutches", "entering classroom carefully with forearm crutches, full body, long black trousers"),

    # 15 emotional full-body scenes.
    ("emotional", "standing alone in empty classroom after sunset, holding back tears, full body, long black trousers, both leg braces visible"),
    ("emotional", "forced small smile while standing in hallway, sad eyes, full body, long black trousers, both leg braces visible"),
    ("emotional", "looking down quietly at his braces, emotionally restrained, full body, long black trousers, both leg braces visible"),
    ("emotional", "standing near rainy window with lonely expression, full body, long black trousers, both leg braces visible"),
    ("emotional", "clutching notebook to chest, anxious restrained expression, full body, long black trousers, both leg braces visible"),
    ("emotional", "standing in dark bedroom with tired eyes, full body, long black trousers, both leg braces visible"),
    ("emotional", "looking into mirror with forced composure, full body, long black trousers, both leg braces visible"),
    ("emotional", "standing outside school gate after everyone left, lonely serious expression, full body, long black trousers, both leg braces visible"),
    ("emotional", "walking slowly while holding back tears, full body, long black trousers, both leg braces visible"),
    ("emotional", "standing beneath streetlight with exhausted posture, full body, long black trousers, both leg braces visible"),
    ("emotional", "determined expression before climbing stairs, full body, long black trousers, both leg braces visible"),
    ("emotional", "sitting on bed in uniform, quiet despair, legs visible, long black trousers, both leg braces visible"),
    ("emotional", "standing beside classroom desk with trembling hands, full body, long black trousers, both leg braces visible"),
    ("emotional", "walking through rain with restrained sadness, full body, long black trousers, both leg braces visible"),
    ("emotional", "standing alone in rooftop walkway wind, melancholy expression, full body, long black trousers, both leg braces visible"),

    # 13 environmental variation scenes.
    ("environment", "school rooftop walkway at blue hour, full body, long black trousers, both leg braces visible"),
    ("environment", "quiet convenience store exterior at night, full body, long black trousers, both leg braces visible"),
    ("environment", "empty subway platform after school, full body, long black trousers, both leg braces visible"),
    ("environment", "narrow apartment hallway, full body, long black trousers, both leg braces visible"),
    ("environment", "school courtyard in pale winter light, full body, long black trousers, both leg braces visible"),
    ("environment", "underpass with wet concrete reflections, full body, long black trousers, both leg braces visible"),
    ("environment", "small clinic waiting area, full body, long black trousers, both leg braces visible"),
    ("environment", "library aisle after school, full body, long black trousers, both leg braces visible"),
    ("environment", "empty playground beside school at dusk, full body, long black trousers, both leg braces visible"),
    ("environment", "bus interior standing carefully near handrail, full body, long black trousers, both leg braces visible"),
    ("environment", "school nurse office doorway, full body, long black trousers, both leg braces visible"),
    ("environment", "rainy alley shortcut after school, full body, long black trousers, both leg braces visible"),
    ("environment", "dim classroom with sunset through curtains, full body, long black trousers, both leg braces visible"),
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
    for _ in range(420):
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
    parser.add_argument("--dataset-root", default="/workspace/kingdom_underfoot/datasets/characters/bk_bini_body_lora")
    parser.add_argument("--comfy-output", default="/workspace/flux-lora/ComfyUI/output")
    parser.add_argument("--lora-name", default="bk_bini_teen/bini_flux_lora_v1.safetensors")
    parser.add_argument("--lora-strength", type=float, default=0.78)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1536)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if len(SCENES) != 48:
        raise RuntimeError(f"Expected 48 scenes, got {len(SCENES)}")

    dataset_root = Path(args.dataset_root)
    image_dir = dataset_root / "images"
    caption_dir = dataset_root / "captions"
    for directory in (image_dir, caption_dir):
        directory.mkdir(parents=True, exist_ok=True)

    existing_selected = list(image_dir.glob("bini_body_0*.png"))
    if len(existing_selected) < 52:
        raise RuntimeError(f"Expected at least 52 existing selected images, found {len(existing_selected)}")

    workflow_path = Path(args.workflow)
    comfy_output = Path(args.comfy_output)
    wait_for_comfy(args.comfy_url)
    base_workflow = json.loads(workflow_path.read_text())

    manifest_path = dataset_root / "manifest.json"
    manifest_by_index = {}
    if manifest_path.exists():
        try:
            for item in json.loads(manifest_path.read_text()):
                manifest_by_index[int(item["index"])] = item
        except Exception:
            manifest_by_index = {}

    for offset, (category, scene) in enumerate(SCENES):
        index = 81 + offset
        png_path = image_dir / f"bini_body_{index:03d}.png"
        txt_path = caption_dir / f"bini_body_{index:03d}.txt"

        if category == "crutches":
            final_prompt = f"{BASE_PROMPT}, {scene}, {CRUTCH_PROMPT}, {STRICT_RULE}"
            caption = f"{CAPTION_BASE}, forearm crutches, careful posture, {scene}"
            negative_prompt = f"{NEGATIVE_PROMPT}, cane, wheelchair, armpit crutches"
        else:
            final_prompt = f"{BASE_PROMPT}, {scene}, {STRICT_RULE}"
            caption = f"{CAPTION_BASE}, {category} scene, {scene}"
            negative_prompt = f"{NEGATIVE_PROMPT}, forearm crutches, cane, wheelchair, armpit crutches"

        if png_path.exists() and txt_path.exists() and not args.overwrite:
            print(f"SKIP {index:03d} existing {png_path}", flush=True)
        else:
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

            print(f"GENERATE {index:03d} [{category}]: {scene}", flush=True)
            response = request_json(f"{args.comfy_url}/prompt", {"prompt": workflow})
            generated = wait_for_output(args.comfy_url, response["prompt_id"])
            src = comfy_output / generated[0]
            shutil.copy2(src, png_path)
            txt_path.write_text(caption + "\n", encoding="utf-8")
            print(f"SAVED {png_path}", flush=True)

        manifest_by_index[index] = {
            "index": index,
            "file": str(png_path),
            "caption_file": str(txt_path),
            "category": category,
            "status": "selected",
            "prompt": final_prompt,
            "caption": caption,
            "negative": negative_prompt,
        }
        manifest_path.write_text(
            json.dumps([manifest_by_index[i] for i in sorted(manifest_by_index)], indent=2),
            encoding="utf-8",
        )

    print(f"DONE generated 081-128 in {dataset_root}", flush=True)


if __name__ == "__main__":
    main()
