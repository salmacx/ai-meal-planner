import logging
import random
import re
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


def _to_list(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [v.strip() for v in value.split(",") if v.strip()]


def _is_allergy_safe(recipe: dict, allergies: list[str]) -> bool:
    if not allergies:
        return True
    ingredient_text = " ".join(recipe.get("ingredients", [])).lower()
    return not any(a.lower() in ingredient_text for a in allergies)


def _build_rotations(pool: list[dict]) -> dict[str, deque]:
    by_meal: dict[str, list[dict]] = defaultdict(list)
    for recipe in pool:
        tags = {t.lower() for t in recipe.get("tags", [])}
        for meal in ("breakfast", "lunch", "dinner"):
            if meal in tags:
                by_meal[meal].append(recipe)

    for meal in ("breakfast", "lunch", "dinner"):
        if not by_meal[meal]:
            by_meal[meal] = pool[:]
        random.shuffle(by_meal[meal])

    logger.info(
        "meal_pool_counts breakfast=%s lunch=%s dinner=%s",
        len(by_meal["breakfast"]),
        len(by_meal["lunch"]),
        len(by_meal["dinner"]),
    )
    return {meal: deque(items) for meal, items in by_meal.items()}


def _base_meal_key(name: str) -> str:
    tokens = re.findall(r"[a-z]+", name.lower())
    stop = {"with", "and", "the", "style", "bowl", "plate", "salad", "sandwich", "wrap", "pasta", "rice", "noodle", "skillet", "breakfast", "lunch", "dinner"}
    core = [t for t in tokens if t not in stop]
    return " ".join(core[:3]) if core else name.lower()


def _pick_recipe(rotation: deque, used_global: set[str], used_day: set[str], used_global_base: set[str], used_day_base: set[str]) -> dict:
    candidates = list(rotation)
    choice = next((
        r for r in candidates
        if r["name"] not in used_global
        and r["name"] not in used_day
        and _base_meal_key(r["name"]) not in used_global_base
        and _base_meal_key(r["name"]) not in used_day_base
    ), None)
    if choice is None:
        choice = next((r for r in candidates if r["name"] not in used_day and _base_meal_key(r["name"]) not in used_day_base), None)
    if choice is None:
        choice = next((r for r in candidates if r["name"] not in used_day), candidates[0])
    while rotation[0]["name"] != choice["name"]:
        rotation.rotate(-1)
    rotation.rotate(-1)
    return choice


def build_base_plan(recipes: list[dict], number_of_days: int, allergies_input: list[str] | str | None) -> list[dict]:
    allergies = _to_list(allergies_input)
    safe_pool = [r for r in recipes if _is_allergy_safe(r, allergies)]
    pool = safe_pool if safe_pool else recipes

    rotations = _build_rotations(pool)
    used_global: set[str] = set()
    used_global_base: set[str] = set()
    days: list[dict] = []

    for day_index in range(number_of_days):
        day = {"day": f"Day {day_index + 1}"}
        used_day: set[str] = set()
        used_day_base: set[str] = set()
        for meal in ("breakfast", "lunch", "dinner"):
            selected = _pick_recipe(rotations[meal], used_global, used_day, used_global_base, used_day_base)
            used_day.add(selected["name"])
            used_global.add(selected["name"])
            base_key = _base_meal_key(selected["name"])
            used_day_base.add(base_key)
            used_global_base.add(base_key)
            day[meal] = {
                "name": selected["name"],
                "ingredients": selected.get("ingredients", []),
                "steps": selected.get("steps", [])[:6],
            }

        logger.info(
            "day_selected day=%s breakfast=%s lunch=%s dinner=%s",
            day["day"],
            day["breakfast"]["name"],
            day["lunch"]["name"],
            day["dinner"]["name"],
        )
        days.append(day)
    return days