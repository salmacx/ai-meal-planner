from pydantic import BaseModel


class MealPlanRequest(BaseModel):
    diet_type: str
    budget: str
    number_of_days: int
    cooking_time: str
    allergies_or_dislikes: list[str]


class DayMealPlan(BaseModel):
    day: str
    breakfast: str
    lunch: str
    dinner: str


class MealPlanResponse(BaseModel):
    days: list[DayMealPlan]