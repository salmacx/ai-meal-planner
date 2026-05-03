from pydantic import BaseModel


class MealPlanRequest(BaseModel):
    diet_type: str
    budget: str
    number_of_days: int
    cooking_time: str
    allergies_or_dislikes: list[str]


class Meal(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]


class DayMealPlan(BaseModel):
    day: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal


class MealPlanResponse(BaseModel):
    days: list[DayMealPlan]