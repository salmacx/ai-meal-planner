import { useState } from "react";

const InputForm = () => {
  const [form, setForm] = useState({
    diet: "vegetarian",
    budget: "low",
    days: 3,
    cookingTime: "<30",
    allergies: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

 return (
  <div className="form">
    <h2>Create Your Meal Plan</h2>

    <label>Diet Type</label>
    <select name="diet" value={form.diet} onChange={handleChange}>
      <option value="vegetarian">Vegetarian</option>
      <option value="vegan">Vegan</option>
      <option value="omnivore">Omnivore</option>
    </select>

    <label>Budget</label>
    <select name="budget" value={form.budget} onChange={handleChange}>
      <option value="low">Low</option>
      <option value="medium">Medium</option>
      <option value="high">High</option>
    </select>

    <label>Number of Days</label>
    <input
      type="number"
      name="days"
      value={form.days}
      onChange={handleChange}
    />

    <label>Cooking Time</label>
    <select name="cookingTime" value={form.cookingTime} onChange={handleChange}>
      <option value="<30">&lt; 30 min</option>
      <option value="<60">&lt; 60 min</option>
    </select>

    <label>Allergies / Dislikes</label>
    <input
      type="text"
      name="allergies"
      placeholder="e.g. nuts, mushrooms"
      value={form.allergies}
      onChange={handleChange}
    />

    <button>Generate Meal Plan</button>
  </div>
);

};

export default InputForm;