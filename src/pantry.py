from __future__ import annotations

"""Per-user pantry persistence via URL query params (browser-side).

Never write shared server files — multi-user deploys would cross-contaminate kitchens.
Users can bookmark the page after Save to restore staples on this device/browser.
"""

from typing import Set

import streamlit as st

QUERY_KEY = "pantry"


def load_saved_pantry() -> Set[str]:
    """Restore kitchen from the current URL (set by a previous Save)."""
    raw = st.query_params.get(QUERY_KEY, "")
    if not raw:
        return set()
    if isinstance(raw, list):
        raw = raw[0] if raw else ""
    return {item.strip() for item in str(raw).split(",") if item.strip()}


def save_pantry(selected: Set[str]) -> None:
    """Persist kitchen into the URL so it is per-browser and multi-user safe."""
    if selected:
        st.query_params[QUERY_KEY] = ",".join(sorted(selected))
    elif QUERY_KEY in st.query_params:
        del st.query_params[QUERY_KEY]
