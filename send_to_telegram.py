#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from urllib import request, parse


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
PHOTO_PATHS = [
    ROOT / "reviews" / "selected_contact_sheet.jpg",
    ROOT / "contact_sheets" / "selected_contact_sheet.jpg",
]

MESSAGE = """Bini Body LoRA Selected Images

KEEP:
026, 027, 028, 029, 030,
031, 032, 033, 034, 035,
037, 038, 039, 040,
042, 043, 044, 045, 046, 047, 049, 050,
051, 052, 053, 054, 055, 056, 057, 058, 059, 060,
061, 062, 063, 064, 065, 066, 067, 068, 069, 070,
071, 072, 073, 074, 075, 076, 077, 078, 079, 080"""


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def multipart_form(fields: dict[str, str], files: dict[str, Path]) -> tuple[bytes, str]:
    boundary = "----bini-body-lora-boundary"
    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        chunks.append(value.encode("utf-8"))
        chunks.append(b"\r\n")
    for key, path in files.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{key}"; '
                f'filename="{path.name}"\r\n'
                "Content-Type: image/jpeg\r\n\r\n"
            ).encode()
        )
        chunks.append(path.read_bytes())
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def telegram_request(token: str, method: str, data: bytes, content_type: str) -> bytes:
    url = f"https://api.telegram.org/bot{token}/{method}"
    req = request.Request(url, data=data, headers={"Content-Type": content_type})
    with request.urlopen(req, timeout=60) as response:
        return response.read()


def main() -> int:
    load_env(ENV_PATH)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env", file=sys.stderr)
        return 1

    photo_path = next((path for path in PHOTO_PATHS if path.exists()), None)
    if photo_path is None:
        print("Missing selected_contact_sheet.jpg. Run scripts/generate_selected_contact_sheet.swift first.", file=sys.stderr)
        return 1

    text_data = parse.urlencode({"chat_id": chat_id, "text": MESSAGE}).encode()
    telegram_request(token, "sendMessage", text_data, "application/x-www-form-urlencoded")

    body, boundary = multipart_form(
        {"chat_id": chat_id, "caption": "selected_contact_sheet.jpg"},
        {"photo": photo_path},
    )
    telegram_request(token, "sendPhoto", body, f"multipart/form-data; boundary={boundary}")
    print(f"Sent Telegram review message and {photo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
