import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

def generate_food_similarity(state: AgentState):
    print("---GENERATE FOOD SIMILARITY---")
    meals_to_generate = state.get("meals_to_generate", ["sáng"])
    user_profile = state["user_profile"]
    food_old = state["food_old"]

    suggested_meals = []
    meals_text = ", ".join(meals_to_generate)

    query = (
        f"Tìm món ăn tương tự món {food_old['name']} dựa trên: "
        f"kcal ~{food_old['kcal']} (±20%), "
        f"protein ~{food_old['protein']}g (±20%), "
        f"lipid ~{food_old['lipid']}g (±20%), "
        f"carbohydrate ~{food_old['carbohydrate']}g (±20%). "
        f"Ưu tiên các món có tags: {', '.join(food_old['tags'])}. "
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