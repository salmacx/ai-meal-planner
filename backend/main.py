import json
import os

from fastapi import FastAPI
from ollama import chat
from pydantic import ValidationError

from backend.models.meal_plan_models import DayMealPlan, MealPlanRequest, MealPlanResponse

app = FastAPI()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def build_prompt(request: MealPlanRequest) -> str:
    allergies = ", ".join(request.allergies_or_dislikes) if request.allergies_or_dislikes else "none"

    return f"""
Create a meal plan based on these preferences:

diet_type: {request.diet_type}
budget: {request.budget}
number_of_days: {request.number_of_days}
cooking_time: {request.cooking_time}
allergies_or_dislikes: {allergies}

Output requirements:
- Return ONLY valid JSON.
- JSON must match this exact shape:
{{
  "days": [
    {{
      "day": "Day 1",
      "breakfast": "meal",
      "lunch": "meal",
      "dinner": "meal"
    }}
  ]
}}

Rules:
- Generate exactly {request.number_of_days} days.
- Use "Day 1", "Day 2", etc.
- Each day must include breakfast, lunch, and dinner.
- Meals must respect diet_type, budget, cooking_time, and allergies_or_dislikes.
- Keep meal names simple and realistic.

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
                breakfast="Oatmeal with banana",
                lunch="Grilled veggie wrap",
                dinner="Rice bowl with roasted vegetables",
            )
        )
    return MealPlanResponse(days=days)

def parse_ollama_json(content: str) -> MealPlanResponse:
    """Parses and validates the model JSON response safely."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
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
            messages=[{"role": "system", "content": "Return valid JSON only. No markdown or extra text."},
                      {"role": "user", "content": prompt}],
            format="json",
        )
        content = response["message"]["content"]
        return parse_ollama_json(content)
    except (KeyError, json.JSONDecodeError, ValidationError, TypeError):
        return build_fallback_plan(request.number_of_days)