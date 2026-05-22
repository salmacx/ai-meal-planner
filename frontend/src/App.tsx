import { useState } from "react";
import InputForm from "./components/InputForm";
import MealPlan from "./components/MealPlan";
import "./App.css";

type SelectedMeal = {
  name: string;
  ingredients: string[];
  steps: string[];
  calories?: number;
};

function App() {
  const [mealPlan, setMealPlan] = useState(null);
  const [selectedMeal, setSelectedMeal] = useState<SelectedMeal | null>(null);

  const [history, setHistory] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const [preferences, setPreferences] = useState({
    diet: "vegetarian",
    budget: "low",
    days: 3,
    cookingTime: "<30",
    allergies: "",
  });

  const loadHistory = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/meal-history?user_id=user"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch history");
      }

      const data = await response.json();
      console.log("HISTORY RESPONSE:", data);

      setHistory(Array.isArray(data) ? data : []);
      setShowHistory(true);
    } catch (error) {
      console.error("Failed to load meal history:", error);
      setHistory([]);
      setShowHistory(true);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🥗 AI Meal Planner</h1>

        <nav>
          <span onClick={loadHistory} style={{ cursor: "pointer" }}>
            Saved Plans
          </span>
          <span>My Profile</span>
        </nav>
      </header>

      {showHistory && (
        <div className="history-panel">
          <div className="history-header">
            <h2>Saved Plans</h2>
            <button onClick={() => setShowHistory(false)}>Close</button>
          </div>

          {history.length === 0 ? (
            <p>No saved plans yet.</p>
          ) : (
            history.map((item: any, index: number) => {
              const plan = item.generated_plan;

              if (!plan?.days) {
                return null;
              }

              return (
                <div key={index} className="history-card">
                  <h3>Plan {index + 1}</h3>

                  {item.timestamp && (
                    <small>
                      {new Date(item.timestamp).toLocaleString()}
                    </small>
                  )}

                  {plan.days.slice(0, 2).map((day: any, dayIndex: number) => (
                    <div key={dayIndex}>
                      <strong>{day.day}</strong>
                      <p>
                        {day.breakfast?.name} / {day.lunch?.name} /{" "}
                        {day.dinner?.name}
                      </p>
                    </div>
                  ))}

                  <button
                    onClick={() => {
                      setMealPlan(plan);
                      setSelectedMeal(null);
                      setShowHistory(false);
                    }}
                  >
                    View This Plan
                  </button>
                </div>
              );
            })
          )}
        </div>
      )}

      <main className="container">
        <div className="left-column">
          <div className="left">
            <InputForm
              setMealPlan={setMealPlan}
              setPreferences={setPreferences}
            />
          </div>

          <aside className="preferences-box">
            <h3>Your Preferences</h3>
            <p>🥗 Diet: {preferences.diet}</p>
            <p>💰 Budget: {preferences.budget}</p>
            <p>📅 Days: {preferences.days}</p>
            <p>⏱ Cooking Time: {preferences.cookingTime}</p>
            <p>
              ⚠️ Allergies:{" "}
              {preferences.allergies ? preferences.allergies : "None"}
            </p>
          </aside>
        </div>

        <div className="right">
          <MealPlan
            mealPlan={mealPlan}
            selectedMeal={selectedMeal}
            setSelectedMeal={setSelectedMeal}
          />
        </div>

        <aside className="recipe-box">
          <h3>Recipe Details</h3>

          {selectedMeal ? (
            <div className="selected-recipe">
              <h4>{selectedMeal.name}</h4>

              {selectedMeal.calories && (
                <p className="recipe-section-title">
                  Calories: {selectedMeal.calories} kcal
                </p>
              )}

              <p className="recipe-section-title">Ingredients</p>
              <ul>
                {selectedMeal.ingredients.map((ing: string, i: number) => (
                  <li key={i}>{ing}</li>
                ))}
              </ul>

              <p className="recipe-section-title">Steps</p>
              <ol>
                {selectedMeal.steps.map((step: string, i: number) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          ) : (
            <p>Select a meal to view recipe details.</p>
          )}
        </aside>
      </main>
    </div>
  );
}

export default App;