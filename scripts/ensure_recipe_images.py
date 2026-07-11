"""Ensure every recipe has a local image — try Commons download, then branded fallback."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from download_images import RECIPE_IMAGES, commons_paths, download_file  # noqa: E402
from src.data_loader import IMAGES_DIR, load_recipes  # noqa: E402

# Warm kitchen palette for fallback cards
PALETTES = [
    ((196, 92, 38), (45, 106, 79)),
    ((224, 122, 58), (139, 90, 43)),
    ((45, 106, 79), (196, 92, 38)),
    ((180, 100, 50), (80, 50, 30)),
    ((210, 140, 70), (60, 90, 50)),
]


def fallback_image(dest: Path, title: str, emoji: str, index: int) -> None:
    w, h = 640, 480
    c1, c2 = PALETTES[index % len(PALETTES)]
    img = Image.new("RGB", (w, h), c1)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    # soft circle accent
    draw.ellipse([w - 220, -80, w + 40, 180], fill=(255, 255, 255, 40) if False else (255, 253, 248))
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = font_title
    text = title
    # wrap title
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        if len(trial) > 18 and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    y0 = h // 2 - 20 * len(lines)
    draw.text((40, 80), emoji, font=font_title, fill=(255, 253, 248))
    for i, ln in enumerate(lines[:3]):
        draw.text((40, y0 + i * 44), ln, font=font_title, fill=(255, 253, 248))
    draw.text((40, h - 60), "Amina kitchen", font=font_sub, fill=(255, 243, 230))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dest, "JPEG", quality=85)


def main() -> None:
    IMAGES_DIR.mkdir(exist_ok=True)
    recipes = load_recipes()
    for index, recipe in enumerate(recipes):
        filename = recipe["image"]
        dest = IMAGES_DIR / filename
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"OK  {filename}")
            continue
        commons = RECIPE_IMAGES.get(filename)
        if commons:
            try:
                print(f"DL  {filename} ...", end=" ", flush=True)
                full, thumbs = commons_paths(commons)
                download_file(thumbs + [full], dest)
                print(f"commons ({dest.stat().st_size // 1024} KB)")
                continue
            except Exception as error:
                print(f"fail ({error})")
        print(f"FB  {filename} (branded fallback)")
        fallback_image(dest, recipe["name"], recipe.get("emoji", "🍲"), index)
    print("done")


if __name__ == "__main__":
    main()
