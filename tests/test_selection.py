from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.selection import (
    checkbox_key,
    sanitize_pantry,
    selected_from_keys,
    sync_checkbox_keys,
)


class SelectionHelpersTests(unittest.TestCase):
    def test_sanitize_drops_unknown(self) -> None:
        known = {"rice", "beans", "onions"}
        raw = {"rice", "uranium", "beans"}
        self.assertEqual(sanitize_pantry(raw, known), {"rice", "beans"})

    def test_checkbox_key_prefix(self) -> None:
        self.assertEqual(checkbox_key("palm oil"), "ing_palm oil")

    def test_selected_from_keys_reads_widget_state(self) -> None:
        fake_state = {
            "ing_rice": True,
            "ing_beans": False,
            "ing_onions": True,
        }
        with patch("src.selection.st") as mock_st:
            mock_st.session_state = fake_state
            result = selected_from_keys(["rice", "beans", "onions"])
        self.assertEqual(result, {"rice", "onions"})

    def test_sync_checkbox_keys_overwrites_all(self) -> None:
        fake_state: dict = {
            "ing_rice": False,
            "ing_beans": True,
        }
        with patch("src.selection.st") as mock_st:
            mock_st.session_state = fake_state
            sync_checkbox_keys(["rice", "beans"], {"rice"})
        self.assertTrue(fake_state["ing_rice"])
        self.assertFalse(fake_state["ing_beans"])

    def test_search_hidden_ingredients_stay_selected_via_keys(self) -> None:
        """Simulates: user picked beans, then searched 'rice' so beans checkbox
        is not rendered — beans must remain selected because key stays True.
        """
        fake_state = {
            "ing_rice": True,
            "ing_beans": True,
            "ing_onions": False,
        }
        with patch("src.selection.st") as mock_st:
            mock_st.session_state = fake_state
            # Only rice is "visible", but rebuild uses ALL keys.
            selected = selected_from_keys(["rice", "beans", "onions"])
        self.assertIn("beans", selected)
        self.assertIn("rice", selected)
        self.assertNotIn("onions", selected)


if __name__ == "__main__":
    unittest.main()
