import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

def generate_food_similarity_2(state: AgentState):
    print("---GENERATE FOOD SIMILARITY---")
    meals_to_generate = state.get("meals_to_generate", ["sáng"])
    user_profile = state["user_profile"]
    meal_old = state["meal_old"]

    suggested_meals = []
    food_name_text = ", ".join([meal['name'] for meal in meal_old])

    all_tags = [
        tag
        for meal in meal_old
        for tag in meal.get("tags", [])
        if isinstance(tag, str)
    ]
    unique_tags = list(set(all_tags))
    food_tag_text = ", ".join(unique_tags)

    meals_text = ", ".join(meals_to_generate)

    query = (
        f"Tìm món ăn ưu tiên các món có tags: {food_tag_text}. "
        f"Phù hợp khẩu phần: {user_profile['khẩu phần']}, "
        f"phục vụ cho bữa {meals_text}."
    )

    print("Query: " + query)

    foods = food_retriever.invoke(query)
    print(f"🔍 Kết quả truy vấn: ")
    for i, food in enumerate(foods):
        print(f"{i} - {food.metadata['name']}")
        suggested_meals.append(food.metadata)

    return {"suggested_meals": suggested_meals}