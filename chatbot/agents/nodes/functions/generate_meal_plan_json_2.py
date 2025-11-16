import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id
import json

def generate_meal_plan_json_2(state: AgentState):
    # logger.info("--- GENERATE_MEAL_PLAN ---")
    user_profile = state.get("user_profile", {})
    suggested_meals = state.get("suggested_meals", [])
    meals_to_generate = state.get("meals_to_generate", ["sáng"])

    meal_text = ", ".join(meals_to_generate)

    suggested_meals_text = "\n".join(
        [f"- ID: {meal['meal_id']} {meal['name']}: {meal.get('kcal', 0)} kcal, "
         f"{meal.get('protein', 0)}g protein, "
         f"{meal.get('lipid', 0)}g chất béo, "
         f"{meal.get('carbohydrate', 0)}g carbohydrate"
         for meal in suggested_meals]
    ) if suggested_meals else "Chưa có món ăn gợi ý."

    meal_old = state["meal_old"]

    meal_old_text = "\n".join([
        f"- {item['name']}: {item.get('kcal',0)} kcal, "
        f"{item.get('protein',0)}g protein, "
        f"{item.get('lipid',0)}g lipid, "
        f"{item.get('carbohydrate',0)}g carbohydrate, "
        f"tương đương: {item.get('portion', 1)} khẩu phần."
        for item in meal_old
    ])

    prompt = f"""
        Bạn là AI chuyên gia dinh dưỡng.

        Nhiệm vụ: Tạo lại thực đơn cho bữa {meal_text} bằng cách chọn MÓN MỚI
        từ danh sách gợi ý bên dưới sao cho:
        - Dinh dưỡng gần nhất với bữa cũ (±15%)
        - Món phù hợp khẩu phần: {user_profile['khẩu phần']}
        - Chỉ được chọn món có trong danh sách gợi ý

        --- THÔNG TIN BỮA CŨ ---
        Bao gồm các món sau:
        {meal_old_text}

        Danh sách món gợi ý:
        {suggested_meals_text}

        --- QUY TẮC ---
        1. Chỉ chọn trong danh sách gợi ý.
        2. Mỗi bữa gồm 1–3 món.
        3. Mỗi món phải trả về đầy đủ: "id", "name", "portion".
        4. "portion" có thể là số thực: 0.5, 1.0, 1.2...
        5. Tổng dinh dưỡng bữa mới phải gần với tổng dinh dưỡng bữa cũ (±15%).
        6. Không được thêm mô tả ngoài JSON.

        --- JSON TRẢ VỀ ---
        {{
            "meals": [
                {{
                    "meal_name": "{meal_text}",
                    "items": [
                        {{
                            "id": "ID món",
                            "name": "Tên món",
                            "portion": số_lượng_khẩu_phần
                        }}
                    ]
                }}
            ],
            "reason": "Giải thích vì sao chọn các món và khẩu phần"
        }}
    """

    print("---Prompt---")
    print(prompt)

    result = llm.invoke(prompt)
    output = result.content

    # Parse JSON an toàn
    try:
        meal_new_raw = json.loads(output)
    except Exception as e:
        print("❌ JSON parse error:", e)
        return {"response": "LLM trả về JSON không hợp lệ", "raw_output": output}

    return {"meal_new_raw": meal_new_raw}