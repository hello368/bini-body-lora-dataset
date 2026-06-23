#!/usr/bin/env python3
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "selected": ROOT / "datasets" / "bini_body_selected",
    "gold": ROOT / "datasets" / "bini_body_gold",
    "needs_fix": ROOT / "datasets" / "bini_body_needs_fix",
    "rejected": ROOT / "datasets" / "bini_body_rejected",
}
REVIEW_CSV = ROOT / "reviews" / "image_review_status.csv"
REPORT = ROOT / "reviews" / "dataset_audit.md"

ALLOWED_STATUS = {"selected_gold", "selected", "needs_fix", "rejected"}
FORBIDDEN_POSITIVE_PATTERNS = {
    "female",
    "girl",
    "schoolgirl",
    "skirt",
    "dress",
    "shorts",
    "bare thighs",
    "child",
    "young boy",
    "wheelchair",
}


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "true", "1", "ok", "pass", "verified"}


def image_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.png"))


def caption_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.txt"))


def read_review_status() -> dict[str, dict[str, str]]:
    if not REVIEW_CSV.exists():
        return {}
    with REVIEW_CSV.open(newline="", encoding="utf-8") as handle:
        return {row["filename"]: row for row in csv.DictReader(handle)}


def main() -> int:
    rows = read_review_status()
    report: list[str] = [
        "# Bini Body Dataset Audit",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
    ]
    warnings: list[str] = []
    errors: list[str] = []
    filename_locations: defaultdict[str, list[str]] = defaultdict(list)

    for label, folder in DATASETS.items():
        images = image_files(folder)
        captions = caption_files(folder)
        image_stems = {p.stem for p in images}
        caption_stems = {p.stem for p in captions if p.name != "README.txt"}
        missing_captions = sorted(image_stems - caption_stems)
        orphan_captions = sorted(caption_stems - image_stems)
        report.append(f"- `{label}`: {len(images)} images, {len(captions)} caption files")
        if missing_captions:
            errors.append(f"{label}: missing captions for {', '.join(missing_captions)}")
        if orphan_captions:
            warnings.append(f"{label}: orphan captions for {', '.join(orphan_captions)}")
        for image in images:
            filename_locations[image.name].append(label)

    duplicates = {name: locs for name, locs in filename_locations.items() if len(locs) > 1}
    for name, locs in sorted(duplicates.items()):
        errors.append(f"duplicate filename across dataset partitions: {name} in {', '.join(locs)}")

    selected_names = set(filename_locations.keys()) & {
        p.name for p in image_files(DATASETS["selected"])
    }
    for excluded_label in ("needs_fix", "rejected"):
        excluded_names = {p.name for p in image_files(DATASETS[excluded_label])}
        overlap = sorted(selected_names & excluded_names)
        if overlap:
            errors.append(f"selected/{excluded_label} overlap: {', '.join(overlap)}")

    status_counts: Counter[str] = Counter()
    for filename, row in rows.items():
        status = row.get("status", "").strip()
        status_counts[status] += 1
        if status not in ALLOWED_STATUS:
            errors.append(f"{filename}: invalid review status `{status}`")

    for label, folder in DATASETS.items():
        for caption in caption_files(folder):
            if caption.name == "README.txt":
                continue
            text = caption.read_text(encoding="utf-8", errors="ignore")
            lower = text.lower().replace("dress shoes", "formal shoes")
            forbidden = sorted(
                word
                for word in FORBIDDEN_POSITIVE_PATTERNS
                if re.search(rf"(?<![a-z]){re.escape(word)}(?![a-z])", lower)
            )
            if forbidden and label in {"selected", "gold"}:
                errors.append(f"{caption.relative_to(ROOT)}: forbidden positive words: {', '.join(forbidden)}")
            review = rows.get(caption.with_suffix(".png").name)
            if not review and label != "gold":
                warnings.append(f"{caption.relative_to(ROOT)} has no review metadata row")
            elif review and review.get("status", "") in {"selected", "selected_gold"}:
                if "leg braces visible" in lower and not truthy(review.get("bilateral_braces_ok", "")):
                    warnings.append(
                        f"{caption.relative_to(ROOT)} says leg braces visible but bilateral_braces_ok is not verified"
                    )
                if "forearm crutches" in lower and not truthy(review.get("crutches_ok", "")):
                    warnings.append(
                        f"{caption.relative_to(ROOT)} says forearm crutches but crutches_ok is not verified"
                    )

    report.extend(
        [
            "",
            "## Review Status Counts",
            "",
        ]
    )
    for status in sorted(status_counts):
        report.append(f"- `{status}`: {status_counts[status]}")

    report.extend(["", "## Errors", ""])
    report.extend([f"- {item}" for item in errors] if errors else ["- None"])
    report.extend(["", "## Warnings", ""])
    report.extend([f"- {item}" for item in warnings] if warnings else ["- None"])
    report.extend(
        [
            "",
            "## Production Rule",
            "",
            "Train body LoRA only from `datasets/bini_body_selected/` or manually promoted `datasets/bini_body_gold/`.",
            "Never train from `datasets/bini_body_needs_fix/`, `datasets/bini_body_rejected/`, `needs_fix/`, or `rejected/`.",
            "Use `bk_bini_body` as the body trigger. Keep `bk_bini_teen` for the separate face LoRA only.",
            "",
        ]
    )
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {REPORT}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
