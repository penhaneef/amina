from __future__ import annotations

import unittest

from src.shopping_list import collect_shopping_by_recipe, collect_shopping_items


class ShoppingListTests(unittest.TestCase):
    def test_grouped_by_recipe(self) -> None:
        recipes = [
            {"name": "Classic Jollof Rice", "emoji": "🍚", "missing_core": {"tomatoes", "chicken"}},
            {"name": "Fish Pepper Soup", "emoji": "🐟", "missing_core": {"fish"}},
            {"name": "Ready Dish", "emoji": "✅", "missing_core": set()},
        ]
        groups = collect_shopping_by_recipe(recipes, max_recipes=3)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0][1], "Classic Jollof Rice")
        self.assertEqual(groups[0][2], ["chicken", "tomatoes"])
        self.assertEqual(groups[1][2], ["fish"])

    def test_flat_dedupes(self) -> None:
        recipes = [
            {"name": "A", "emoji": "1", "missing_core": {"onions", "peppers"}},
            {"name": "B", "emoji": "2", "missing_core": {"peppers", "rice"}},
        ]
        flat = collect_shopping_items(recipes, max_recipes=3)
        self.assertEqual(flat, ["onions", "peppers", "rice"])


if __name__ == "__main__":
    unittest.main()
