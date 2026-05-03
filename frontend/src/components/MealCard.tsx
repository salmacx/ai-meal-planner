import { useState } from "react";

const MealCard = ({ title, meal }: any) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="meal">
      <p onClick={() => setOpen(!open)}>
        <strong>{title}:</strong> {meal.name}
      </p>

      {open && (
        <div className="meal-details">
          <p>Ingredients:</p>
          <ul>
            {meal.ingredients.map((ing: string, i: number) => (
              <li key={i}>{ing}</li>
            ))}
          </ul>

          <p>Steps:</p>
          <ol>
            {meal.steps.map((step: string, i: number) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

export default MealCard;