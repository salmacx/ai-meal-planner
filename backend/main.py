import logging
import os
import random
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.rag_chain import enrich_plan_with_llm
from backend.models.meal_plan_models import DayMealPlan, MealPlanRequest, MealPlanResponse, PreferencesRequest
from backend.tools.MongoMemory import MongoMemory
from backend.tools.json_memory import JsonMemory
from backend.tools.meal_planner import build_base_plan
from backend.tools.recipe_search import search_recipes
from backend.tools.validation import parse_and_validate
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meal_planner")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = MongoMemory(os.getenv("MONGODB_URI"))

json_memory = JsonMemory()


def _response_from_base(days_payload: list[dict]) -> MealPlanResponse:
    return MealPlanResponse(days=[DayMealPlan(**day) for day in days_payload])

def estimate_calories(meal_name: str) -> int:
    meal = meal_name.lower()

    score = 0

    if any(x in meal for x in ["salad", "soup"]):
        score += 300
    if any(x in meal for x in ["rice", "pasta", "noodles"]):
        score += 250
    if any(x in meal for x in ["chicken", "beef", "tofu"]):
        score += 300
    if any(x in meal for x in ["egg", "cheese"]):
        score += 200
    if any(x in meal for x in ["smoothie", "oats"]):
        score += 250

    return score if score > 0 else 450

def add_fallback_calories(plan: MealPlanResponse) -> MealPlanResponse:
    for day in plan.days:
        for meal in [day.breakfast, day.lunch, day.dinner]:
            if meal.calories is None:
                meal.calories = estimate_calories(meal.name)
    return plan

@app.post("/preferences")
def save_preferences(payload: PreferencesRequest):
    return json_memory.save_preferences(payload.diet, payload.allergies)

@app.get("/preferences")
def get_preferences():
    return json_memory.load()

@app.post("/generate-meal-plan", response_model=MealPlanResponse)
def generate_meal_plan(request: MealPlanRequest) -> MealPlanResponse:
    stored = json_memory.load()
    diet = request.diet_type or stored.get("diet") or "omnivore"
    allergies = request.allergies_or_dislikes or stored.get("allergies", [])
    avoided_meals = stored.get("recent_meals", [])

    logger.info("memory_loaded diet=%s allergies=%s avoided_meals=%s", diet, len(allergies), len(avoided_meals))

    recipes = search_recipes(diet, request.cooking_time)
    random.seed(time.time())
    base_days = build_base_plan(recipes, request.number_of_days, allergies)
    base_response = _response_from_base(base_days)

    logger.info("prompt_generation_ready days=%s avoided_meals=%s", len(base_days), len(avoided_meals))
    recipe_context = recipes[:5]
    llm_content, llm_seconds = enrich_plan_with_llm(base_days, diet, allergies, avoided_meals, recipe_context,timeout_seconds=20)

    logger.info("llm_inference_time_seconds=%.2f", llm_seconds)

    if llm_content:
        try:
            llm_response = parse_and_validate(
                llm_content,
                request.number_of_days,
                diet,
                allergies
            )

            # quality check
            def is_real_meal(name: str) -> bool:
                bad = ["breakfast meal", "lunch meal", "dinner meal"]
                return name.lower() not in bad

            good = 0
            total = 0

            for day in llm_response.days:
                for meal in [day.breakfast, day.lunch, day.dinner]:
                    total += 1
                    if is_real_meal(meal.name):
                        good += 1

            score = good / total if total else 0

            # only use llm if it aint trash
            if score >= 0.6:
                final_response = llm_response
                logger.info("llm_used score=%.2f", score)
            else:
                final_response = base_response
                logger.warning("llm_rejected_low_quality score=%.2f", score)

        except Exception as exc:
            logger.warning("LLM parse failed, using fallback: %s", exc)
            final_response = base_response
    else:
        logger.warning("llm_failed_fallback_used")
        final_response = base_response

    meal_names = []
    for day in final_response.days:
        meal_names.extend([day.breakfast.name, day.lunch.name, day.dinner.name])
    json_memory.add_recent_meals(meal_names)

    final_response = add_fallback_calories(final_response)
    memory.save_plan(request.user_id or "user", request.model_dump(), final_response.model_dump())
    return final_response


@app.get("/meal-history")
def meal_history(user_id: str | None = None, limit: int = 5):
    return memory.get_recent_plans(user_id=user_id, limit=limit)