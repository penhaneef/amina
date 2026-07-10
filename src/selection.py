from __future__ import annotations

"""Pantry selection state helpers for Streamlit.

Streamlit widgets with a ``key`` own that key in ``st.session_state``.
If you also keep a separate ``selected`` set and only update one side
(e.g. quick-pick buttons touch ``selected`` but not checkbox keys), the
next rerun (slider, filter, etc.) will fight itself and un-pick items.

Rule: checkbox keys are the source of truth; ``selected`` is derived.
"""

from typing import Iterable, Set

import streamlit as st

CHECKBOX_PREFIX = "ing_"


def checkbox_key(ingredient: str) -> str:
    return f"{CHECKBOX_PREFIX}{ingredient}"


def ensure_checkbox_keys(all_ingredients: Iterable[str], selected: Set[str]) -> None:
    """Create missing keys only — never overwrite existing widget state."""
    selected_set = set(selected)
    for ingredient in all_ingredients:
        key = checkbox_key(ingredient)
        if key not in st.session_state:
            st.session_state[key] = ingredient in selected_set


def sync_checkbox_keys(all_ingredients: Iterable[str], selected: Set[str]) -> None:
    """Force every checkbox key to match ``selected`` (programmatic updates only)."""
    selected_set = set(selected)
    for ingredient in all_ingredients:
        st.session_state[checkbox_key(ingredient)] = ingredient in selected_set


def selected_from_keys(all_ingredients: Iterable[str]) -> Set[str]:
    """Read pantry from checkbox keys (works even if some boxes were not rendered)."""
    return {
        ingredient
        for ingredient in all_ingredients
        if st.session_state.get(checkbox_key(ingredient), False)
    }


def set_selected(all_ingredients: Iterable[str], new_selected: Set[str]) -> Set[str]:
    """Write pantry via keys + derived set. Call only before ingredient checkboxes run."""
    known = set(all_ingredients)
    cleaned = {item for item in new_selected if item in known}
    sync_checkbox_keys(known, cleaned)
    st.session_state.selected = cleaned
    return cleaned


def sanitize_pantry(raw: Iterable[str], all_ingredients: Iterable[str]) -> Set[str]:
    """Drop unknown IDs from URL / saved pantry."""
    known = set(all_ingredients)
    return {item for item in raw if item in known}


def rebuild_selected(all_ingredients: Iterable[str]) -> Set[str]:
    """Derive ``session_state.selected`` from keys after widgets have run."""
    selected = selected_from_keys(all_ingredients)
    st.session_state.selected = selected
    return selected
