import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

import json

def generate_best_food_choice(state: AgentState):
    print("---GENERATE BEST FOOD CHOICE---")

    user_profile = state["user_profile"]
    food_old = state["food_old"]
    suggested_meals = state["suggested_meals"]

    if not suggested_meals:
        return {"error": "Không có món để chọn"}

    # Chuẩn bị danh sách món đã retriever được
    candidate_text = "\n".join([
        f"- ID: {m['meal_id']}, {m['name']} | "
        f"{m.get('kcal',0)} kcal, {m.get('protein',0)} protein, "
        f"{m.get('lipid',0)} lipid, {m.get('carbohydrate',0)} carbohydrate | "
        f"tags: {', '.join(m.get('tags', []))}"
        for m in suggested_meals
    ])

    # Prompt chọn món tốt nhất
    prompt = f"""
        Bạn là AI chuyên gia dinh dưỡng.

        Nhiệm vụ: Trong danh sách các món sau đây, hãy CHỌN RA 1 MÓN TƯƠNG TỰ NHẤT
        để thay thế món: {food_old['name']}.

        Giá trị dinh dưỡng món cũ:
        - kcal: {food_old['kcal']}
        - protein: {food_old['protein']}
        - lipid: {food_old['lipid']}
        - carbohydrate: {food_old['carbohydrate']}
        - tags: {', '.join(food_old['tags'])}

        Danh sách món gợi ý:
        {candidate_text}

        --- QUY TẮC ---
        1. Chọn món có dinh dưỡng gần nhất với món cũ (±20%).
        2. Ưu tiên món có nhiều tag trùng với món cũ.
        3. Đề xuất khẩu phần (portion) phù hợp để tổng năng lượng món gần với món cũ (ví dụ: 0.5, 1, 1.2).
        4. Chỉ trả JSON duy nhất, không viết gì thêm.

        --- ĐỊNH DẠNG JSON TRẢ VỀ ---
        {{
            "id": <ID>,
            "name": "<Tên món>",
            "portion": số_lượng_khẩu_phần (float)
        }}

        KHÔNG VIẾT GÌ NGOÀI JSON.
    """


    print("---Prompt---")
    print(prompt)

    result = llm.invoke(prompt)
    output = result.content

    # Parse JSON an toàn
    try:
        food_new_raw = json.loads(output)
    except Exception as e:
        print("❌ JSON parse error:", e)
        return {"response": "LLM trả về JSON không hợp lệ", "raw_output": output}

    return {"food_new_raw": food_new_raw}