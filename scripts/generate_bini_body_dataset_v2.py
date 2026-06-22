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
    "pale skin, lonely serious expression, black Korean male school uniform "
    "blazer, white dress shirt, dark tie, long black school trousers, black "
    "dress shoes, medical orthopedic leg braces on both legs, realistic anime, "
    "cinematic lighting, high-end Korean webtoon style, full body, solo "
    "character, character consistency, masterpiece, best quality"
)

CAPTION_BASE = (
    "bk_bini_teen, 17 year old Korean male high school student, slim fragile "
    "body, black male school uniform, long black trousers, bilateral orthopedic "
    "leg braces"
)

CRUTCH_ADDITION = (
    "using a pair of forearm crutches, medical forearm crutches, careful "
    "posture, both leg braces visible"
)

CAPTION_CRUTCH = "forearm crutches, careful posture"

NEGATIVE_PROMPT = (
    "female, girl, schoolgirl, skirt, dress, shorts, bare thighs, child, young "
    "boy, toddler, chibi, cute child, muscular adult, old man, beard, robot leg, "
    "cybernetic leg, prosthetic replacement, amputee, one leg brace only, "
    "missing leg brace, wheelchair, cane, armpit crutches, bad anatomy, extra "
    "limbs, extra arms, extra legs, cropped body, duplicate character, multiple "
    "people, text, watermark, logo"
)

LEG_BRACES_NEGATIVE = "forearm crutches, armpit crutches, wheelchair, cane"
CRUTCH_NEGATIVE = "armpit crutches, wheelchair, cane, walking stick"
DISCREET_AID_NEGATIVE = (
    "visible crutches, wheelchair, cane, armpit crutches, robot leg, shorts, skirt"
)


