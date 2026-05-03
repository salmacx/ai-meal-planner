import InputForm from "./components/InputForm";
import "./App.css";

function App() {
  return (
    <div className="container">
      <div className="left">
        <InputForm />
      </div>

      <div className="right">
        <h2>Your Meal Plan</h2>
        <p>No data yet</p>
      </div>
    </div>
  );
}

export default App;