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


@st.cache_data(show_spinner=False)
def load_recipes() -> List[Dict]:
    return load_json("recipes.json")


@st.cache_data(show_spinner=False)
def load_ingredient_config() -> Dict:
    return load_json("ingredients.json")
