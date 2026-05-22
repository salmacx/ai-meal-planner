from __future__ import annotations
import concurrent.futures
import json
import logging
from langchain_ollama import ChatOllama
import time
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate


llm = ChatOllama(model="phi3:mini", temperature=0, num_predict=80)
logger = logging.getLogger("meal_planner")

PROMPT = PromptTemplate.from_template(
"""
Return ONLY valid JSON with this structure:
{{ "days": [...] }}

Rules:
- Keep same structure (days → meals)
- Each meal must have: name, ingredients, steps, reason
- Keep meals simple
- Respect diet: {diet_type}
- Avoid: {allergies}
- Avoid repeating: {avoided_meals}

Use these recipes as inspiration. Try to reuse ingredients or meal ideas from them when possible:

{retrieved_recipes}

Input:
{input_plan}
"""
)

parser = JsonOutputParser()

CHAIN = PROMPT | llm | parser

def enrich_plan_with_llm(
    days_payload: list[dict],
    diet_type: str,
    allergies: list[str],
    avoided_meals: list[str],
    recipe_context: list[dict],
    timeout_seconds: int = 20,
) -> tuple[str | None, float]:

    context = [
        {
            "name": r.get("name"),
            "diet": r.get("diet"),
            "tags": r.get("tags", []),
            "ingredients": r.get("ingredients", [])[:5]
        }
        for r in recipe_context[:5]
    ]

    vars = {
        "diet_type": diet_type,
        "allergies": ", ".join(allergies) if allergies else "none",
        "avoided_meals": avoided_meals[:10],
        "input_plan": json.dumps({"days": days_payload}, ensure_ascii=False),
        "retrieved_recipes": json.dumps(context or [], ensure_ascii=False),
    }

    def _invoke() -> dict:
        return CHAIN.invoke(vars)

    logger.info("langchain_chain_execute_start context_recipes=%s", len(recipe_context))
    start = time.time()
    for _ in range(2):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_invoke)
                result = future.result(timeout=timeout_seconds)
                logger.info("langchain_chain_execute_success")
                return result, time.time() - start
        except Exception as exc:
            logger.warning(f"LLM ERROR: {repr(exc)}")
            continue

    logger.error("LLM FAILED COMPLETELY")
    return None, time.time() - start