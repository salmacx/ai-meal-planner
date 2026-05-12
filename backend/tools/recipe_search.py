import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def _time_to_minutes(value: str) -> int | None:
    text = value.strip().lower().replace(" ", "")

    if not text:
        return None

    if text.startswith("<"):
        digits = "".join(ch for ch in text if ch.isdigit())

        return int(digits) if digits else None

    if "-" in text:
        left, right = text.split("-", 1)
        left_num = "".join(ch for ch in left if ch.isdigit())
        right_num = "".join(ch for ch in right if ch.isdigit())
        if left_num and right_num:
            return (int(left_num) + int(right_num)) // 2

    digits = "".join(ch for ch in text if ch.isdigit())


    return int(digits) if digits else None

def search_recipes(diet_type: str, cooking_time: str,  min_results: int = 12) -> list[dict]:

    data_path = Path(__file__).resolve().parents[1] / "data" / "recipes.json"

    with data_path.open("r", encoding="utf-8") as f:

        recipes = json.load(f)

    logger.info("recipes_loaded=%s", len(recipes))

    diet_filter = (diet_type or "").strip().lower()

    time_filter_value = _time_to_minutes(cooking_time or "")

    diet_results = [r for r in recipes if diet_filter in {"", "omnivore"} or r.get("diet", "").lower() == diet_filter]

    if time_filter_value is None:
        filtered = diet_results
    else:
        filtered = []
        for recipe in diet_results:
            recipe_time = _time_to_minutes(recipe.get("cooking_time", ""))
            if recipe_time is None:
                continue
            if abs(recipe_time - time_filter_value) <= 20:
                    filtered.append(recipe)

        if len(filtered) < min_results:
            logger.info("filtered_too_small=%s fallback_to_diet_results=%s", len(filtered), len(diet_results))
            filtered = diet_results if len(diet_results) >= min_results else recipes

    logger.info("filtered_recipe_count=%s", len(filtered))
    return filtered