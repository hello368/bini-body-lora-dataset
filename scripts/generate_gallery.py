#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAINING_IMAGES = sorted((ROOT / "images").glob("bini_body_*.png"))
NEEDS_FIX_IMAGES = sorted((ROOT / "needs_fix").glob("bini_body_*.png"))
REJECTED_IMAGES = sorted((ROOT / "rejected").glob("bini_body_*.png"))
DATASET_SELECTED = sorted((ROOT / "datasets" / "bini_body_selected").glob("bini_body_*.png"))
DATASET_GOLD = sorted((ROOT / "datasets" / "bini_body_gold").glob("bini_body_*.png"))
DATASET_NEEDS_FIX = sorted((ROOT / "datasets" / "bini_body_needs_fix").glob("bini_body_*.png"))
DATASET_REJECTED = sorted((ROOT / "datasets" / "bini_body_rejected").glob("bini_body_*.png"))
SELECTED_SHEET = ROOT / "contact_sheets" / "selected_contact_sheet.jpg"
EVAL_IMAGES = sorted((ROOT / "evaluation" / "body_lora_v1").glob("body_lora_v1_eval_*.png"))
EVAL_SHEET = ROOT / "contact_sheets" / "body_lora_v1_evaluation_sheet.jpg"
LORA_NAME = "bk_bini_body_v1.safetensors"
COMPARISON_SHEETS = sorted((ROOT / "evaluation" / "comparison_grids").glob("*.jpg"))
CONSERVATIVE_IMAGES = sorted((ROOT / "evaluation" / "bk_bini_body_v1_conservative").glob("bk_bini_body_v1_conservative_eval_*.png"))
CONSERVATIVE_SHEET = ROOT / "contact_sheets" / "bk_bini_body_v1_conservative_eval.jpg"
CONSERVATIVE_LORA_NAME = "bk_bini_body_v1_conservative.safetensors"


def cards_for(images: list[Path], folder: str, status: str) -> str:
    return "\n".join(
        f'''        <a class="card" href="{folder}/{image.name}" target="_blank" rel="noopener">
          <img src="{folder}/{image.name}" alt="{image.name}" loading="lazy">
          <span>{image.name}</span>
          <em>{status}</em>
        </a>'''
        for image in images
    )


def sheets_for(images: list[Path], folder: str) -> str:
    return "\n".join(
        f'''      <a class="sheet" href="{folder}/{image.name}" target="_blank" rel="noopener">
        <img src="{folder}/{image.name}" alt="{image.name}">
        <span>{image.name}</span>
      </a>'''
        for image in images
    )


