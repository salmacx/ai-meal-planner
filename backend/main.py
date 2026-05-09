import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.meal_plan_models import DayMealPlan, MealPlanRequest, MealPlanResponse
from backend.tools.recipe_search import search_recipes
from backend.agents.rag_chain import generate_rag_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def build_fallback_plan(number_of_days: int) -> MealPlanResponse:
    """Fallback used when Ollama output is missing/malformed."""
    days: list[DayMealPlan] = []
    for day_number in range(1, number_of_days + 1):
        days.append(
            DayMealPlan(
                day=f"Day {day_number}",
                breakfast={
                    "name": "Oatmeal with banana",
                    "ingredients": ["oats", "milk", "banana"],
                    "steps": [
                        "Boil oats in water or milk until soft and creamy.",
                        "Stir in milk and mix thoroughly until combined.",
                        "Slice banana and add on top before serving."
                    ],
                },
                lunch={
                    "name": "Grilled veggie wrap",
                    "ingredients": ["tortilla", "bell pepper", "zucchini", "hummus"],
                    "steps": [
    "Slice vegetables and grill them in a pan until soft and slightly charred.",
    "Spread hummus evenly across the tortilla surface.",
    "Place grilled vegetables on top, wrap tightly, and serve warm."
],
                },
                dinner={
                    "name": "Rice bowl with roasted vegetables",
                    "ingredients": ["rice", "carrot", "broccoli", "soy sauce"],
                    "steps": [
    "Cook rice according to package instructions until tender and fluffy.",
    "Chop vegetables and roast them in the oven with oil until golden.",
    "Combine cooked rice with roasted vegetables and drizzle with soy sauce before serving."
],
                },
            )
        )
    return MealPlanResponse(days=days)

def parse_ollama_json(content: str, number_of_days: int) -> MealPlanResponse:
    """Parses and validates the model JSON response safely."""

    # this is for clean response, so removing whitespace and markdown
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    data = json.loads(cleaned)

    # checking structure
    days = data.get("days")

    if not isinstance(days, list):
        raise ValueError("Invalid format: 'days' must be a list")

    if len(days) != number_of_days:
        raise ValueError("Wrong number of days returned")

    # checking each day
    for day in days:
        for field in ["day", "breakfast", "lunch", "dinner"]:
            if field not in day:
                raise ValueError(f"Missing field: {field}")

    # checking each meal
        for meal_key in ["breakfast", "lunch", "dinner"]:
            meal = day[meal_key]

            if not isinstance(meal, dict):
                raise ValueError(f"{meal_key} must be an object")

            if "name" not in meal:
                raise ValueError(f"{meal_key} missing name")

            if not isinstance(meal.get("ingredients"), list):
                raise ValueError(f"{meal_key} ingredients must be a list")

            if not isinstance(meal.get("steps"), list):
                raise ValueError(f"{meal_key} steps must be a list")

    # checking duplicates across all days

    seen_meals = set()

    for day in days:
        for meal_key in ["breakfast", "lunch", "dinner"]:
            meal_name = day[meal_key].get("name", "").strip().lower()

            if meal_name in seen_meals:
                continue

            seen_meals.add(meal_name)

    return MealPlanResponse(**data)



@app.post("/generate-meal-plan", response_model=MealPlanResponse)
def generate_meal_plan(request: MealPlanRequest) -> MealPlanResponse:
    """
    Accepts user meal preferences and return structured meal plan JSON.
    """

    try:
        for _ in range(3):  # try up to 3 times
            content = generate_rag_response(request)

            try:
                return parse_ollama_json(content, request.number_of_days)
            except (json.JSONDecodeError, ValueError):
                continue

        # if all retries fail then fallback
        return build_fallback_plan(request.number_of_days)

    except Exception as e:
        print("Unexpected error:", str(e))
        return build_fallback_plan(request.number_of_days)

@app.get("/test-recipes")
def test_recipes():
    with open("backend/data/recipes.json") as f:
        return json.load(f)


@app.get("/search-test")
def search_test():
    return search_recipes("vegan", "<30 min")