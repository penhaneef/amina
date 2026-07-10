from __future__ import annotations

import unittest

from src.data_loader import IMAGES_DIR, load_ingredient_config, load_recipes


class DataTests(unittest.TestCase):
    def test_all_recipes_have_required_fields(self) -> None:
        required = {
            "id", "name", "core_ingredients", "other_ingredients", "time",
            "servings", "spice", "vibe", "emoji", "image", "steps", "measurements",
        }
        for recipe in load_recipes():
            missing = required - recipe.keys()
            self.assertEqual(missing, set(), f"{recipe.get('name')} missing {missing}")

    def test_measurements_cover_listed_ingredients(self) -> None:
        for recipe in load_recipes():
            measurements = recipe["measurements"]
            listed = set(recipe["core_ingredients"]) | set(recipe["other_ingredients"])
            for ingredient in listed:
                self.assertIn(
                    ingredient,
                    measurements,
                    f"{recipe['name']} missing measurement for {ingredient}",
                )

    def test_recipe_images_exist(self) -> None:
        for recipe in load_recipes():
            path = IMAGES_DIR / recipe["image"]
            self.assertTrue(path.exists(), f"Missing image for {recipe['name']}")

    def test_ingredient_categories_are_non_empty(self) -> None:
        config = load_ingredient_config()
        for category, items in config["categories"].items():
            self.assertGreater(len(items), 0, f"{category} is empty")


if __name__ == "__main__":
    unittest.main()