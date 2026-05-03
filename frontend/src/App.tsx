import { useState } from "react";
import InputForm from "./components/InputForm";
import MealPlan from "./components/MealPlan";
import "./App.css";

function App() {
  const [mealPlan, setMealPlan] = useState(null);

  return (
    <div className="container">
      <div className="left">
        <InputForm setMealPlan={setMealPlan} />
      </div>

      <div className="right">
        <MealPlan mealPlan={mealPlan} />
      </div>
    </div>
  );
}

export default App;