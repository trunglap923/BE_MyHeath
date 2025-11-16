import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

def enrich_meal_plan_with_nutrition(state: AgentState):
    meal_plan = state["meal_plan"]
    suggested_meals = state.get("suggested_meals", [])

     # Map ID → món gốc
    meal_map = {str(m["meal_id"]): m for m in suggested_meals}

    # Những field KHÔNG nhân portion
    skip_scale_fields = {
        "meal_id", "name", "ingredients", "ingredients_text",
        "difficulty", "servings", "cooking_time_minutes"
    }

    enriched_meals = []

    for meal in meal_plan.get("meals", []):
        enriched_items = []

        for item in meal.get("items", []):
            meal_id = str(item["id"])
            portion = float(item["portion"])

            base = meal_map.get(meal_id)

            if base:
                enriched_item = {
                    "id": meal_id,
                    "name": item["name"],
                    "portion": portion
                }

                for key, value in base.items():
                    # Nếu không nhân portion
                    if key in skip_scale_fields:
                        enriched_item[key] = value
                        continue

                    # Nếu là số → nhân portion
                    if isinstance(value, (int, float)):
                        enriched_item[key] = round(value * portion, 4)
                    else:
                        # Các field text, list thì giữ nguyên
                        enriched_item[key] = value

                enriched_items.append(enriched_item)

            else:
                enriched_items.append(item)

        enriched_meals.append({
            "meal_name": meal["meal_name"],
            "items": enriched_items
        })

    meal_plan_day = {
        "meals": enriched_meals,
        "reason": meal_plan.get("reason", "")
    }

    return {
        "meal_plan_day": meal_plan_day
    }