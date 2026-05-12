import json

from backend.models.meal_plan_models import MealPlanResponse


def _clean(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    return cleaned


def parse_and_validate(content, expected_days: int, diet_type: str, allergies: list[str]) -> MealPlanResponse:

    if isinstance(content, dict):
        data = content
    else:
        data = json.loads(_clean(content))

    days = data.get("days", [])

    if not isinstance(days, list) or len(days) == 0:
        raise ValueError("Invalid days structure")

    # fix wrong number of days
    if len(days) != expected_days:
        days = (days * expected_days)[:expected_days]

    allergies_lower = [a.lower() for a in allergies]

    cleaned_days = []

    for idx, day in enumerate(days, start=1):

        # ensure keys exist
        if "breakfast" not in day:
            day["breakfast"] = {}
        if "lunch" not in day:
            day["lunch"] = {}
        if "dinner" not in day:
            day["dinner"] = {}

        # fix meals
        for meal_key in ["breakfast", "lunch", "dinner"]:
            meal = day.get(meal_key, {})

            if not meal.get("name"):
                meal["name"] = f"{meal_key.title()} Meal"

            if not isinstance(meal.get("ingredients"), list):
                meal["ingredients"] = ["Unknown ingredients"]

            if not isinstance(meal.get("steps"), list):
                meal["steps"] = ["Prepare and serve"]

            if not isinstance(meal.get("reason"), str):
                meal["reason"] = "Balanced meal"

            # allergy safety
            full_text = (
                    meal["name"] + " " +
                    " ".join(meal["ingredients"]) + " " +
                    " ".join(meal.get("steps", []))
            ).lower()

            bad = next((a for a in allergies_lower if a in full_text), None)

            if bad:
                meal["name"] = f"{meal_key.title()} Safe Meal"
                meal["ingredients"] = ["Safe ingredients"]
                meal["steps"] = ["Prepare safely"]
                meal["reason"] = "Allergy-safe replacement"

            day[meal_key] = meal

        # create clean day-- fix duplication bug
        cleaned_days.append({
            "day": f"Day {idx}",
            "breakfast": day["breakfast"],
            "lunch": day["lunch"],
            "dinner": day["dinner"],
        })

    data["days"] = cleaned_days

    return MealPlanResponse(**data)