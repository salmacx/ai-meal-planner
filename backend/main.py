import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ollama import chat
from pydantic import ValidationError

from backend.models.meal_plan_models import DayMealPlan, MealPlanRequest, MealPlanResponse
from backend.tools.recipe_search import search_recipes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def build_prompt(request: MealPlanRequest) -> str:
    allergies = ", ".join(request.allergies_or_dislikes) if request.allergies_or_dislikes else "none"

    retrieved_recipes = search_recipes(request.diet_type, request.cooking_time)[:5]

    if retrieved_recipes:
        recipe_context_parts: list[str] = ["Relevant recipes:"]
        for index, recipe in enumerate(retrieved_recipes, start=1):
            recipe_context_parts.append(
                f"- Recipe {index}:\n"
                f"  name: {recipe.get('name', '')}\n"
                f"  ingredients: {', '.join(recipe.get('ingredients', []))}\n"
                f"  steps: {' | '.join(recipe.get('steps', []))}"
            )
        recipe_context = "\n\n".join(recipe_context_parts)
    else:
        recipe_context = "Relevant recipes:\n- None found for the given filters."

    return f"""
Create a meal plan based on these preferences:

diet_type: {request.diet_type}
budget: {request.budget}
number_of_days: {request.number_of_days}
cooking_time: {request.cooking_time}
allergies_or_dislikes: {allergies}

{recipe_context}

You MUST base the generated meals on the provided "Relevant recipes".
Do NOT invent completely unrelated meals.
When possible, reuse and adapt ingredients and steps from the provided recipes.
Do NOT ignore the provided recipes.

Output requirements:
- The "days" array length MUST be exactly {request.number_of_days}.
- Return ONLY valid JSON.
- JSON must match this exact shape:
{{
  "days": [
    {{
      "day": "Day 1",
      "breakfast": {{
        "name": "meal",
        "ingredients": ["item"],
        "steps": [
  "Step 1: Describe the action clearly",
  "Step 2: Continue with the next action",
  "Step 3: Finish the process"
]
      }},
      "lunch": {{
        "name": "meal",
        "ingredients": ["item"],
        "steps": [
  "Step 1: Describe the action clearly",
  "Step 2: Continue with the next action",
  "Step 3: Finish the process"
]
      }},
      "dinner": {{
        "name": "meal",
        "ingredients": ["item"],
        "steps": [
  "Step 1: Describe the action clearly",
  "Step 2: Continue with the next action",
  "Step 3: Finish the process"
]
      }}
    }}
  ]
}}

Rules:
- Generate EXACTLY {request.number_of_days} day objects inside the "days" array.
- Do NOT generate fewer or more than {request.number_of_days} days.
- Use "Day 1", "Day 2", etc.
- Each day must include breakfast, lunch, and dinner.
- Meals must respect diet_type, budget, cooking_time, and allergies_or_dislikes.
- Keep meal names simple and realistic.
- Each meal MUST include 3–6 detailed cooking steps.
- Each step must contain at least 8–12 words.
- Each step must be a full sentence describing a real cooking action.
- Do NOT use vague steps like "cook food" or "prepare ingredients".
- Steps must be realistic, specific, and usable by a beginner.

Strict constraints:
- Do NOT include any ingredients that violate diet_type.
- Do NOT include any ingredients listed in allergies_or_dislikes.
- If unsure, choose safe alternatives.

""".strip()

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
                    "steps": ["Boil oats", "Add milk", "Add banana"],
                },
                lunch={
                    "name": "Grilled veggie wrap",
                    "ingredients": ["tortilla", "bell pepper", "zucchini", "hummus"],
                    "steps": ["Grill vegetables", "Spread hummus on tortilla", "Wrap and serve"],
                },
                dinner={
                    "name": "Rice bowl with roasted vegetables",
                    "ingredients": ["rice", "carrot", "broccoli", "soy sauce"],
                    "steps": ["Cook rice", "Roast vegetables", "Combine and add soy sauce"],
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

    return MealPlanResponse(**data)

@app.post("/generate-meal-plan", response_model=MealPlanResponse)
def generate_meal_plan(request: MealPlanRequest) -> MealPlanResponse:
    """
    Accepts user meal preferences and return structured meal plan JSON.
    """
    prompt = build_prompt(request)

    try:
        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only. No markdown or extra text."},
                {"role": "user", "content": prompt},
            ],
            format="json",
        )
        content = response["message"]["content"]
        return parse_ollama_json(content,request.number_of_days)

    except (KeyError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as e:
        print("ERROR PARSING OLLAMA RESPONSE:", e)
        print("RAW OLLAMA CONTENT:", content if "content" in locals() else "NO CONTENT")
        return build_fallback_plan(request.number_of_days)

@app.get("/test-recipes")
def test_recipes():
    with open("backend/data/recipes.json") as f:
        return json.load(f)


@app.get("/search-test")
def search_test():
    return search_recipes("vegan", "<30 min")