def main():
    selected_cards = cards_for(TRAINING_IMAGES, "images", "selected")
    needs_fix_cards = cards_for(NEEDS_FIX_IMAGES, "needs_fix", "needs fix")
    rejected_cards = cards_for(REJECTED_IMAGES, "rejected", "rejected")
    eval_cards = cards_for(EVAL_IMAGES, "evaluation/body_lora_v1", "evaluation")
    comparison_sheets = sheets_for(COMPARISON_SHEETS, "evaluation/comparison_grids")
    conservative_cards = cards_for(CONSERVATIVE_IMAGES, "evaluation/bk_bini_body_v1_conservative", "conservative evaluation")
    conservative_sheet = ""
    if CONSERVATIVE_SHEET.exists():
        conservative_sheet = f'''      <a class="sheet" href="contact_sheets/{CONSERVATIVE_SHEET.name}" target="_blank" rel="noopener">
        <img src="contact_sheets/{CONSERVATIVE_SHEET.name}" alt="conservative evaluation contact sheet">
        <span>{CONSERVATIVE_SHEET.name} · {len(CONSERVATIVE_IMAGES)} evaluation images</span>
      </a>'''
    eval_sheet = ""
    if EVAL_SHEET.exists():
        eval_sheet = f'''      <a class="sheet" href="contact_sheets/{EVAL_SHEET.name}" target="_blank" rel="noopener">
        <img src="contact_sheets/{EVAL_SHEET.name}" alt="body lora v1 evaluation contact sheet">
        <span>{EVAL_SHEET.name} · {len(EVAL_IMAGES)} evaluation images</span>
      </a>'''
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
    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 14px 0;
    }}
    .stats span {{
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 8px 10px;
      color: var(--muted);
      font-size: 13px;
    }}
    .stats strong {{
      color: var(--text);
      font-weight: 700;
    }}
    a {{
      color: #9fc7ff;
    }}
    .experiment-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .experiment {{
      display: block;
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 12px;
      text-decoration: none;
      color: var(--text);
    }}
    .experiment strong {{
      display: block;
      margin-bottom: 8px;
      font-size: 14px;
      overflow-wrap: anywhere;
    }}
    .experiment span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
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
    <p class="meta">{len(DATASET_SELECTED)} production selected images for <code>bk_bini_body</code>. GitHub is the source of truth.</p>
  </header>
  <main>
    <section aria-label="Production workflow">
      <h2>BODY LORA PRODUCTION WORKFLOW</h2>
      <p class="meta">ComfyUI: dataset generation, pose control, evaluation, contact sheets. Training: AI Toolkit or Kohya/sd-scripts on RunPod.</p>
      <div class="stats">
        <span>Selected: <strong>{len(DATASET_SELECTED)}</strong></span>
        <span>Gold: <strong>{len(DATASET_GOLD)}</strong></span>
        <span>Needs fix: <strong>{len(DATASET_NEEDS_FIX)}</strong></span>
        <span>Rejected: <strong>{len(DATASET_REJECTED)}</strong></span>
      </div>
      <p class="meta">Triggers: face <code>bk_bini_teen</code> · body <code>bk_bini_body</code> · braces <code>bk_bini_braces</code></p>
      <p class="meta"><a href="reviews/dataset_audit.md">dataset_audit.md</a> · <a href="reviews/training_report.md">training_report.md</a> · <a href="reviews/evaluation_report.md">evaluation_report.md</a></p>
    </section>
    <section aria-label="Training experiments">
      <h2>BODY LORA TRAINING EXPERIMENTS</h2>
      <div class="experiment-grid">
        <a class="experiment" href="training/configs/bk_bini_body_v1_conservative.toml"><strong>bk_bini_body_v1_conservative</strong><span>rank 16 · alpha 16 · 1200-1600 steps · text encoder off</span></a>
        <a class="experiment" href="training/configs/bk_bini_body_v1_standard.toml"><strong>bk_bini_body_v1_standard</strong><span>rank 32 · alpha 32 · 1800-2400 steps · text encoder off initially</span></a>
        <a class="experiment" href="training/configs/bk_bini_braces_v1.toml"><strong>bk_bini_braces_v1</strong><span>visible braces/crutches subset · rank 16 or 32 · 1200-1800 steps</span></a>
      </div>
      <div class="contact-sheets">
{comparison_sheets}
      </div>
    </section>
    <section aria-label="Body LoRA v1 conservative evaluation">
      <h2>BODY LORA V1 CONSERVATIVE EVALUATION</h2>
      <p class="meta">LoRA: <code>{CONSERVATIVE_LORA_NAME}</code> · config: rank 16, alpha 16, lr 8e-5, text encoder off, 1024 resolution, checkpoints every 250 steps, target 1600 steps.</p>
      <p class="meta"><a href="reviews/bk_bini_body_v1_conservative_training_report.md">bk_bini_body_v1_conservative_training_report.md</a></p>
      <div class="contact-sheets">
{conservative_sheet}
      </div>
      <div class="grid">
{conservative_cards}
      </div>
    </section>
    <section aria-label="Body LoRA v1 evaluation">
      <h2>BODY LORA V1 EVALUATION</h2>
      <p class="meta">LoRA: <code>{LORA_NAME}</code> · training set: {len(DATASET_SELECTED)} selected images · trigger: <code>bk_bini_body</code>. Use <code>bk_bini_teen</code> only when combining with the face LoRA at evaluation time.</p>
      <div class="contact-sheets">
{eval_sheet}
      </div>
      <div class="grid">
{eval_cards}
      </div>
    </section>
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
