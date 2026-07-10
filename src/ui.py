from __future__ import annotations

import base64
from pathlib import Path
from typing import Dict, List, Set

import streamlit as st

from src.brand import APP_NAME, ASSISTANT_LABEL, LOGO_PATH, SUBTITLE, TAGLINE
from src.matcher import Tier

TIER_META = {
    "ready_now": {
        "title": "Cook this now",
        "subtitle": "You have the main ingredients — start here.",
        "badge": "Ready",
        "badge_class": "badge-ready",
        "section_class": "tier-ready",
        "card_class": "card-ready",
        "icon": "✅",
    },
    "almost_there": {
        "title": "Almost there",
        "subtitle": "Missing a few staples — still worth considering.",
        "badge": "Almost",
        "badge_class": "badge-almost",
        "section_class": "tier-almost",
        "card_class": "card-almost",
        "icon": "🛒",
    },
    "shop_run": {
        "title": "Needs a shop run",
        "subtitle": "You have a start, but you'll need more before cooking.",
        "badge": "Shop first",
        "badge_class": "badge-shop",
        "section_class": "tier-shop",
        "card_class": "card-shop",
        "icon": "🏪",
    },
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
        .block-container { padding-top: 0.5rem; padding-bottom: 2rem; max-width: 1180px; }
        [data-testid="stSidebar"] { display: none; }
        section[data-testid="stMain"] { padding-left: 0.75rem; padding-right: 0.75rem; }

        .hero-banner {
            background: linear-gradient(120deg, #C45C26 0%, #E07A3A 35%, #2D6A4F 100%);
            border-radius: 18px; padding: 1.15rem 1.35rem; margin-bottom: 1rem;
            color: #FFFDF8; box-shadow: 0 8px 24px rgba(196, 92, 38, 0.25);
        }
        .hero-row {
            display: flex; align-items: center; gap: 1rem;
        }
        .hero-logo {
            width: 72px; height: 72px; border-radius: 16px; object-fit: cover;
            box-shadow: 0 4px 14px rgba(0,0,0,0.18);
            border: 2px solid rgba(255,255,255,0.45); flex-shrink: 0;
            background: #FFFDF8;
        }
        .hero-title {
            font-size: clamp(1.55rem, 4vw, 2.25rem);
            font-weight: 800; margin: 0; line-height: 1.15; color: #FFFDF8;
        }
        .hero-tagline {
            margin: 0.15rem 0 0 0; font-size: 1.05rem; font-weight: 700;
            color: #FFF8F0; opacity: 0.98;
        }
        .hero-sub {
            margin: 0.3rem 0 0 0; font-size: 0.95rem; color: #FFF3E6; opacity: 0.95;
        }
        .hero-pills {
            display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.75rem;
        }
        .hero-pill {
            background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35);
            border-radius: 999px; padding: 0.15rem 0.65rem; font-size: 0.78rem;
        }

        .kitchen-panel {
            background: linear-gradient(180deg, #FFF8F0 0%, #FFFDF9 100%);
            border: 1px solid #E8C4A8; border-radius: 16px;
            padding: 0.25rem 0.75rem 0.75rem 0.75rem;
        }
        .kitchen-panel-title {
            font-size: 1.05rem; font-weight: 800; color: #5C3A2A;
            margin: 0.5rem 0 0.25rem 0;
        }

        .assistant-box {
            background: linear-gradient(135deg, #FFF3E6 0%, #FFE8D6 55%, #E8F5E9 100%);
            border-left: 5px solid #C45C26; border-radius: 14px;
            padding: 1rem 1.2rem; margin-bottom: 1rem; color: #3D2314;
            box-shadow: 0 4px 14px rgba(196, 92, 38, 0.1);
        }
        .chip-row { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.6rem; }
        .chip {
            background: linear-gradient(135deg, #FFE0C2 0%, #FFD4A8 100%);
            color: #5C3A2A; border: 1px solid #E8A87C;
            border-radius: 999px; padding: 0.22rem 0.75rem; font-size: 0.82rem; font-weight: 600;
        }

        .tier-band {
            border-radius: 12px; padding: 0.65rem 0.9rem; margin: 1.1rem 0 0.65rem 0;
        }
        .tier-ready { background: linear-gradient(90deg, #E8F5E9 0%, #F1FAF1 100%); border-left: 5px solid #2D6A4F; }
        .tier-almost { background: linear-gradient(90deg, #FFF8E1 0%, #FFFBF0 100%); border-left: 5px solid #E9A319; }
        .tier-shop { background: linear-gradient(90deg, #FFF0E6 0%, #FFF8F2 100%); border-left: 5px solid #C45C26; }

        .tier-title { font-size: 1.2rem; font-weight: 800; margin: 0; }
        .tier-ready .tier-title { color: #1B4332; }
        .tier-almost .tier-title { color: #9A6F00; }
        .tier-shop .tier-title { color: #8B4513; }
        .tier-sub { color: #6B4C3B; font-size: 0.86rem; margin: 0.1rem 0 0 0; }

        .recipe-card {
            border-radius: 14px; padding: 0.9rem 1rem; margin-bottom: 0.5rem;
            box-shadow: 0 3px 12px rgba(61, 35, 20, 0.08);
        }
        .card-ready { background: #FFFFFF; border: 1px solid #A8D5BA; border-left: 5px solid #2D6A4F; }
        .card-almost { background: #FFFFFF; border: 1px solid #F0D98C; border-left: 5px solid #E9A319; }
        .card-shop { background: #FFFFFF; border: 1px solid #E8C4A8; border-left: 5px solid #C45C26; }

        .recipe-name { font-size: 1.1rem; font-weight: 800; color: #3D2314; margin: 0 0 0.3rem 0; }
        .recipe-meta { color: #6B4C3B; font-size: 0.85rem; margin-bottom: 0.35rem; }
        .recipe-vibe { color: #4A3728; font-style: italic; font-size: 0.9rem; margin-bottom: 0.35rem; }
        .recipe-status { font-size: 0.9rem; }
        .status-ready { color: #2D6A4F; font-weight: 700; }
        .status-almost { color: #B8860B; font-weight: 700; }
        .status-shop { color: #8B5E3C; }
        .badge {
            display: inline-block; border-radius: 999px; padding: 0.14rem 0.6rem;
            font-size: 0.72rem; font-weight: 700; margin-left: 0.4rem;
        }
        .badge-ready { background: #B7E4C7; color: #1B4332; }
        .badge-almost { background: #FFE08A; color: #7A5A00; }
        .badge-shop { background: #FFD4A8; color: #7C4A2D; }

        .footer-note { color: #8B7355; font-size: 0.78rem; margin-top: 2rem; }
        .mobile-section-label { display: none; }

        div[data-testid="stButton"] button {
            border-radius: 999px !important; min-height: 2.35rem; font-weight: 600 !important;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #C45C26, #E07A3A) !important;
            border: none !important; color: white !important;
        }
        div[data-testid="stTabs"] button { font-weight: 700; }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #C45C26 !important; border-bottom-color: #C45C26 !important;
        }

        /* Laptop / desktop: stick only the main kitchen column (not nested recipe cols) */
        @media (min-width: 900px) {
            div[data-testid="stHorizontalBlock"]:has(.panel-results) > div[data-testid="stColumn"]:first-child,
            div[data-testid="stHorizontalBlock"]:has(.panel-results) > div[data-testid="column"]:first-child {
                position: sticky; top: 1rem; align-self: start;
            }
            .panel-results h3 { margin-top: 0; }
        }

        /* Phone / tablet: stack kitchen then suggestions */
        @media (max-width: 899px) {
            .block-container { padding-top: 0.25rem; max-width: 100%; }
            .hero-banner { border-radius: 14px; padding: 1rem 0.9rem; }
            .hero-logo { width: 58px; height: 58px; border-radius: 14px; }
            .hero-row { gap: 0.75rem; }
            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 0.5rem !important;
            }
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
            .mobile-section-label {
                display: block;
                background: linear-gradient(90deg, #E8F5E9, #FFF8E1);
                color: #3D2314; font-weight: 800; font-size: 1rem;
                border-radius: 10px; padding: 0.55rem 0.8rem;
                margin: 0.5rem 0 0.75rem 0;
            }
            .panel-results h3 { display: none; }
            div[data-testid="stButton"] button { min-height: 2.6rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _logo_data_uri() -> str | None:
    if not LOGO_PATH.exists():
        return None
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_hero() -> None:
    logo_uri = _logo_data_uri()
    logo_html = (
        f'<img class="hero-logo" src="{logo_uri}" alt="{APP_NAME} logo" />'
        if logo_uri
        else ""
    )
    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-row">
                {logo_html}
                <div>
                    <p class="hero-title">{APP_NAME}</p>
                    <p class="hero-tagline">{TAGLINE}</p>
                    <p class="hero-sub">{SUBTITLE}</p>
                </div>
            </div>
            <div class="hero-pills">
                <span class="hero-pill">🇳🇬 Nigerian dishes</span>
                <span class="hero-pill">⚡ Quick picks</span>
                <span class="hero-pill">👩🏽‍🍳 Step-by-step</span>
                <span class="hero-pill">🏠 Northern kitchen companion</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assistant_box(headline: str, detail: str, chips_html: str) -> None:
    st.markdown(
        f"""
        <div class="assistant-box">
            <strong>👩🏽‍🍳 {ASSISTANT_LABEL}</strong><br>{headline}<br>
            <span style="font-size:0.92rem;">{detail}</span>
            <div class="chip-row">{chips_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_name(ingredient: str, display_names: Dict[str, str]) -> str:
    return display_names.get(ingredient, ingredient.replace("_", " ").title())


def recipe_image_path(images_dir: Path, recipe: Dict) -> str | None:
    filename = recipe.get("image")
    if not filename:
        return None
    path = images_dir / filename
    return str(path) if path.exists() else None


def status_line(recipe: Dict, tier: Tier) -> str:
    if tier == "ready_now":
        if not recipe["missing"]:
            return "✅ You have everything for this dish."
        extras = ", ".join(item.replace("_", " ").title() for item in sorted(recipe["missing"]))
        return f"✅ Core covered. Optional extras: {extras}"

    missing_core = ", ".join(item.replace("_", " ").title() for item in sorted(recipe["missing_core"]))
    if tier == "almost_there":
        return f"🛒 Pick up: <strong>{missing_core}</strong>"
    return f"🛒 You still need: <strong>{missing_core}</strong>"


def render_recipe_card(recipe: Dict, tier: Tier, show_medal: bool = False) -> None:
    meta = TIER_META[tier]
    medal = "🥇 " if show_medal else ""
    status_class = {"ready_now": "status-ready", "almost_there": "status-almost", "shop_run": "status-shop"}[tier]

    st.markdown(
        f"""
        <div class="recipe-card {meta['card_class']}">
            <p class="recipe-name">{medal}{recipe['emoji']} {recipe['name']}
                <span class="badge {meta['badge_class']}">{meta['badge']}</span>
            </p>
            <p class="recipe-meta">
                {recipe['match_percent']}% match · ⏱️ {recipe['time']} min ·
                👨‍👩‍👧 {recipe['servings']} · 🌶️ {recipe['spice']} · {recipe['region']}
            </p>
            <p class="recipe-vibe">{recipe['vibe']}</p>
            <p class="recipe-status {status_class}">{status_line(recipe, tier)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ingredient_breakdown(
    recipe: Dict,
    available: Set[str],
    global_substitutes: Dict[str, List[str]],
    display_names: Dict[str, str],
) -> None:
    from src.matcher import ingredient_satisfied, recipe_substitute_map

    substitute_map = recipe_substitute_map(recipe, global_substitutes)
    measurements = recipe.get("measurements") or {}

    left, right = st.columns(2)
    with left:
        st.markdown("**Core (must have)**")
        for ingredient in recipe["core_ingredients"]:
            label = display_name(ingredient, display_names)
            amount = measurements.get(ingredient)
            suffix = f" — *{amount}*" if amount else ""
            if ingredient_satisfied(ingredient, available, substitute_map):
                st.markdown(f"✅ {label}{suffix}")
            else:
                st.markdown(f"❌ {label}{suffix}")
    with right:
        st.markdown("**Nice to have**")
        for ingredient in recipe["other_ingredients"]:
            label = display_name(ingredient, display_names)
            amount = measurements.get(ingredient)
            suffix = f" — *{amount}*" if amount else ""
            if ingredient_satisfied(ingredient, available, substitute_map):
                st.markdown(f"✅ {label}{suffix}")
            else:
                st.markdown(f"➖ {label}{suffix}")

    if measurements:
        st.caption("Amounts are approximate home-cook portions for the listed servings.")

    if recipe.get("substitute_hints"):
        st.info("💡 " + " · ".join(recipe["substitute_hints"]))


def render_recipe_steps(recipe: Dict) -> None:
    st.markdown("**How to cook it**")
    for index, step in enumerate(recipe.get("steps", []), start=1):
        st.markdown(f"{index}. {step}")


def render_tier_section(
    tier: Tier,
    recipes: List[Dict],
    available: Set[str],
    images_dir: Path,
    global_substitutes: Dict[str, List[str]],
    display_names: Dict[str, str],
    *,
    show_header: bool = True,
    limit: int = 3,
) -> None:
    if not recipes:
        return

    if show_header:
        meta = TIER_META[tier]
        st.markdown(
            f"""
            <div class="tier-band {meta['section_class']}">
                <p class="tier-title">{meta['icon']} {meta['title']}</p>
                <p class="tier-sub">{meta['subtitle']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for index, recipe in enumerate(recipes[:limit]):
        image_path = recipe_image_path(images_dir, recipe)
        if image_path:
            img_col, text_col = st.columns([1, 2])
            with img_col:
                st.image(image_path, width="stretch")
            with text_col:
                render_recipe_card(recipe, tier, show_medal=(tier == "ready_now" and index == 0))
        else:
            render_recipe_card(recipe, tier, show_medal=(tier == "ready_now" and index == 0))

        # Keyed expanders so open/closed state is not mixed across recipe swaps.
        with st.expander(
            f"Details — {recipe['name']}",
            expanded=(tier == "ready_now" and index == 0),
            key=f"details_{tier}_{recipe.get('id', recipe['name'])}",
        ):
            render_ingredient_breakdown(recipe, available, global_substitutes, display_names)
            render_recipe_steps(recipe)


def render_excluded(excluded: List[Dict]) -> None:
    """Show only near-matches held back by filters (not weak/irrelevant dishes)."""
    if not excluded:
        return
    with st.expander(
        f"Close matches held back by filters ({len(excluded)})",
        expanded=False,
    ):
        st.caption(
            "These dishes fit your ingredients well enough to consider, "
            "but your time or lifestyle filters set them aside."
        )
        for recipe in excluded:
            st.markdown(f"**{recipe['emoji']} {recipe['name']}** — _{recipe['filter_reason']}_")


def render_shopping_list(
    groups: List[tuple],
    display_names: Dict[str, str],
    flat_items: List[str] | None = None,
) -> None:
    """Show missing cores grouped by dish, plus optional market dump list."""
    if not groups:
        return
    total = sum(len(items) for *_, items in groups)
    with st.expander(f"🛒 Shop list by dish ({total} missing cores)", expanded=False):
        st.caption("Each line is what you still need for that meal — pick one dish and shop for it.")
        for emoji, name, items in groups:
            labeled = ", ".join(display_name(item, display_names) for item in items)
            st.markdown(f"**{emoji} For {name}:** {labeled}")
        if flat_items and len(flat_items) > 1:
            st.markdown("---")
            st.caption("All items once (market dump):")
            st.markdown(", ".join(display_name(item, display_names) for item in flat_items))


def render_featured_recipe(recipe: Dict, images_dir: Path) -> None:
    """Empty-state engagement: show one dish to explore without pantry ticks."""
    st.markdown("#### ✨ Try exploring")
    st.caption("Tick ingredients above — or peek at a featured dish to get inspired.")
    image_path = recipe_image_path(images_dir, recipe)
    if image_path:
        col_img, col_text = st.columns([1, 2])
        with col_img:
            st.image(image_path, width="stretch")
        with col_text:
            st.markdown(f"**{recipe['emoji']} {recipe['name']}**")
            st.caption(
                f"⏱️ {recipe['time']} min · 👨‍👩‍👧 {recipe['servings']} · 🌶️ {recipe['spice']}"
            )
            st.write(recipe["vibe"])
    else:
        st.markdown(f"**{recipe['emoji']} {recipe['name']}** — {recipe['vibe']}")
    st.info("Tip: tap **Jollof demo** in My Kitchen for a ready-to-cook example.")


def render_footer() -> None:
    st.markdown(
        f"""
        <p class="footer-note">
        <strong>{APP_NAME}</strong> suggests meals from ingredients you tick — always use your judgment in the kitchen.
        Food photos from <a href="https://commons.wikimedia.org/wiki/Category:Cuisine_of_Nigeria">Wikimedia Commons</a> (CC licenses).
        </p>
        """,
        unsafe_allow_html=True,
    )


__all__ = [
    "display_name",
    "inject_styles",
    "render_assistant_box",
    "render_excluded",
    "render_featured_recipe",
    "render_footer",
    "render_hero",
    "render_shopping_list",
    "render_tier_section",
]