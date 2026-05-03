export interface Preferences {
  diet: string;
  budget: string;
  days: number;
  cookingTime: string;
  allergies: string;
}

export interface Meal {
  name: string;
  ingredients: string[];
  steps: string[];
}

export interface DayPlan {
  day: number;
  breakfast: Meal;
  lunch: Meal;
  dinner: Meal;
}

export interface MealPlanResponse {
  plan: DayPlan[];
}