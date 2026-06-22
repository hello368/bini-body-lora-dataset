#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAINING_IMAGES = sorted((ROOT / "images").glob("bini_body_*.png"))
NEEDS_FIX_IMAGES = sorted((ROOT / "needs_fix").glob("bini_body_*.png"))
REJECTED_IMAGES = sorted((ROOT / "rejected").glob("bini_body_*.png"))
SELECTED_SHEET = ROOT / "contact_sheets" / "selected_contact_sheet.jpg"


def cards_for(images: list[Path], folder: str, status: str) -> str:
    return "\n".join(
        f'''        <a class="card" href="{folder}/{image.name}" target="_blank" rel="noopener">
          <img src="{folder}/{image.name}" alt="{image.name}" loading="lazy">
          <span>{image.name}</span>
          <em>{status}</em>
        </a>'''
        for image in images
    )


def main():
    selected_cards = cards_for(TRAINING_IMAGES, "images", "selected")
    needs_fix_cards = cards_for(NEEDS_FIX_IMAGES, "needs_fix", "needs fix")
    rejected_cards = cards_for(REJECTED_IMAGES, "rejected", "rejected")
    selected_sheet = ""
    if SELECTED_SHEET.exists():
        selected_sheet = f'''      <a class="sheet" href="contact_sheets/{SELECTED_SHEET.name}" target="_blank" rel="noopener">
        <img src="contact_sheets/{SELECTED_SHEET.name}" alt="selected contact sheet">
        <span>{SELECTED_SHEET.name} · final selected set</span>
      </a>'''
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bini Body LoRA Final Selected Training Set</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0d0f12;
      --panel: #171b20;
      --line: #2a3038;
      --text: #edf1f5;
      --muted: #9aa4b2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px clamp(16px, 4vw, 40px) 18px;
      border-bottom: 1px solid var(--line);
      background: #111418;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(24px, 4vw, 40px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .meta {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    main {{
      padding: 24px clamp(12px, 3vw, 40px) 40px;
    }}
    .contact-sheets {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }}
    .sheet {{
      display: block;
      border: 1px solid var(--line);
      background: var(--panel);
      text-decoration: none;
    }}
    .sheet img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .sheet span {{
      display: block;
      padding: 10px 12px;
      color: var(--muted);
      font-size: 13px;
      border-top: 1px solid var(--line);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 14px;
    }}
    section + section {{
      margin-top: 34px;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 18px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    details {{
      border-top: 1px solid var(--line);
      padding-top: 18px;
    }}
    summary {{
      cursor: pointer;
      color: var(--text);
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 14px;
    }}
    .card {{
      display: block;
      overflow: hidden;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      text-decoration: none;
    }}
    .card img {{
      display: block;
      width: 100%;
      aspect-ratio: 2 / 3;
      object-fit: cover;
      background: #0a0c0f;
    }}
    .card span {{
      display: block;
      padding: 9px 10px;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      overflow-wrap: anywhere;
      border-top: 1px solid var(--line);
    }}
    .card em {{
      display: block;
      padding: 0 10px 9px;
      color: var(--muted);
      font-size: 11px;
      font-style: normal;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    @media (max-width: 520px) {{
      main {{ padding-left: 10px; padding-right: 10px; }}
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
      .card span {{ font-size: 11px; padding: 8px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Bini Body LoRA Final Selected Training Set</h1>
    <p class="meta">{len(TRAINING_IMAGES)} selected training images for <code>bk_bini_teen</code>. Click any image for full size.</p>
  </header>
  <main>
    <section class="contact-sheets" aria-label="Contact sheets">
{selected_sheet}
    </section>
    <section aria-label="Selected images">
      <h2>FINAL SELECTED TRAINING SET</h2>
      <div class="grid">
{selected_cards}
      </div>
    </section>
    <details aria-label="Needs fix candidate images">
      <summary>NEEDS FIX: 008, 012, 036, 041, 048</summary>
      <div class="grid">
{needs_fix_cards}
      </div>
    </details>
    <details aria-label="Rejected candidate images">
      <summary>REJECTED / CANDIDATE IMAGES: 001-007, 009-011, 013-025</summary>
      <div class="grid">
{rejected_cards}
      </div>
    </details>
  </main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(
        f"Wrote {ROOT / 'index.html'} with "
        f"{len(TRAINING_IMAGES)} selected, {len(NEEDS_FIX_IMAGES)} needs-fix, "
        f"and {len(REJECTED_IMAGES)} rejected images"
    )


if __name__ == "__main__":
    main()
