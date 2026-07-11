from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
IMAGES_DIR = APP_DIR / "images"


def load_json(name: str) -> Any:
    with open(DATA_DIR / name, encoding="utf-8") as handle:
        return json.load(handle)


def _file_stamp(name: str) -> float:
    """Bust Streamlit cache when JSON on disk changes (Cloud redeploys + local edits)."""
    path = DATA_DIR / name
    return path.stat().st_mtime if path.exists() else 0.0


@st.cache_data(show_spinner=False)
def load_recipes(_stamp: float = 0.0) -> List[Dict]:
    return load_json("recipes.json")


@st.cache_data(show_spinner=False)
def load_ingredient_config(_stamp: float = 0.0) -> Dict:
    return load_json("ingredients.json")


def get_recipes() -> List[Dict]:
    return load_recipes(_file_stamp("recipes.json"))


def get_ingredient_config() -> Dict:
    return load_ingredient_config(_file_stamp("ingredients.json"))
