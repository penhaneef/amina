from __future__ import annotations

from typing import Dict, List, Literal, Set, Tuple

Tier = Literal["ready_now", "almost_there", "shop_run", "hidden"]

MIN_CORE_RATIO_ALMOST = 0.5
MIN_CORE_MATCH_ALMOST = 2
MAX_MISSING_CORE_ALMOST = 2
MIN_MATCH_PERCENT_ALMOST = 30
# Shop-run is intentionally stricter than "any shared onion/pepper" —
# otherwise Moi Moi appears when the user only has a jollof base.
MIN_CORE_MATCH_SHOP = 2
MIN_CORE_RATIO_SHOP = 0.4
MIN_MATCH_PERCENT_SHOP = 25
MAX_MISSING_CORE_SHOP = 3


def recipe_substitute_map(recipe: Dict, global_substitutes: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """Substitutes are recipe-specific — protein swaps must not leak across dishes."""
    mapping: Dict[str, Set[str]] = {
        ingredient: set(alternatives) for ingredient, alternatives in global_substitutes.items()
    }
    for ingredient, alternatives in recipe.get("substitutes", {}).items():
        mapping.setdefault(ingredient, set()).update(alternatives)
    return mapping


def ingredient_satisfied(ingredient: str, available: Set[str], substitute_map: Dict[str, Set[str]]) -> bool:
    if ingredient in available:
        return True
    for alternative in substitute_map.get(ingredient, set()):
        if alternative in available:
            return True
    return False


def satisfied_ingredients(ingredients: List[str], available: Set[str], substitute_map: Dict[str, Set[str]]) -> Set[str]:
    return {item for item in ingredients if ingredient_satisfied(item, available, substitute_map)}


def recipe_needs_meat(recipe: Dict, meat: Set[str]) -> bool:
    """Only core meat blocks 'no meat today' — optional beef/chicken in other_ingredients is OK."""
    return bool(set(recipe["core_ingredients"]) & meat)


def filter_reason(recipe: Dict, filters: Dict[str, bool], meat: Set[str]) -> str | None:
    if filters.get("no_meat") and recipe_needs_meat(recipe, meat):
        return "Needs chicken or beef"
    if filters.get("kid_friendly") and not recipe.get("kid_friendly"):
        return "Marked as not child-friendly (spice/complexity)"
    if filters.get("budget") and not recipe.get("budget"):
        return "Not tagged as budget-friendly"
    if filters.get("ramadan") and not recipe.get("ramadan"):
        return "Not tagged as Ramadan-friendly"
    return None


def passes_filters(recipe: Dict, filters: Dict[str, bool], meat: Set[str]) -> bool:
    return filter_reason(recipe, filters, meat) is None


def calculate_match_score(
    recipe: Dict,
    available: Set[str],
    carbs: Set[str],
    proteins: Set[str],
    global_substitutes: Dict[str, List[str]],
) -> Dict:
    substitute_map = recipe_substitute_map(recipe, global_substitutes)
    core = list(recipe["core_ingredients"])
    other = list(recipe["other_ingredients"])
    all_ingredients = set(core) | set(other)

    core_met = satisfied_ingredients(core, available, substitute_map)
    other_met = satisfied_ingredients(other, available, substitute_map)
    core_match = len(core_met)
    other_match = len(other_met)

    core_weight = len(core) * 2
    other_weight = len(other)
    max_score = core_weight + other_weight
    score = (core_match * 2) + other_match

    recipe_carbs = all_ingredients & carbs
    recipe_proteins = all_ingredients & proteins
    # Only recipes that *can* be balanced may earn (or expect) the +4 bonus.
    can_be_balanced = bool(recipe_carbs) and bool(recipe_proteins)
    carb_met = {item for item in recipe_carbs if ingredient_satisfied(item, available, substitute_map)}
    protein_met = {item for item in recipe_proteins if ingredient_satisfied(item, available, substitute_map)}
    has_balanced_meal = can_be_balanced and bool(carb_met) and bool(protein_met)
    balanced_bonus = 4 if has_balanced_meal else 0
    score += balanced_bonus

    # Defining staples (carb/protein in core): beans for Moi Moi, rice for jollof, etc.
    core_staples = set(core) & (carbs | proteins)
    if not core_staples:
        has_core_staple = True
    else:
        has_core_staple = any(
            ingredient_satisfied(item, available, substitute_map) for item in core_staples
        )

    effective_max = max_score + (4 if can_be_balanced else 0)
    match_percent = round((score / effective_max) * 100) if effective_max else 0

    missing = {item for item in all_ingredients if not ingredient_satisfied(item, available, substitute_map)}
    missing_core = {item for item in core if not ingredient_satisfied(item, available, substitute_map)}

    substitute_hints: List[str] = []
    for item in sorted(missing_core):
        alternatives = sorted(substitute_map.get(item, set()))
        if alternatives:
            substitute_hints.append(
                f"No {item}? These also work: {', '.join(alternatives)}"
            )

    return {
        **recipe,
        "score": score,
        "match_percent": min(match_percent, 100),
        "core_match_count": core_match,
        "core_total": len(core),
        "missing": missing,
        "missing_core": missing_core,
        "has_core": core_match == len(core),
        "has_core_staple": has_core_staple,
        "has_balanced_meal": has_balanced_meal,
        "substitute_hints": substitute_hints,
    }


def classify_tier(recipe: Dict) -> Tier:
    if recipe["has_core"]:
        return "ready_now"

    # Without a defining carb/protein (e.g. beans for Moi Moi), don't suggest it.
    if not recipe.get("has_core_staple", True):
        return "hidden"

    core_matched = recipe["core_match_count"]
    core_total = recipe["core_total"]
    missing_core_count = len(recipe["missing_core"])
    core_ratio = core_matched / core_total if core_total else 0

    if (
        core_matched >= MIN_CORE_MATCH_ALMOST
        and core_ratio >= MIN_CORE_RATIO_ALMOST
        and missing_core_count <= MAX_MISSING_CORE_ALMOST
        and recipe["match_percent"] >= MIN_MATCH_PERCENT_ALMOST
    ):
        return "almost_there"

    if (
        core_matched >= MIN_CORE_MATCH_SHOP
        and core_ratio >= MIN_CORE_RATIO_SHOP
        and missing_core_count <= MAX_MISSING_CORE_SHOP
        and recipe["match_percent"] >= MIN_MATCH_PERCENT_SHOP
    ):
        return "shop_run"

    return "hidden"


def bucket_recipes(recipes: List[Dict]) -> Dict[Tier, List[Dict]]:
    buckets: Dict[Tier, List[Dict]] = {
        "ready_now": [],
        "almost_there": [],
        "shop_run": [],
        "hidden": [],
    }
    for recipe in recipes:
        buckets[classify_tier(recipe)].append(recipe)

    # Stable within-bucket order (also used when flattening for display).
    for tier in ("ready_now", "almost_there", "shop_run"):
        buckets[tier].sort(key=match_rank_key, reverse=True)
    return buckets


def match_rank_key(recipe: Dict) -> Tuple[int, int, bool]:
    """Sort key: higher match % first, then score, then balanced meal."""
    return (
        int(recipe.get("match_percent", 0)),
        int(recipe.get("score", 0)),
        bool(recipe.get("has_balanced_meal", False)),
    )


def ranked_matches(buckets: Dict[Tier, List[Dict]]) -> List[Dict]:
    """Single list of suggestions ordered strictly by match % (high → low).

    Tier badges stay on each card; ordering ignores tier so an 80% "Almost"
    ranks above a 70% "Ready".
    """
    combined: List[Dict] = []
    for tier in ("ready_now", "almost_there", "shop_run"):
        for recipe in buckets.get(tier, []):
            combined.append({**recipe, "tier": tier})
    combined.sort(key=match_rank_key, reverse=True)
    return combined


def score_and_bucket(
    recipes: List[Dict],
    available: Set[str],
    filters: Dict[str, bool],
    carbs: Set[str],
    proteins: Set[str],
    meat: Set[str],
    global_substitutes: Dict[str, List[str]],
    max_time: int,
) -> Tuple[Dict[Tier, List[Dict]], List[Dict]]:
    """Score recipes, bucket matches, and list only *relevant* filter exclusions.

    Dishes that are ingredient-weak (would be ``hidden``) are not listed under
    "Filtered out" — that section is only for near-matches held back by time
    or lifestyle filters (so Moi Moi never appears just because time filtered it
    when the user has no beans).
    """
    scored = [
        calculate_match_score(recipe, available, carbs, proteins, global_substitutes)
        for recipe in recipes
    ]
    excluded: List[Dict] = []
    eligible: List[Dict] = []
    for recipe in scored:
        tier = classify_tier(recipe)
        # Weak ingredient matches stay invisible — never clutter "Filtered out".
        if tier == "hidden":
            continue

        reason = filter_reason(recipe, filters, meat)
        if reason:
            excluded.append({**recipe, "filter_reason": reason, "match_tier": tier})
            continue
        if recipe["time"] > max_time:
            excluded.append(
                {
                    **recipe,
                    "filter_reason": f"Takes {recipe['time']} mins (your limit is {max_time})",
                    "match_tier": tier,
                }
            )
            continue
        eligible.append(recipe)

    excluded.sort(key=match_rank_key, reverse=True)
    return bucket_recipes(eligible), excluded


def assistant_message(
    ready: List[Dict],
    almost: List[Dict],
    shop: List[Dict],
    selected: Set[str],
) -> Tuple[str, str]:
    if ready:
        complete = [recipe for recipe in ready if not recipe["missing"]]
        if complete:
            return (
                "Oya! You're ready to cook.",
                "You have the main ingredients for at least one full dish. Start with the top pick below.",
            )
        return (
            "Oya! You can start cooking.",
            "Core ingredients are covered. Anything still missing is optional.",
        )

    if almost:
        return (
            "You're close — a small shop run will do.",
            "You have most of the main ingredients. I listed exactly what's still missing.",
        )

    if shop:
        return (
            "You've got a start, but not enough to cook yet.",
            "Add more staples from the missing list below.",
        )

    if len(selected) == 1:
        item = next(iter(selected)).replace("_", " ").title()
        return (
            f"Just {item}? Not enough on its own yet.",
            "Add carbs (rice, beans, yam) and basics like onions and peppers.",
        )

    return (
        "Nothing realistic matches yet.",
        "Add more staples or ease your filters. Try the quick picks to get started.",
    )