const MealPlan = ({ mealPlan }: any) => {
  return (
    <div>
      <h2>Your Meal Plan</h2>

      {!mealPlan && <p>No data yet</p>}

      {mealPlan?.days.map((day: any, index: number) => (
        <div key={index} className="day">
          <h3>{day.day}</h3>

          <p><strong>Breakfast:</strong> {day.breakfast}</p>
          <p><strong>Lunch:</strong> {day.lunch}</p>
          <p><strong>Dinner:</strong> {day.dinner}</p>
        </div>
      ))}
    </div>
  );
};

export default MealPlan;