import os
import shutil
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _bootstrap() -> None:
    """Clear stale bytecode once per process so Streamlit never loads old .pyc.

    Always wipe ``__pycache__`` once at startup (fixes ImportError after edits).
    Full ``sys.modules`` purge is DEV-only (``AMINA_DEV=1``) for aggressive
    hot-reload; ``start.ps1`` sets that locally.
    """
    if os.environ.get("AMINA_BOOTSTRAPPED"):
        return
    for cache_dir in _ROOT.rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)
    if os.environ.get("AMINA_DEV", "").strip() in {"1", "true", "TRUE", "yes", "YES"}:
        for module_name in list(sys.modules):
            if module_name == "src" or module_name.startswith("src."):
                del sys.modules[module_name]
    os.environ["AMINA_BOOTSTRAPPED"] = "1"


_bootstrap()

import streamlit as st

from src.brand import APP_NAME, FAVICON_PATH, TAGLINE
from src.data_loader import IMAGES_DIR, get_ingredient_config, get_recipes
from src.matcher import assistant_message, score_and_bucket
from src.pantry import load_saved_pantry, save_pantry
from src.selection import (
    checkbox_key,
    ensure_checkbox_keys,
    rebuild_selected,
    sanitize_pantry,
    set_selected,
)
from src.shopping_list import collect_shopping_by_recipe, collect_shopping_items
from src.ui import (
    display_name,
    inject_styles,
    render_assistant_box,
    render_excluded,
    render_featured_recipe,
    render_footer,
    render_hero,
    render_shopping_list,
    render_tier_section,
)

_page_icon = str(FAVICON_PATH) if FAVICON_PATH.exists() else "🍲"

