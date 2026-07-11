"""Audit recipes for name/step vs ingredient gaps and data hygiene."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
recipes = json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))
config = json.loads((ROOT / "data" / "ingredients.json").read_text(encoding="utf-8"))

known: set[str] = set()
for items in config["categories"].values():
    known.update(items)
known.update(config["quick_picks"])
known.update(config["carbs"])
known.update(config["proteins"])

# Map free-text mentions -> canonical ingredient ids (when they should be modelled)
MENTION_MAP = {
    "pap": "pap",
    "ogi": "pap",
    "akamu": "pap",
    "bread": "bread",
    "fufu": "fufu",
    "garri": "garri",
    "eba": "garri",
    "pounded yam": "pounded yam",
    "iyan": "pounded yam",
    "plantain": "plantain",
    "dodo": "plantain",
    "salad": "cabbage",  # proxy for salad veg
    "cabbage": "cabbage",
    "crayfish": "crayfish",
    "stockfish": "stockfish",
    "thyme": "thyme",
    "bay leaves": "bay leaves",
    "bay leaf": "bay leaves",
    "curry": "curry powder",
    "suya spice": "suya spice",
    "suya": "suya spice",
    "ginger": "ginger",
    "garlic": "garlic",
    "spinach": "spinach",
    "pumpkin leaves": "pumpkin leaves",
    "ugwu": "spinach",
    "beef": "beef",
    "chicken": "chicken",
    "fish": "fish",
    "rice": "rice",
    "beans": "beans",
    "eggs": "eggs",
    "egg": "eggs",
    "tomatoes": "tomatoes",
    "tomato": "tomatoes",
    "onions": "onions",
    "onion": "onions",
    "peppers": "peppers",
    "pepper": "peppers",
    "palm oil": "palm oil",
    "vegetable oil": "vegetable oil",
    "groundnut": "groundnut oil",
    "seasoning": "seasoning cubes",
    "stock": None,  # water/stock often generic
    "water": None,
    "salt": None,
    "oil": None,
}


def find_mentions(text: str) -> set[str]:
    text = text.lower()
    found: set[str] = set()
    # longer phrases first
    for phrase in sorted(MENTION_MAP.keys(), key=len, reverse=True):
        if phrase in text:
            canon = MENTION_MAP[phrase]
            if canon:
                found.add(canon)
    return found


print("=== Recipe audit ===\n")
for r in recipes:
    listed = set(r["core_ingredients"]) | set(r["other_ingredients"])
    meas = set((r.get("measurements") or {}).keys())
    name = r["name"]
    body = " ".join(r.get("steps", []) + [r.get("vibe", ""), name])
    mentions = find_mentions(body)
    # Name components that look like dish parts (split on + & / parentheses)
    name_bits = re.split(r"[\+&/(),\-]", name.lower())
    issues: list[str] = []

    missing_meas = listed - meas
    if missing_meas:
        issues.append(f"missing measurements: {sorted(missing_meas)}")

    extra_meas = meas - listed
    if extra_meas:
        issues.append(f"measurements for non-listed: {sorted(extra_meas)}")

    # Mentions in steps/name not in listed ingredients
    for m in sorted(mentions - listed):
        # ignore if any listed is a substitute target that covers it
        issues.append(f"mentions '{m}' but not in core/other ingredients")

    # Substitutes not selectable
    sub_map = dict(r.get("substitutes") or {})
    for ing, alts in sub_map.items():
        for a in alts:
            if a not in known:
                issues.append(f"recipe sub '{a}' for '{ing}' not in kitchen list")

    # Global subs used by recipe ingredients
    for ing in listed:
        for a in config.get("global_substitutes", {}).get(ing, []):
            if a not in known:
                issues.append(f"global sub '{a}' for '{ing}' not in kitchen list")

    # Name promises (e.g. "Soup + Pounded Yam", "Chicken + Salad")
    if "+" in name or " & " in name:
        issues.append("name has compound dish (+ or &) — verify both parts are modelled in core")

    if issues:
        print(f"{r['id']} — {name}")
        for i in issues:
            print(f"  • {i}")
        print(f"  core={r['core_ingredients']}")
        print(f"  other={r['other_ingredients']}")
        print()

print("=== Selectable kitchen gaps for global substitutes ===")
for ing, alts in config.get("global_substitutes", {}).items():
    for a in alts:
        if a not in known:
            print(f"  {ing} -> {a} (not selectable)")
