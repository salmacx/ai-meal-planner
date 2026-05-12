from pydantic import BaseModel, Field
from typing import Literal


class MealPlanRequest(BaseModel):
    diet_type: Literal["omnivore", "vegetarian", "vegan"] = "omnivore"
    budget: str
    number_of_days: int = Field(ge=1, le=14)
    cooking_time: str
    allergies_or_dislikes: list[str] = Field(default_factory=list)
    user_id: str | None = None
    include_history: bool = False

class PreferencesRequest(BaseModel):
        diet: Literal["omnivore", "vegetarian", "vegan"] | None = None
        allergies: list[str] = Field(default_factory=list)


class Meal(BaseModel):
    name: str
    ingredients: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    reason: str | None = None
    calories: int | None = None


class DayMealPlan(BaseModel):
    day: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal


class MealPlanResponse(BaseModel):
    days: list[DayMealPlan]

class StoredMealPlan(BaseModel):
        user_id: str | None = None
        request: MealPlanRequest
        generated_plan: MealPlanResponse
        timestamp: str

