import MealCard from "./MealCard";

const MealPlan = () => {
  const plan = [
    {
      day: 1,
      breakfast: {
        name: "Oatmeal",
        ingredients: ["oats", "milk", "banana"],
        steps: ["Boil oats", "Add milk", "Top with banana"],
      },
      lunch: {
        name: "Vegetable Pasta",
        ingredients: ["pasta", "tomato", "zucchini"],
        steps: ["Cook pasta", "Cook vegetables", "Mix"],
      },
      dinner: {
        name: "Rice with tofu",
        ingredients: ["rice", "tofu", "soy sauce"],
        steps: ["Cook rice", "Fry tofu", "Combine"],
      },
    },
  ];

  return (
    <div>
      <h2>Your Meal Plan</h2>

      {plan.map((day) => (
        <div key={day.day} className="day">
          <h3>Day {day.day}</h3>

          <MealCard title="Breakfast" meal={day.breakfast} />
          <MealCard title="Lunch" meal={day.lunch} />
          <MealCard title="Dinner" meal={day.dinner} />
        </div>
      ))}
    </div>
  );
};

export default MealPlan;