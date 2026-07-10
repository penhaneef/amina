"""Compress recipe images for faster mobile loading."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"
MAX_WIDTH = 800
QUALITY = 82


def compress(path: Path) -> None:
    with Image.open(path) as image:
        image = image.convert("RGB")
        if image.width > MAX_WIDTH:
            ratio = MAX_WIDTH / image.width
            image = image.resize((MAX_WIDTH, int(image.height * ratio)), Image.Resampling.LANCZOS)
        image.save(path, format="JPEG", optimize=True, quality=QUALITY)
    print(f"{path.name}: {path.stat().st_size // 1024} KB")


def main() -> None:
    for path in sorted(IMAGES_DIR.glob("*.jpg")):
        compress(path)


if __name__ == "__main__":
    main()