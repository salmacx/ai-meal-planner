import InputForm from "./components/InputForm";
import MealPlan from "./components/MealPlan";
import "./App.css";

function App() {
  return (
    <div className="container">
      <div className="left">
        <InputForm />
      </div>

      <div className="right">
        <MealPlan />
      </div>
    </div>
  );
}

export default App;