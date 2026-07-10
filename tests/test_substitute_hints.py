from __future__ import annotations

import unittest

from src.data_loader import load_ingredient_config, load_recipes
from src.matcher import calculate_match_score


class SubstituteHintTests(unittest.TestCase):
    def test_missing_core_shows_alternative_suggestions(self) -> None:
        config = load_ingredient_config()
        recipe = next(item for item in load_recipes() if item["id"] == "egusi-soup")
        scored = calculate_match_score(
            recipe,
            {"egusi", "palm oil", "onions", "peppers", "garri"},
            set(config["carbs"]),
            set(config["proteins"]),
            config["global_substitutes"],
        )
        hints = " ".join(scored["substitute_hints"])
        self.assertIn("spinach", hints)
        self.assertIn("pumpkin leaves", hints)


if __name__ == "__main__":
    unittest.main()