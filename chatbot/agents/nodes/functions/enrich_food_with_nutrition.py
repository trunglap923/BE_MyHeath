import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

def enrich_food_with_nutrition(state: AgentState):
    food_new_raw = state["food_new_raw"]
    suggested_meals = state.get("suggested_meals", [])

     # Map ID → món gốc
    meal_map = {str(m["meal_id"]): m for m in suggested_meals}

    # Những field KHÔNG nhân portion
    skip_scale_fields = {
        "meal_id", "name", "ingredients", "ingredients_text",
        "difficulty", "servings", "cooking_time_minutes"
    }


    meal_id = str(food_new_raw["id"])
    portion = float(food_new_raw["portion"])

    base = meal_map.get(meal_id)

    enriched_food = {}

    if base:
        enriched_food = {
            "id": meal_id,
            "name": food_new_raw["name"],
            "portion": portion
        }

        for key, value in base.items():
            # Nếu không nhân portion
            if key in skip_scale_fields:
                enriched_food[key] = value
                continue

            # Nếu là số → nhân portion
            if isinstance(value, (int, float)):
                enriched_food[key] = round(value * portion, 4)
            else:
                # Các field text, list thì giữ nguyên
                enriched_food[key] = value

        return {"food_new": enriched_food}
    else:
        return {"food_new": food_new_raw}