SCENES = [
    # Core character sheet images.
    ("leg_braces", "full body front view, standing naturally, neutral expression, white background, character sheet, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "full body back view, standing naturally, white background, character sheet, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "full body left side view, white background, character sheet, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "full body right side view, white background, character sheet, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "full body 3/4 front left view, white background, character sheet, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "full body 3/4 front right view, white background, character sheet, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "walking slowly, full body, careful gait, long black trousers, both orthopedic leg braces visible"),
    ("leg_braces", "sitting at classroom desk, long black trousers, leg braces visible on both legs"),
    ("leg_braces", "slowly climbing stairs, holding rail, long black trousers, leg braces visible on both legs"),
    ("crutches", "standing with forearm crutches, full body, long black trousers"),

    # Standing: leg braces only.
    ("leg_braces", "standing in classroom, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing in school hallway, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing beside classroom desk, holding notebook, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing at bus stop, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "waiting near stairs, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing under school corridor lights, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing outside school gate, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing near classroom window, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing alone in empty classroom after school, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing on rooftop walkway, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing in rain, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing under streetlight, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing in dark bedroom, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing in front of mirror, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing near lockers, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing by stair rail, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing at classroom door, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing in school courtyard, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing beside bus stop sign, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "standing on sidewalk at dusk, full body, long black trousers, both leg braces visible"),

    # Walking: leg braces only.
    ("leg_braces", "walking in school hallway, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking outside school, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking home at night, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking through empty corridor, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking past classroom windows, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking across school courtyard, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking in rainy evening, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking toward bus stop, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking across empty street, full body, careful gait, long black trousers, both leg braces visible"),
    ("leg_braces", "walking past convenience store at night, full body, careful gait, long black trousers, both leg braces visible"),

    # Sitting: leg braces only.
    ("leg_braces", "sitting alone in classroom, long black trousers, both leg braces visible"),
    ("leg_braces", "looking out classroom window, seated, long black trousers, both leg braces visible"),
    ("leg_braces", "sitting on bed, long black trousers, both leg braces visible"),
    ("leg_braces", "studying late at night, seated, long black trousers, both leg braces visible"),
    ("leg_braces", "looking at old photograph, seated, long black trousers, both leg braces visible"),
    ("leg_braces", "sitting on stair landing, exhausted, long black trousers, both leg braces visible"),
    ("leg_braces", "sitting alone in school hallway, long black trousers, both leg braces visible"),
    ("leg_braces", "sitting at bus stop bench, long black trousers, both leg braces visible"),

    # Stairs and emotional: leg braces only.
    ("leg_braces", "descending stairs carefully, holding rail, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "resting on stair landing, exhausted, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "holding stair rail, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "reaching top of staircase, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "forced smile, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "holding back tears, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "lonely expression, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "determined expression, full body, long black trousers, both leg braces visible"),
    ("leg_braces", "emotionally exhausted, full body, long black trousers, both leg braces visible"),

    # Forearm crutches: 16 images.
    ("crutches", "standing in school corridor with forearm crutches, full body, long black trousers"),
    ("crutches", "walking slowly outside school with forearm crutches, full body, long black trousers"),
    ("crutches", "standing at bus stop with forearm crutches, full body, long black trousers"),
    ("crutches", "walking in school hallway with forearm crutches, full body, long black trousers"),
    ("crutches", "waiting near stairs with forearm crutches, full body, long black trousers"),
    ("crutches", "evening hallway lighting with forearm crutches, full body, long black trousers"),
    ("crutches", "walking home at night with forearm crutches, full body, long black trousers"),
    ("crutches", "rainy night with forearm crutches, full body, long black trousers"),
    ("crutches", "crossing empty street with forearm crutches, full body, long black trousers"),
    ("crutches", "standing under rain with forearm crutches, full body, long black trousers"),
    ("crutches", "standing near classroom door with forearm crutches, full body, long black trousers"),
    ("crutches", "standing alone in hallway with forearm crutches, full body, long black trousers"),
    ("crutches", "walking past school lockers with forearm crutches, full body, long black trousers"),
    ("crutches", "standing by stair rail with forearm crutches, full body, long black trousers"),
    ("crutches", "standing outside school gate with forearm crutches, full body, long black trousers"),

    # Mobility aids not clearly visible: 8 images.
    ("discreet", "upper full body portrait standing behind classroom desk, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "seated at desk with legs partly under desk, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "standing behind bus stop railing, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "standing in doorway with lower legs partly shadowed, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "sitting on bed with legs partly hidden by shadow, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "standing in rain with lower legs partly obscured by reflections, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "standing behind classroom chair, long black trousers visible, uniform correct, mobility aids not clearly visible"),
    ("discreet", "walking in dark hallway with lower legs partly shadowed, long black trousers visible, uniform correct, mobility aids not clearly visible"),
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


def status_for(output_dir, name):
    stem = Path(name).stem
    if (output_dir.parent / "selected" / name).exists():
        return "selected"
    if (output_dir.parent / "rejected" / name).exists():
        return "rejected"
    if (output_dir.parent / "selected" / f"{stem}.txt").exists():
        return "selected"
    if (output_dir.parent / "rejected" / f"{stem}.txt").exists():
        return "rejected"
    return "candidate"


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
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--stop-index", type=int, default=80)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if len(SCENES) != 80:
        raise RuntimeError(f"Expected 80 scenes, got {len(SCENES)}")

    dataset_root = Path(args.dataset_root)
    image_dir = dataset_root / "images"
    caption_dir = dataset_root / "captions"
    selected_dir = dataset_root / "selected"
    rejected_dir = dataset_root / "rejected"
    reviews_dir = dataset_root / "reviews"
    for directory in (image_dir, caption_dir, selected_dir, rejected_dir, reviews_dir):
        directory.mkdir(parents=True, exist_ok=True)

    workflow_path = Path(args.workflow)
    comfy_output = Path(args.comfy_output)
    wait_for_comfy(args.comfy_url)
    base_workflow = json.loads(workflow_path.read_text())

    manifest = []
    for index, (mobility, scene) in enumerate(SCENES, 1):
        if index < args.start_index or index > args.stop_index:
            continue

        png_path = image_dir / f"bini_body_{index:03d}.png"
        txt_path = caption_dir / f"bini_body_{index:03d}.txt"

        if mobility == "crutches":
            final_prompt = f"{BASE_PROMPT}, {scene}, {CRUTCH_ADDITION}"
            caption = f"{CAPTION_BASE}, {CAPTION_CRUTCH}, {scene}"
            negative_prompt = f"{NEGATIVE_PROMPT}, {CRUTCH_NEGATIVE}"
        elif mobility == "discreet":
            final_prompt = (
                f"{BASE_PROMPT}, {scene}, long black trousers, clearly male "
                "17 year old, medical orthopedic leg braces may be subtle or partly obscured"
            )
            caption = f"{CAPTION_BASE}, mobility aids not clearly visible, {scene}"
            negative_prompt = f"{NEGATIVE_PROMPT}, {DISCREET_AID_NEGATIVE}"
        else:
            final_prompt = f"{BASE_PROMPT}, {scene}"
            caption = f"{CAPTION_BASE}, {scene}"
            negative_prompt = f"{NEGATIVE_PROMPT}, {LEG_BRACES_NEGATIVE}"

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

            print(f"GENERATE {index:03d} [{mobility}]: {scene}", flush=True)
            response = request_json(f"{args.comfy_url}/prompt", {"prompt": workflow})
            generated = wait_for_output(args.comfy_url, response["prompt_id"])
            src = comfy_output / generated[0]
            shutil.copy2(src, png_path)
            txt_path.write_text(caption + "\n", encoding="utf-8")
            print(f"SAVED {png_path}", flush=True)

        manifest.append(
            {
                "index": index,
                "file": str(png_path),
                "caption_file": str(txt_path),
                "mobility": mobility,
                "status": status_for(image_dir, png_path.name),
                "prompt": final_prompt,
                "caption": caption,
                "negative": negative_prompt,
            }
        )
        (dataset_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    (dataset_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"DONE {len(manifest)} files in {dataset_root}", flush=True)


if __name__ == "__main__":
    main()