st.set_page_config(
    page_title=f"{APP_NAME} — {TAGLINE}",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

RECIPES = get_recipes()
CONFIG = get_ingredient_config()
CARBS = set(CONFIG["carbs"])
PROTEINS = set(CONFIG["proteins"])
MEAT = set(CONFIG["meat"])
QUICK_PICKS = CONFIG["quick_picks"]
CATEGORIES = CONFIG["categories"]
DISPLAY_NAMES = CONFIG.get("display_names", {})
GLOBAL_SUBSTITUTES = CONFIG["global_substitutes"]

# Default 60 so everyday plates (stew ~40–50 min) are not hidden on first load.
DEFAULT_MAX_TIME = 60

# Every selectable ingredient (checkbox keys must cover this whole set).
ALL_INGREDIENTS: set[str] = set(QUICK_PICKS)
for _cat_items in CATEGORIES.values():
    ALL_INGREDIENTS.update(_cat_items)

# Guard against accidental duplicate labels across categories (duplicate keys crash Streamlit).
_seen_labels: dict[str, str] = {}
for _category, _items in CATEGORIES.items():
    for _ingredient in _items:
        if _ingredient in _seen_labels and _seen_labels[_ingredient] != _category:
            raise RuntimeError(
                f"Ingredient '{_ingredient}' appears in both "
                f"'{_seen_labels[_ingredient]}' and '{_category}' — checkbox keys would clash."
            )
        _seen_labels[_ingredient] = _category


def init_state() -> None:
    if "selected" not in st.session_state:
        loaded = sanitize_pantry(load_saved_pantry(), ALL_INGREDIENTS)
        st.session_state.selected = loaded
        # First visit: seed keys from URL pantry (programmatic write is OK here).
        set_selected(ALL_INGREDIENTS, loaded)
    if "seen_onboarding" not in st.session_state:
        st.session_state.seen_onboarding = False
    # Filter widget defaults (keys match widget keys below).
    st.session_state.setdefault("time", DEFAULT_MAX_TIME)
    st.session_state.setdefault("no_meat", False)
    st.session_state.setdefault("kids", False)
    st.session_state.setdefault("budget", False)
    st.session_state.setdefault("ramadan", False)
    # Missing keys only — never overwrite (would swallow user clicks).
    ensure_checkbox_keys(ALL_INGREDIENTS, st.session_state.selected)


def toggle_ingredient(ingredient: str) -> None:
    current = set(st.session_state.selected)
    if ingredient in current:
        current.discard(ingredient)
    else:
        current.add(ingredient)
    set_selected(ALL_INGREDIENTS, current)


def reset_filters() -> None:
    # Widget keys are the filters themselves — assign before next render.
    st.session_state.time = DEFAULT_MAX_TIME
    st.session_state.no_meat = False
    st.session_state.kids = False
    st.session_state.budget = False
    st.session_state.ramadan = False


def featured_recipe_of_day():
    """Stable daily pick so empty state feels intentional, not random-flashy."""
    if not RECIPES:
        return None
    index = date.today().toordinal() % len(RECIPES)
    return RECIPES[index]


def _btn_width_kwargs() -> dict:
    """Streamlit 1.58+ prefers width=; fall back for older versions."""
    return {"width": "stretch"}


def render_kitchen() -> dict:
    st.markdown('<p class="kitchen-panel-title">Quick picks</p>', unsafe_allow_html=True)
    st.caption("Tap what you have — fastest way to start.")

    cols = st.columns(3)
    for index, ingredient in enumerate(QUICK_PICKS):
        with cols[index % 3]:
            is_on = ingredient in st.session_state.selected
            if st.button(
                display_name(ingredient, DISPLAY_NAMES),
                key=f"qp_{ingredient}",
                type="primary" if is_on else "secondary",
                **_btn_width_kwargs(),
            ):
                # Programmatic update before checkboxes run this script path + rerun.
                toggle_ingredient(ingredient)
                st.rerun()

    action_left, action_right = st.columns(2)
    with action_left:
        if st.session_state.selected and st.button(
            "Clear all", key="clear", **_btn_width_kwargs()
        ):
            set_selected(ALL_INGREDIENTS, set())
            st.rerun()
    with action_right:
        if st.button("Jollof demo", key="demo", **_btn_width_kwargs()):
            set_selected(
                ALL_INGREDIENTS,
                {"rice", "tomatoes", "onions", "peppers", "vegetable oil", "chicken"},
            )
            st.rerun()

    pantry_left, pantry_right = st.columns(2)
    with pantry_left:
        if st.button("💾 Save kitchen", key="save_pantry", **_btn_width_kwargs()):
            # Rebuild from keys first so we never save a stale set.
            save_pantry(rebuild_selected(ALL_INGREDIENTS))
            st.success("Kitchen saved in this browser (bookmark the page to keep it).")
    with pantry_right:
        if st.button("📂 Load kitchen", key="load_pantry", **_btn_width_kwargs()):
            loaded = sanitize_pantry(load_saved_pantry(), ALL_INGREDIENTS)
            set_selected(ALL_INGREDIENTS, loaded)
            if loaded:
                st.rerun()
            else:
                st.info("Nothing saved yet — tick ingredients and press Save kitchen.")

    st.divider()
    st.markdown('<p class="kitchen-panel-title">All ingredients</p>', unsafe_allow_html=True)

    search = st.text_input(
        "Search ingredients",
        placeholder="e.g. rice, pepper, palm oil…",
        key="search",
    ).strip().lower()

    # Checkboxes own their keys. Do NOT pass value=. Do NOT add/discard in the loop
    # based only on visible rows (search would wipe hidden selections).
    for category, ingredients in CATEGORIES.items():
        visible = [
            item for item in sorted(ingredients)
            if not search
            or search in item
            or search in display_name(item, DISPLAY_NAMES).lower()
        ]
        if not visible:
            continue
        with st.expander(category, expanded=bool(search)):
            for ingredient in visible:
                st.checkbox(
                    display_name(ingredient, DISPLAY_NAMES),
                    key=checkbox_key(ingredient),
                )

    # Single source of truth: derive pantry from ALL keys (rendered or not).
    selected = rebuild_selected(ALL_INGREDIENTS)

    if selected:
        chips = "".join(
            f'<span class="chip">{display_name(item, DISPLAY_NAMES)}</span>'
            for item in sorted(selected)
        )
        st.markdown(f'<div class="chip-row">{chips}</div>', unsafe_allow_html=True)

    st.divider()
    settings_left, settings_right = st.columns([3, 2])
    with settings_left:
        st.markdown('<p class="kitchen-panel-title">Settings</p>', unsafe_allow_html=True)
    with settings_right:
        if st.button("Reset filters", key="reset_filters", **_btn_width_kwargs()):
            reset_filters()
            st.rerun()

    # No value= with key= — key owns the slider state.
    max_time = st.slider("Max cooking time (mins)", 15, 90, step=5, key="time")

    filter_cols = st.columns(2)
    with filter_cols[0]:
        no_meat = st.checkbox("No meat today", key="no_meat")
        kid_friendly = st.checkbox("Good for children", key="kids")
    with filter_cols[1]:
        budget = st.checkbox("Budget-friendly", key="budget")
        ramadan = st.checkbox("Ramadan-friendly", key="ramadan")

    return {
        "no_meat": no_meat,
        "kid_friendly": kid_friendly,
        "budget": budget,
        "ramadan": ramadan,
        "max_time": max_time,
    }


def active_filter_labels(filters: dict) -> list[str]:
    labels = []
    if filters.get("no_meat"):
        labels.append("No meat")
    if filters.get("kid_friendly"):
        labels.append("Child-friendly")
    if filters.get("budget"):
        labels.append("Budget")
    if filters.get("ramadan"):
        labels.append("Ramadan")
    if filters.get("max_time", 90) < 90:
        labels.append(f"≤{filters['max_time']} mins")
    return labels


def render_results(filters: dict) -> None:
    # Always re-derive in case kitchen wasn't the last mutator.
    selected = rebuild_selected(ALL_INGREDIENTS)

    if not selected:
        st.info("Tick ingredients in **My Kitchen** to see what you can cook.")
        st.markdown("**Demo:** tap **Jollof demo** — Jollof appears under **Cook this now**.")
        featured = featured_recipe_of_day()
        if featured:
            render_featured_recipe(featured, IMAGES_DIR)
        return

    filter_labels = active_filter_labels(filters)
    if filter_labels:
        st.caption("Active filters: " + " · ".join(filter_labels))

    available = set(selected)
    buckets, excluded = score_and_bucket(
        RECIPES,
        available,
        filters,
        CARBS,
        PROTEINS,
        MEAT,
        GLOBAL_SUBSTITUTES,
        filters["max_time"],
    )

    ready = buckets["ready_now"]
    almost = buckets["almost_there"]
    shop = buckets["shop_run"]

    headline, detail = assistant_message(ready, almost, shop, available)
    chips = "".join(
        f'<span class="chip">{display_name(item, DISPLAY_NAMES)}</span>'
        for item in sorted(selected)
    )
    render_assistant_box(headline, detail, chips)

    render_excluded(excluded)

    shop_source = almost + shop
    groups = collect_shopping_by_recipe(shop_source, max_recipes=3)
    flat = collect_shopping_items(shop_source, max_recipes=3)
    render_shopping_list(groups, DISPLAY_NAMES, flat_items=flat)

    if not ready and not almost and not shop:
        st.warning("No realistic matches. Add more staples or relax your filters.")
        featured = featured_recipe_of_day()
        if featured:
            render_featured_recipe(featured, IMAGES_DIR)
        return

    render_tier_section(
        "ready_now", ready, available, IMAGES_DIR, GLOBAL_SUBSTITUTES, DISPLAY_NAMES, limit=5,
    )
    render_tier_section(
        "almost_there", almost, available, IMAGES_DIR, GLOBAL_SUBSTITUTES, DISPLAY_NAMES, limit=5,
    )

    if shop:
        with st.expander(f"Needs a shop run ({len(shop)} dishes) — not ready to cook yet"):
            render_tier_section(
                "shop_run", shop, available, IMAGES_DIR, GLOBAL_SUBSTITUTES, DISPLAY_NAMES,
                show_header=False, limit=8,
            )


# ====================== Main ======================
inject_styles()
init_state()
render_hero()

if not st.session_state.seen_onboarding:
    with st.expander("👋 First time here? 20-second guide", expanded=True):
        st.markdown(
            f"""
            1. Tap **quick picks** or search for ingredients you have.
            2. Scroll down (on phone) or look right (on laptop) for suggestions from **{APP_NAME}**.
            3. Cook from **Cook this now** first — open **Details** for amounts and steps.
            4. Optional: **Save kitchen** (stores in this browser’s link — bookmark to keep it).
            """
        )
        if st.button("Got it", key="onboarding_done"):
            st.session_state.seen_onboarding = True
            st.rerun()

kitchen_col, results_col = st.columns([2, 3], gap="large")

with kitchen_col:
    st.markdown('<div class="panel-kitchen">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 🧺 My Kitchen")
        filters = render_kitchen()
    st.markdown("</div>", unsafe_allow_html=True)

with results_col:
    st.markdown('<div class="panel-results">', unsafe_allow_html=True)
    st.markdown('<p class="mobile-section-label">🍲 Your suggestions</p>', unsafe_allow_html=True)
    st.markdown("### 🍲 Suggestions")
    render_results(filters)
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
