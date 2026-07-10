from __future__ import annotations

from typing import Dict, List, Set, Tuple


def collect_shopping_by_recipe(
    recipes: List[Dict],
    *,
    max_recipes: int = 3,
) -> List[Tuple[str, str, List[str]]]:
    """Return (emoji, name, missing_core_sorted) for top suggested recipes."""
    groups: List[Tuple[str, str, List[str]]] = []
    for recipe in recipes[:max_recipes]:
        missing = sorted(recipe.get("missing_core", set()))
        if not missing:
            continue
        groups.append((recipe.get("emoji", "🍲"), recipe["name"], missing))
    return groups


def collect_shopping_items(recipes: List[Dict], *, max_recipes: int = 3) -> List[str]:
    """Flat deduped missing cores (kept for tests / simple callers)."""
    items: List[str] = []
    seen: Set[str] = set()
    for _, _, missing in collect_shopping_by_recipe(recipes, max_recipes=max_recipes):
        for ingredient in missing:
            if ingredient not in seen:
                seen.add(ingredient)
                items.append(ingredient)
    return items
