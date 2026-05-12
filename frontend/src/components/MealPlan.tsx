import { useState } from "react";

const MealPlan = ({ mealPlan, selectedMeal, setSelectedMeal }: any) => {
  const [closedDays, setClosedDays] = useState<number[]>([]);

  const toggleDay = (index: number) => {
    if (closedDays.includes(index)) {
      setClosedDays(closedDays.filter((dayIndex) => dayIndex !== index));
    } else {
      setClosedDays([...closedDays, index]);
    }
  };

  const getMealName = (meal: any) => {
    return typeof meal === "string" ? meal : meal.name;
  };

  const getMealCalories = (meal: any) => {
    if (typeof meal === "string") return null;
    return meal.calories;
  };

  return (
    <div>
      <h2>Your Meal Plan</h2>

      {!mealPlan && <p>No data yet</p>}

      {mealPlan?.days.map((day: any, index: number) => {
        const isClosed = closedDays.includes(index);

        return (
          <div key={index} className="day">
            <div className="day-header">
              <h3>{day.day}</h3>

              <button className="toggle-btn" onClick={() => toggleDay(index)}>
                {isClosed ? "▼" : "▲"}
              </button>
            </div>

            {!isClosed && (
              <div className="meal-row">
                <div
                  className={`meal-box ${
                    selectedMeal === day.breakfast ? "selected-meal" : ""
                  }`}
                  onClick={() => setSelectedMeal(day.breakfast)}
                >
                  <span className="meal-label">
                    <strong>Breakfast</strong>
                  </span>
                  <p>{getMealName(day.breakfast)}</p>
                  {getMealCalories(day.breakfast) && (
                    <small>{getMealCalories(day.breakfast)} kcal</small>
                  )}
                </div>

                <div
                  className={`meal-box ${
                    selectedMeal === day.lunch ? "selected-meal" : ""
                  }`}
                  onClick={() => setSelectedMeal(day.lunch)}
                >
                  <span className="meal-label">
                    <strong>Lunch</strong>
                  </span>
                  <p>{getMealName(day.lunch)}</p>
                  {getMealCalories(day.lunch) && (
                    <small>{getMealCalories(day.lunch)} kcal</small>
                  )}
                </div>

                <div
                  className={`meal-box ${
                    selectedMeal === day.dinner ? "selected-meal" : ""
                  }`}
                  onClick={() => setSelectedMeal(day.dinner)}
                >
                  <span className="meal-label">
                    <strong>Dinner</strong>
                  </span>
                  <p>{getMealName(day.dinner)}</p>
                  {getMealCalories(day.dinner) && (
                    <small>{getMealCalories(day.dinner)} kcal</small>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default MealPlan;