from __future__ import annotations

import unittest

from src.data_loader import load_ingredient_config, load_recipes
from src.matcher import (
    assistant_message,
    calculate_match_score,
    classify_tier,
    score_and_bucket,
)


class MatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recipes = load_recipes()
        cls.config = load_ingredient_config()
        cls.carbs = set(cls.config["carbs"])
        cls.proteins = set(cls.config["proteins"])
        cls.meat = set(cls.config["meat"])
        cls.global_substitutes = cls.config["global_substitutes"]

    def score(self, selected: set[str], recipe_id: str) -> dict:
        recipe = next(item for item in self.recipes if item["id"] == recipe_id)
        return calculate_match_score(recipe, selected, self.carbs, self.proteins, self.global_substitutes)

    def bucket(self, selected: set[str], **filters: bool) -> dict:
        buckets, _ = score_and_bucket(
            self.recipes,
            selected,
            filters,
            self.carbs,
            self.proteins,
            self.meat,
            self.global_substitutes,
            max_time=90,
        )
        return buckets

    def test_beef_only_hides_all_recipes(self) -> None:
        buckets = self.bucket({"beef"})
        self.assertEqual(buckets["ready_now"], [])
        self.assertEqual(buckets["almost_there"], [])
        self.assertEqual(buckets["shop_run"], [])

    def test_jollof_core_is_ready_now(self) -> None:
        selected = {"rice", "tomatoes", "onions", "peppers", "vegetable oil"}
        buckets = self.bucket(selected)
        ready_names = [item["name"] for item in buckets["ready_now"]]
        self.assertIn("Classic Jollof Rice", ready_names)

    def test_jollof_missing_pepper_is_almost_not_ready(self) -> None:
        selected = {"rice", "tomatoes", "onions", "vegetable oil"}
        jollof = self.score(selected, "jollof-rice")
        self.assertEqual(classify_tier(jollof), "almost_there")
        self.assertFalse(jollof["has_core"])

    def test_pumpkin_leaves_substitutes_for_spinach_in_egusi(self) -> None:
        selected = {
            "egusi", "palm oil", "onions", "peppers", "pumpkin leaves", "pounded yam",
        }
        egusi = self.score(selected, "egusi-soup")
        self.assertTrue(egusi["has_core"])

    def test_garri_substitutes_for_okra_soup_swallow(self) -> None:
        selected = {"okra", "palm oil", "onions", "peppers", "spinach", "garri"}
        okra = self.score(selected, "okra-soup")
        self.assertTrue(okra["has_core"])

    def test_no_meat_allows_okra_when_beef_is_optional(self) -> None:
        selected = {"okra", "palm oil", "onions", "peppers", "spinach", "garri"}
        buckets, excluded = score_and_bucket(
            self.recipes,
            selected,
            {"no_meat": True},
            self.carbs,
            self.proteins,
            self.meat,
            self.global_substitutes,
            max_time=90,
        )
        ready_names = [item["name"] for item in buckets["ready_now"]]
        self.assertIn("Okra Soup with Fufu or Garri", ready_names)
        excluded_names = [item["name"] for item in excluded]
        self.assertNotIn("Okra Soup with Fufu or Garri", excluded_names)

    def test_no_meat_filter_excludes_suya(self) -> None:
        selected = {
            "chicken", "peppers", "onions", "suya spice", "tomatoes", "cabbage", "vegetable oil",
        }
        _, excluded = score_and_bucket(
            self.recipes,
            selected,
            {"no_meat": True},
            self.carbs,
            self.proteins,
            self.meat,
            self.global_substitutes,
            max_time=90,
        )
        excluded_names = [item["name"] for item in excluded]
        self.assertIn("Suya-Spiced Grilled Chicken + Salad", excluded_names)

    def test_suya_requires_spice_and_salad_core(self) -> None:
        """Chicken alone must not unlock 'Suya + Salad' without spice and salad veg."""
        weak = self.score({"chicken", "peppers", "onions"}, "suya-chicken")
        self.assertFalse(weak["has_core"])
        self.assertIn("suya spice", weak["missing_core"])
        full = self.score(
            {"chicken", "suya spice", "onions", "peppers", "tomatoes", "cabbage"},
            "suya-chicken",
        )
        self.assertTrue(full["has_core"])

    def test_time_filter_excludes_long_recipes(self) -> None:
        buckets, excluded = score_and_bucket(
            self.recipes,
            {"rice", "pumpkin leaves", "groundnut oil", "onions", "peppers", "beef"},
            {},
            self.carbs,
            self.proteins,
            self.meat,
            self.global_substitutes,
            max_time=40,
        )
        excluded_names = [item["name"] for item in excluded]
        self.assertIn("Tuwo Shinkafa + Miyan Taushe", excluded_names)

    def test_weak_match_not_listed_as_filtered_out(self) -> None:
        """Moi Moi must not appear when user has no beans (staple missing)."""
        buckets, excluded = score_and_bucket(
            self.recipes,
            {"rice", "tomatoes", "onions", "peppers", "chicken"},
            {},
            self.carbs,
            self.proteins,
            self.meat,
            self.global_substitutes,
            max_time=45,
        )
        excluded_names = [item["name"] for item in excluded]
        self.assertNotIn("Moi Moi", excluded_names)
        all_suggested = (
            [item["name"] for item in buckets["ready_now"]]
            + [item["name"] for item in buckets["almost_there"]]
            + [item["name"] for item in buckets["shop_run"]]
        )
        self.assertNotIn("Moi Moi", all_suggested)
        self.assertNotIn("Akara & Pap (Quick Breakfast)", all_suggested)
        for item in excluded:
            self.assertNotEqual(item.get("match_tier"), "hidden")

    def test_moi_moi_needs_beans_staple(self) -> None:
        without_beans = self.score({"onions", "peppers", "vegetable oil", "eggs"}, "moi-moi")
        self.assertFalse(without_beans["has_core_staple"])
        self.assertEqual(classify_tier(without_beans), "hidden")
        with_beans = self.score({"beans", "onions", "peppers", "vegetable oil"}, "moi-moi")
        self.assertTrue(with_beans["has_core_staple"])
        self.assertEqual(classify_tier(with_beans), "ready_now")

    def test_full_match_can_reach_100_percent(self) -> None:
        """Balance bonus only expands the denominator when the recipe can be balanced."""
        full = {
            "rice", "tomatoes", "onions", "peppers",
            "vegetable oil", "chicken", "thyme", "bay leaves", "seasoning cubes",
        }
        jollof = self.score(full, "jollof-rice")
        self.assertEqual(jollof["match_percent"], 100)
        self.assertTrue(jollof["has_balanced_meal"])

    def test_core_only_jollof_is_ready_with_high_percent(self) -> None:
        core_only = {"rice", "tomatoes", "onions", "peppers", "vegetable oil"}
        jollof = self.score(core_only, "jollof-rice")
        self.assertTrue(jollof["has_core"])
        self.assertEqual(classify_tier(jollof), "ready_now")
        # Has rice (carb) but no protein in available → no balance bonus, still fair %.
        self.assertGreaterEqual(jollof["match_percent"], 50)

    def test_assistant_message_for_single_ingredient(self) -> None:
        headline, _ = assistant_message([], [], [], {"beef"})
        self.assertIn("Beef", headline)

    def test_party_fried_rice_accepts_beef_as_chicken_sub(self) -> None:
        selected = {"rice", "vegetable oil", "onions", "peppers", "curry powder", "beef"}
        fried = self.score(selected, "party-fried-rice")
        self.assertTrue(fried["has_core"])

    def test_bucket_sorting_prefers_balanced_meals(self) -> None:
        selected = {
            "rice", "tomatoes", "onions", "peppers", "chicken",
            "vegetable oil", "thyme", "bay leaves", "seasoning cubes",
        }
        buckets = self.bucket(selected)
        self.assertEqual(buckets["ready_now"][0]["id"], "jollof-rice")

    def test_sorts_by_match_percent_within_tier(self) -> None:
        """Higher % match should rank above a lower % with a bigger raw score."""
        selected = {"beans", "beef", "onions", "rice", "tomatoes", "vegetable oil"}
        buckets = self.bucket(selected)
        almost = buckets["almost_there"]
        self.assertGreaterEqual(len(almost), 2)
        percents = [item["match_percent"] for item in almost]
        self.assertEqual(percents, sorted(percents, reverse=True))

    def test_akara_requires_pap_or_bread(self) -> None:
        """Dish is Akara & Pap — side must be modelled, not only mentioned in steps."""
        no_side = self.score(
            {"beans", "onions", "peppers", "vegetable oil"},
            "akara-pap",
        )
        self.assertIn("pap", no_side["missing_core"])
        self.assertFalse(no_side["has_core"])
        with_pap = self.score(
            {"beans", "onions", "peppers", "vegetable oil", "pap"},
            "akara-pap",
        )
        self.assertTrue(with_pap["has_core"])
        with_bread = self.score(
            {"beans", "onions", "peppers", "vegetable oil", "bread"},
            "akara-pap",
        )
        self.assertTrue(with_bread["has_core"])


if __name__ == "__main__":
    unittest.main()