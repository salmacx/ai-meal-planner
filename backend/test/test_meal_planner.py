import json

from fastapi.testclient import TestClient

from backend.main import app, estimate_calories, add_fallback_calories
from backend.models.meal_plan_models import MealPlanResponse
from backend.tools.meal_planner import build_base_plan
from backend.tools.validation import parse_and_validate


client = TestClient(app)


def test_build_base_plan_returns_correct_number_of_days():
    recipes = [
        {
            "name": "Oatmeal",
            "tags": ["breakfast"],
            "ingredients": ["oats", "banana"],
            "steps": ["Mix ingredients"],
        },
        {
            "name": "Rice Bowl",
            "tags": ["lunch"],
            "ingredients": ["rice", "tofu"],
            "steps": ["Cook rice"],
        },
        {
            "name": "Pasta",
            "tags": ["dinner"],
            "ingredients": ["pasta", "tomato"],
            "steps": ["Cook pasta"],
        },
    ]

    plan = build_base_plan(recipes, 3, [])

    assert len(plan) == 3


def test_build_base_plan_respects_allergies():
    recipes = [
        {
            "name": "Peanut Oatmeal",
            "tags": ["breakfast"],
            "ingredients": ["oats", "peanut"],
            "steps": ["Mix"],
        },
        {
            "name": "Banana Oatmeal",
            "tags": ["breakfast"],
            "ingredients": ["oats", "banana"],
            "steps": ["Mix"],
        },
        {
            "name": "Rice Bowl",
            "tags": ["lunch"],
            "ingredients": ["rice", "tofu"],
            "steps": ["Cook"],
        },
        {
            "name": "Pasta",
            "tags": ["dinner"],
            "ingredients": ["pasta", "tomato"],
            "steps": ["Cook"],
        },
    ]

    plan = build_base_plan(recipes, 1, ["peanut"])

    assert "peanut" not in str(plan).lower()


def test_estimate_calories_returns_positive_number():
    calories = estimate_calories("Chicken Rice Bowl")

    assert calories > 0


def test_add_fallback_calories_adds_missing_calories():
    plan = MealPlanResponse(
        days=[
            {
                "day": "Day 1",
                "breakfast": {
                    "name": "Oatmeal",
                    "ingredients": ["oats"],
                    "steps": ["Cook oats"],
                },
                "lunch": {
                    "name": "Rice Bowl",
                    "ingredients": ["rice"],
                    "steps": ["Cook rice"],
                },
                "dinner": {
                    "name": "Pasta",
                    "ingredients": ["pasta"],
                    "steps": ["Cook pasta"],
                },
            }
        ]
    )

    result = add_fallback_calories(plan)

    assert result.days[0].breakfast.calories is not None
    assert result.days[0].lunch.calories is not None
    assert result.days[0].dinner.calories is not None


def test_parse_and_validate_accepts_valid_json():
    llm_output = json.dumps(
        {
            "days": [
                {
                    "day": "Day 1",
                    "breakfast": {
                        "name": "Oatmeal",
                        "ingredients": ["oats"],
                        "steps": ["Cook oats"],
                    },
                    "lunch": {
                        "name": "Rice Bowl",
                        "ingredients": ["rice"],
                        "steps": ["Cook rice"],
                    },
                    "dinner": {
                        "name": "Pasta",
                        "ingredients": ["pasta"],
                        "steps": ["Cook pasta"],
                    },
                }
            ]
        }
    )

    result = parse_and_validate(llm_output, 1, "omnivore", [])

    assert len(result.days) == 1


def test_generate_meal_plan_endpoint_returns_days():
    response = client.post(
        "/generate-meal-plan",
        json={
            "user_id": "test_user",
            "diet_type": "vegetarian",
            "budget": "low",
            "number_of_days": 1,
            "cooking_time": "<30",
            "allergies_or_dislikes": [],
        },
    )

    assert response.status_code == 200
    assert "days" in response.json()


def test_preferences_endpoint_saves_and_returns_preferences():
    post_response = client.post(
        "/preferences",
        json={
            "diet": "vegan",
            "allergies": ["milk"],
        },
    )

    assert post_response.status_code == 200

    get_response = client.get("/preferences")

    assert get_response.status_code == 200
    assert get_response.json()["diet"] == "vegan"


def test_meal_history_endpoint_returns_list():
    response = client.get("/meal-history?user_id=test_user")

    assert response.status_code == 200
    assert isinstance(response.json(), list)