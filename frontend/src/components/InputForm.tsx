import { useEffect, useState } from "react";

const InputForm = ({ setMealPlan }: any) => {
  const [form, setForm] = useState({
    diet: "vegetarian",
    budget: "low",
    days: 3,
    cookingTime: "<30",
    allergies: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const userId = "user";

  useEffect(() => {
    fetch(`http://localhost:8000/preferences?user_id=${userId}`)
      .then((res) => {
        if (!res.ok) return null;
        return res.json();
      })
      .then((data) => {
        if (!data) return;

        setForm({
          diet: data.diet_type || "vegetarian",
          budget: data.budget || "low",
          days: data.number_of_days || 3,
          cookingTime: data.cooking_time || "<30",
          allergies: Array.isArray(data.allergies_or_dislikes)
            ? data.allergies_or_dislikes.join(", ")
            : "",
        });
      })
      .catch(() => {
        console.log("No saved preferences found yet.");
      });
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const savePreferences = async () => {
    await fetch("http://localhost:8000/preferences", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
        diet_type: form.diet,
        budget: form.budget,
        number_of_days: form.days,
        cooking_time: form.cookingTime,
        allergies_or_dislikes: form.allergies
          ? form.allergies.split(",").map((item) => item.trim())
          : [],
      }),
    });
  };

  const handleSubmit = async () => {
    if (form.days < 1 || form.days > 7) {
      setError("Number of days must be between 1 and 7");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/generate-meal-plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          diet_type: form.diet,
          budget: form.budget,
          number_of_days: form.days,
          cooking_time: form.cookingTime,
          allergies_or_dislikes: form.allergies
            ? form.allergies.split(",").map((item) => item.trim())
            : [],
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate meal plan");
      }

      const data = await response.json();
      setMealPlan(data);

      await savePreferences();
    } catch (error) {
      setError("Failed to generate meal plan. Please try again.");
    } finally {
      setLoading(false);
    }
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

      <div className="days-control">
        <button
          type="button"
          className="days-btn"
          onClick={() =>
            setForm({ ...form, days: Math.max(1, form.days - 1) })
          }
        >
          −
        </button>

        <span className="days-value">{form.days} days</span>

        <button
          type="button"
          className="days-btn"
          onClick={() =>
            setForm({ ...form, days: Math.min(7, form.days + 1) })
          }
        >
          +
        </button>
      </div>

      <label>Cooking Time</label>
      <select
        name="cookingTime"
        value={form.cookingTime}
        onChange={handleChange}
      >
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

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Generating..." : "Generate Meal Plan"}
      </button>
      {loading && (
        <div className="progress-wrapper">
            <div className="progress-bar"></div>
        </div>
        )}

      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default InputForm;