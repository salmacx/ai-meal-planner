from langchain_ollama import ChatOllama
from backend.tools.recipe_search import search_recipes
import random

llm = ChatOllama(model="llama3.2")


def generate_rag_response(request):
    recipes = search_recipes(request.diet_type, request.cooking_time)

    # filtering out allergies before sending to LLM

    allergies = request.allergies_or_dislikes or []

    if isinstance(allergies, str):
        allergies = [a.strip() for a in allergies.split(",")]

    if allergies:
        recipes = [
            r for r in recipes
            if not any(
                allergy.lower() in ingredient.lower()
                for allergy in allergies
                for ingredient in r.get("ingredients", [])
            )
        ]

    recipes = recipes[:15]
    random.shuffle(recipes)

    if not recipes:
        return """{
      "days": []
    }"""

    context = "\n\n".join(
        f"{r.get('name', '')}\n"
        f"Ingredients: {', '.join(r.get('ingredients', []))}\n"
        f"Steps: {' | '.join(r.get('steps', []))}"
        for r in recipes
    )


    prompt = f"""
You are generating a structured meal plan.

You MUST ONLY use the provided recipes.

STRICT RULES:
- Each meal MUST be based on one of the provided recipes
- Each day MUST use different recipes
- Try to avoid repeating meals where possible
- Prefer variety across days
- If limited recipes, reuse them in different combinations
- You MUST vary meals across days

{context}

STRICT RULES:
- You MUST return ONLY valid JSON
- NO text before or after JSON
- Follow this EXACT structure:

{{
  "days": [
    {{
      "day": "Day 1",
      "breakfast": {{
        "name": "string",
        "ingredients": ["string"],
        "steps": ["string"]
      }},
      "lunch": {{
        "name": "string",
        "ingredients": ["string"],
        "steps": ["string"]
      }},
      "dinner": {{
        "name": "string",
        "ingredients": ["string"],
        "steps": ["string"]
      }}
    }}
  ]
}}

CONSTRAINTS:
- Generate EXACTLY {request.number_of_days} days
- Respect diet: {request.diet_type}
- Respect cooking time: {request.cooking_time}
- Respect allergies: {request.allergies_or_dislikes}
- Each meal MUST have 3–6 detailed steps
- Every meal MUST clearly reuse ingredients from the provided recipes
- Do NOT invent meals outside the provided recipes
- If no relevant recipe exists, reuse the closest one
- Each day MUST use a different combination of recipes
- Try to minimize repetition across the plan
- Reuse recipes in different combinations if needed
- Vary ingredients and preparation slightly for each day
- Rotate between the provided recipes to create diversity

RETURN JSON ONLY.
"""

    response = llm.invoke(prompt)

    return response.content