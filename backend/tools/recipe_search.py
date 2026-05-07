import json
from pathlib import Path


def search_recipes(diet_type: str, cooking_time: str) -> list[dict]:
    data_path = Path(__file__).resolve().parents[1] / "data" / "recipes.json"
    with data_path.open("r", encoding="utf-8") as f:
        recipes = json.load(f)

    def time_to_minutes(value: str) -> int | None:
        text = value.strip().lower().replace(" ", "")
        if not text:
            return None
        if text.startswith("<"):
            num = "".join(ch for ch in text if ch.isdigit())
            return int(num) if num else None
        if "-" in text:
            left, right = text.split("-", 1)
            left_num = "".join(ch for ch in left if ch.isdigit())
            right_num = "".join(ch for ch in right if ch.isdigit())
            if left_num and right_num:
                return (int(left_num) + int(right_num)) // 2
        num = "".join(ch for ch in text if ch.isdigit())
        return int(num) if num else None

    diet_filter = (diet_type or "").strip().lower()
    time_filter_value = time_to_minutes(cooking_time or "")

    results: list[dict] = []
    for recipe in recipes:
        if diet_filter and diet_filter != "omnivore":
            if recipe.get("diet", "").strip().lower() != diet_filter:
                continue

        if time_filter_value is not None:
            recipe_time_value = time_to_minutes(recipe.get("cooking_time", ""))
            if recipe_time_value is None or abs(recipe_time_value - time_filter_value) > 10:
                continue

        results.append(recipe)

    return results