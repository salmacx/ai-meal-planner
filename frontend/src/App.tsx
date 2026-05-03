import { useState } from "react";
import InputForm from "./components/InputForm";
import MealPlan from "./components/MealPlan";
import "./App.css";

function App() {
  const [mealPlan, setMealPlan] = useState(null);

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
        <div className="left">
          <InputForm setMealPlan={setMealPlan} />
        </div>

        <div className="right">
          <MealPlan mealPlan={mealPlan} />
        </div>

        <aside className="sidebar">
          <h3>Your Preferences</h3>
          <p>🥗 Diet: Vegetarian</p>
          <p>💰 Budget: Low</p>
          <p>⏱ Cooking Time: &lt; 30 min</p>
        </aside>
      </main>
    </div>
  );
}

export default App;