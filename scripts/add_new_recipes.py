"""One-shot helper to merge new everyday recipes into recipes.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data" / "recipes.json"

new_recipes = [
    {
        "id": "yam-egg",
        "name": "Yam & Egg Sauce",
        "core_ingredients": ["yam", "eggs", "tomatoes", "onions", "peppers", "vegetable oil"],
        "other_ingredients": ["seasoning cubes", "thyme"],
        "measurements": {
            "yam": "1 medium tuber (about 1 kg)",
            "eggs": "4–6 eggs",
            "tomatoes": "3 medium",
            "onions": "1 large",
            "peppers": "2–3",
            "vegetable oil": "1/3 cup",
            "seasoning cubes": "1 cube",
            "thyme": "1/2 tsp",
        },
        "substitutes": {"yam": ["sweet potato"], "vegetable oil": ["palm oil"]},
        "time": 30,
        "servings": 3,
        "spice": "Medium",
        "vibe": "Weeknight classic. Soft yam with rich tomato-egg sauce — filling without fuss.",
        "emoji": "🥚",
        "image": "yam-egg.jpg",
        "region": "General",
        "kid_friendly": True,
        "budget": True,
        "ramadan": True,
        "steps": [
            "Peel and slice yam. Boil in salted water until just tender. Drain and keep warm.",
            "Blend or chop tomatoes, peppers, and onions.",
            "Heat oil, fry the blend until thick and the raw taste is gone. Season with cubes and thyme.",
            "Crack eggs into the sauce and scramble gently, or fry eggs separately and fold in.",
            "Serve hot sauce over the boiled yam.",
        ],
    },
    {
        "id": "spaghetti",
        "name": "Nigerian Spaghetti",
        "core_ingredients": ["spaghetti", "tomatoes", "onions", "peppers", "vegetable oil"],
        "other_ingredients": ["chicken", "curry powder", "thyme", "seasoning cubes", "carrots", "green beans"],
        "measurements": {
            "spaghetti": "500 g pack",
            "tomatoes": "4 medium or 1 tin paste + 2 fresh",
            "onions": "1 large",
            "peppers": "2–3",
            "vegetable oil": "1/3–1/2 cup",
            "chicken": "300–500 g pieces (optional)",
            "curry powder": "1 tsp",
            "thyme": "1/2 tsp",
            "seasoning cubes": "2 cubes",
            "carrots": "1 medium, diced",
            "green beans": "1/2 cup chopped",
        },
        "substitutes": {"chicken": ["beef", "liver"], "tomatoes": ["tomato paste"]},
        "time": 35,
        "servings": 4,
        "spice": "Medium",
        "vibe": "Crowded-house favourite. Colourful, saucy pasta that disappears from the pot.",
        "emoji": "🍝",
        "image": "spaghetti.jpg",
        "region": "General",
        "kid_friendly": True,
        "budget": True,
        "ramadan": True,
        "steps": [
            "Boil spaghetti in salted water until al dente. Drain and toss with a little oil.",
            "If using chicken, season and fry or boil until cooked. Set aside.",
            "Fry onions in oil, add blended tomatoes and peppers. Cook until thick and oil floats.",
            "Add curry, thyme, seasoning, and optional carrots/green beans. Simmer 5 minutes.",
            "Fold in spaghetti (and chicken). Toss well and serve hot.",
        ],
    },
    {
        "id": "coconut-rice",
        "name": "Coconut Rice",
        "core_ingredients": ["rice", "coconut milk", "onions", "peppers", "vegetable oil"],
        "other_ingredients": ["tomatoes", "curry powder", "thyme", "seasoning cubes", "chicken"],
        "measurements": {
            "rice": "3 cups (uncooked)",
            "coconut milk": "2 cups (or 1 tin + water to make 2 cups)",
            "onions": "1 large",
            "peppers": "2",
            "vegetable oil": "1/4 cup",
            "tomatoes": "2 medium (optional colour)",
            "curry powder": "1 tsp",
            "thyme": "1/2 tsp",
            "seasoning cubes": "2 cubes",
            "chicken": "400 g (optional)",
        },
        "substitutes": {"chicken": ["beef", "fish"], "vegetable oil": ["palm oil"]},
        "time": 45,
        "servings": 4,
        "spice": "Mild",
        "vibe": "Creamy, fragrant rice with a gentle sweetness. Feels special on a Sunday.",
        "emoji": "🥥",
        "image": "coconut-rice.jpg",
        "region": "General / South-South",
        "kid_friendly": True,
        "budget": False,
        "ramadan": True,
        "steps": [
            "Rinse rice. Optionally parboil and drain.",
            "Fry onions (and a little pepper/tomato if using) in oil until soft.",
            "Pour in coconut milk, seasoning, curry, and thyme. Bring to a gentle simmer.",
            "Add rice, stir once, cover and cook on low until liquid is absorbed and rice is tender.",
            "Fluff with a fork. Serve with chicken or stew if you like.",
        ],
    },
    {
        "id": "miyan-kuka",
        "name": "Miyan Kuka + Tuwo",
        "core_ingredients": ["kuka", "rice", "onions", "peppers", "palm oil"],
        "other_ingredients": ["beef", "seasoning cubes", "crayfish", "ginger"],
        "measurements": {
            "kuka": "1–2 cups baobab leaf powder (kuka)",
            "rice": "3 cups soft rice (for tuwo)",
            "onions": "1 large",
            "peppers": "2–3",
            "palm oil": "1/3 cup",
            "beef": "500 g",
            "seasoning cubes": "2 cubes",
            "crayfish": "2 tbsp ground",
            "ginger": "1 small piece",
        },
        "substitutes": {"rice": ["garri", "fufu"], "palm oil": ["groundnut oil"], "beef": ["chicken"]},
        "time": 55,
        "servings": 5,
        "spice": "Medium",
        "vibe": "Northern comfort in a bowl. Earthy kuka soup with soft tuwo — proper home food.",
        "emoji": "🌿",
        "image": "miyan-kuka.jpg",
        "region": "Hausa / Northern",
        "kid_friendly": True,
        "budget": True,
        "ramadan": True,
        "steps": [
            "Boil beef with seasoning and ginger until tender. Reserve stock.",
            "Make tuwo: cook soft rice with extra water, mash until smooth and firm. Keep warm.",
            "In a pot, heat palm oil lightly. Add blended peppers and onions; cook briefly.",
            "Pour in stock. Sprinkle kuka powder while stirring so it does not cake. Simmer until thick and drawy.",
            "Add crayfish and meat. Adjust salt. Serve miyan kuka with tuwo (or garri/fufu).",
        ],
    },
    {
        "id": "white-rice-stew",
        "name": "White Rice & Tomato Stew",
        "core_ingredients": ["rice", "tomatoes", "onions", "peppers", "vegetable oil"],
        "other_ingredients": ["chicken", "thyme", "curry powder", "seasoning cubes", "ginger", "garlic"],
        "measurements": {
            "rice": "3 cups (uncooked)",
            "tomatoes": "5–6 medium or 1 tin paste + fresh tomatoes",
            "onions": "2 medium",
            "peppers": "3–4",
            "vegetable oil": "1/2 cup",
            "chicken": "500 g–1 kg",
            "thyme": "1 tsp",
            "curry powder": "1 tsp",
            "seasoning cubes": "2 cubes",
            "ginger": "1 small piece",
            "garlic": "2–3 cloves",
        },
        "substitutes": {"chicken": ["beef", "fish"], "tomatoes": ["tomato paste"]},
        "time": 50,
        "servings": 4,
        "spice": "Medium",
        "vibe": "Everyday Nigerian plate. Plain rice with deep red stew — always welcome at the table.",
        "emoji": "🍛",
        "image": "white-rice-stew.jpg",
        "region": "General",
        "kid_friendly": True,
        "budget": True,
        "ramadan": True,
        "steps": [
            "Boil rice in salted water until soft and fluffy. Drain if needed and keep warm.",
            "Season chicken with salt, curry, and thyme. Boil or fry until cooked. Reserve stock if boiled.",
            "Blend tomatoes, peppers, onions, ginger, and garlic.",
            "Heat oil, fry the blend until thick, dark red, and oil rises. Season with cubes.",
            "Add chicken and a splash of stock. Simmer 10 minutes. Serve stew over white rice.",
        ],
    },
]


def main() -> None:
    recipes = json.loads(path.read_text(encoding="utf-8"))
    existing = {r["id"] for r in recipes}
    for recipe in new_recipes:
        if recipe["id"] not in existing:
            recipes.append(recipe)
            print("added", recipe["id"])
        else:
            print("skip", recipe["id"])
    path.write_text(json.dumps(recipes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("total", len(recipes))


if __name__ == "__main__":
    main()
