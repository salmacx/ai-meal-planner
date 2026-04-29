import json
import os

from fastapi import FastAPI
from ollama import chat
from pydantic import ValidationError

from backend.models.meal_plan_models import DayMealPlan, MealPlanRequest, MealPlanResponse

app = FastAPI()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def build_prompt(request: MealPlanRequest) -> str:
    """Builds a small prompt from Sprint 1 input fields."""
    return f"""
Create a structured meal plan in JSON only.

User preferences:
- diet_type: {request.diet_type}
- budget: {request.budget}
- number_of_days: {request.number_of_days}
- cooking_time: {request.cooking_time}
- allergies_or_dislikes: {", ".join(request.allergies_or_dislikes) if request.allergies_or_dislikes else "none"}

Rules:
- Return ONLY valid JSON.
- JSON must match this exact shape:
{{
  "days": [
    {{
      "day": "Day 1",
      "breakfast": "...",
      "lunch": "...",
      "dinner": "..."
    }}
  ]
}}
- Generate exactly {request.number_of_days} days.
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
    data = json.loads(content)
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
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )
        content = response["message"]["content"]
        return parse_ollama_json(content)
    except (KeyError, json.JSONDecodeError, ValidationError, TypeError):
        return build_fallback_plan(request.number_of_days)