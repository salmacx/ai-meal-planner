from fastapi import FastAPI

from backend.models.meal_plan_models import DayMealPlan, MealPlanRequest, MealPlanResponse

app = FastAPI()


@app.post("/generate-meal-plan", response_model=MealPlanResponse)
def generate_meal_plan(request: MealPlanRequest) -> MealPlanResponse:
    """
    Accepts user meal preferences and returns a fake meal plan for Sprint 1.
    """
    fake_days: list[DayMealPlan] = []

    for day_number in range(1, request.number_of_days + 1):
        fake_days.append(
            DayMealPlan(
                day=f"Day {day_number}",
                breakfast="Oatmeal with banana",
                lunch="Grilled veggie wrap",
                dinner="Rice bowl with roasted vegetables",
            )
        )

    return MealPlanResponse(days=fake_days)