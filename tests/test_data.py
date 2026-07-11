from __future__ import annotations

import unittest

from src.data_loader import IMAGES_DIR, get_ingredient_config, get_recipes

# Tests call the stamp-aware loaders (same data as the app).
load_recipes = get_recipes
load_ingredient_config = get_ingredient_config


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

    def test_all_substitutes_are_selectable(self) -> None:
        """Every substitute target must appear in the kitchen ingredient list."""
        config = load_ingredient_config()
        known: set[str] = set()
        for items in config["categories"].values():
            known.update(items)
        known.update(config["quick_picks"])
        known.update(config["carbs"])
        known.update(config["proteins"])

        for ingredient, alts in config["global_substitutes"].items():
            for alt in alts:
                self.assertIn(
                    alt,
                    known,
                    f"global substitute '{alt}' for '{ingredient}' is not selectable",
                )

        for recipe in load_recipes():
            for ingredient, alts in recipe.get("substitutes", {}).items():
                for alt in alts:
                    self.assertIn(
                        alt,
                        known,
                        f"{recipe['name']}: substitute '{alt}' for '{ingredient}' not selectable",
                    )

    def test_compound_name_parts_are_in_core(self) -> None:
        """Dishes named X + Y / X & Y must model both sides in core ingredients."""
        checks = {
            "egusi-soup": {"egusi", "pounded yam"},
            "ewa-dodo": {"beans", "plantain"},
            "suya-chicken": {"chicken", "suya spice", "cabbage", "tomatoes"},
            "tuwo-shinkafa": {"rice", "pumpkin leaves"},
            "akara-pap": {"beans", "pap"},
            "okra-soup": {"okra", "garri"},
            "yam-egg": {"yam", "eggs"},
            "white-rice-stew": {"rice", "tomatoes"},
            "miyan-kuka": {"kuka", "rice"},
        }
        recipes = {item["id"]: item for item in load_recipes()}
        for recipe_id, required in checks.items():
            core = set(recipes[recipe_id]["core_ingredients"])
            self.assertTrue(
                required <= core,
                f"{recipe_id} core missing {required - core}",
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