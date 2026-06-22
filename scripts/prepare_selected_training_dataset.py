#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


SELECTED_IDS = [
    "026", "027", "028", "029", "030",
    "031", "032", "033", "034", "035",
    "037", "038", "039", "040",
    "042", "043", "044", "045", "046", "047",
    "049", "050",
    "051", "052", "053", "054", "055", "056", "057", "058", "059", "060",
    "061", "062", "063", "064", "065", "066", "067", "068", "069", "070",
    "071", "072", "073", "074", "075", "076", "077", "078", "079", "080",
]

EXCLUDED_IDS = {
    "001", "002", "003", "004", "005", "006", "007",
    "008", "009", "010", "011", "012", "013", "014", "015", "016", "017",
    "018", "019", "020", "021", "022", "023", "024", "025",
    "036", "041", "048",
}


def link_or_copy(src: Path, dst: Path, copy_files: bool) -> None:
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if copy_files:
        shutil.copy2(src, dst)
    else:
        dst.symlink_to(Path("..") / ".." / "images" / src.name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", default="training/selected_dataset")
    parser.add_argument("--copy", action="store_true", help="Copy images instead of creating symlinks.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    image_dir = root / "images"
    caption_dir = root / "captions"
    output_dir = root / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    expected = set(SELECTED_IDS)
    actual_images = {path.stem[-3:] for path in image_dir.glob("bini_body_*.png")}
    actual_captions = {path.stem[-3:] for path in caption_dir.glob("bini_body_*.txt")}

    if actual_images != expected:
        raise SystemExit(f"images/ must contain selected IDs only. extra={sorted(actual_images - expected)} missing={sorted(expected - actual_images)}")
    if actual_captions != expected:
        raise SystemExit(f"captions/ must contain selected IDs only. extra={sorted(actual_captions - expected)} missing={sorted(expected - actual_captions)}")

    excluded_in_training = expected & EXCLUDED_IDS
    if excluded_in_training:
        raise SystemExit(f"Excluded IDs present in selected set: {sorted(excluded_in_training)}")

    for old in output_dir.glob("bini_body_*"):
        old.unlink()

    manifest = []
    for image_id in SELECTED_IDS:
        stem = f"bini_body_{image_id}"
        src_image = image_dir / f"{stem}.png"
        src_caption = caption_dir / f"{stem}.txt"
        dst_image = output_dir / src_image.name
        dst_caption = output_dir / src_caption.name
        link_or_copy(src_image, dst_image, args.copy)
        shutil.copy2(src_caption, dst_caption)
        manifest.append(
            {
                "id": image_id,
                "image": str(dst_image.relative_to(root)),
                "caption": str(dst_caption.relative_to(root)),
                "source_image": str(src_image.relative_to(root)),
                "source_caption": str(src_caption.relative_to(root)),
            }
        )

    manifest_path = root / "training" / "selected_training_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Prepared {len(manifest)} selected training pairs in {output_dir}")
    print(f"Wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
