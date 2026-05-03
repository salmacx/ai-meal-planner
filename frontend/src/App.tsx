import { useState } from "react";
import InputForm from "./components/InputForm";
import MealPlan from "./components/MealPlan";
import "./App.css";

function App() {
  const [mealPlan, setMealPlan] = useState(null);
  const [selectedMeal, setSelectedMeal] = useState<string | null>(null);

  return (
    <div className="app">
      <header className="header">
        <h1>🥗 AI Meal Planner</h1>

        <nav>
          <span>Saved Plans</span>
          <span>My Profile</span>
        </nav>
      </header>

      <main className="container">
        <div className="left-column">
          <div className="left">
            <InputForm setMealPlan={setMealPlan} />
          </div>

          <aside className="preferences-box">
            <h3>Your Preferences</h3>
            <p>🥗 Diet: Vegetarian</p>
            <p>💰 Budget: Low</p>
            <p>⏱ Cooking Time: &lt; 30 min</p>
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
    <h4>{selectedMeal}</h4>

    <p className="recipe-section-title">Ingredients</p>
    <ul>
      <li>Ingredient 1</li>
      <li>Ingredient 2</li>
      <li>Ingredient 3</li>
    </ul>

    <p className="recipe-section-title">Steps</p>
    <ol>
      <li>Prepare the ingredients.</li>
      <li>Cook the meal.</li>
      <li>Serve and enjoy.</li>
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