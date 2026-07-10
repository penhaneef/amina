"""Download recipe images from Wikimedia Commons (CC-licensed)."""
from __future__ import annotations

import hashlib
import time
import urllib.parse
import urllib.request
from pathlib import Path

IMAGES_DIR = Path(__file__).parent / "images"

RECIPE_IMAGES = {
    "jollof-rice.jpg": "Nigerian_Jollof_Rice.jpg",
    "egusi-soup.jpg": "Egusi_and_eba.jpg",
    "fish-pepper-soup.jpg": "Nigerian_prepared_Pepper-Soup.jpg",
    "ewa-dodo.jpg": "Ewa_agoyin.jpg",
    "okra-soup.jpg": "Nigerian_Okro_Soup.jpg",
    "suya-chicken.jpg": "Suya_meats.jpg",
    "party-fried-rice.jpg": "African_Fried_Rice_with_Fried_Plantain_and_Beef.jpg",
    "yam-porridge.jpg": "Beef_yam_porridge_with_red_and_green_pepper.jpg",
    "moi-moi.jpg": "Steaming_wrapped_moi_moi.jpg",
    "tuwo-shinkafa.jpg": "Tuwo_shinkafa_made_with_rice.jpg",
    "akara-pap.jpg": "Akara_na_Akamu_(Fried_Bean_cakes_and_Pap).jpg",
}

USER_AGENT = "AminaRecipeApp/1.0 (local MVP; educational use)"
WIDTH = 480


def commons_paths(filename: str) -> tuple[str, list[str]]:
    digest = hashlib.md5(filename.encode("utf-8")).hexdigest()
    encoded = urllib.parse.quote(filename.replace(" ", "_"))
    base = f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[0:2]}/{encoded}"
    thumbs = [
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{digest[0]}/{digest[0:2]}/{encoded}/{w}px-{encoded}"
        for w in (330, 220, 400)
    ]
    return base, thumbs


def download_file(urls: list[str], dest: Path, retries: int = 4) -> None:
    last_error: Exception | None = None
    for url in urls:
        for attempt in range(retries):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = response.read()
                if len(data) < 1000:
                    raise ValueError("Response too small")
                dest.write_bytes(data)
                return
            except Exception as error:
                last_error = error
                if attempt < retries - 1:
                    time.sleep(2 ** (attempt + 1))
        time.sleep(1)
    raise RuntimeError(f"All URLs failed for {dest.name}") from last_error


def main() -> None:
    IMAGES_DIR.mkdir(exist_ok=True)
    for local_name, commons_name in RECIPE_IMAGES.items():
        dest = IMAGES_DIR / local_name
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"Skip {dest.name} (already downloaded)")
            continue
        print(f"Downloading {commons_name} -> {dest.name} ...", end=" ", flush=True)
        full_url, thumb_urls = commons_paths(commons_name)
        download_file(thumb_urls + [full_url], dest)
        print(f"OK ({dest.stat().st_size // 1024} KB)")
        time.sleep(1.5)


if __name__ == "__main__":
    main()