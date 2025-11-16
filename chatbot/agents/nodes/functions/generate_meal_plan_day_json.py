import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

import json

def generate_meal_plan_day_json(state: AgentState):
    # logger.info("--- GENERATE_MEAL_PLAN ---")
    user_profile = state.get("user_profile", {})
    suggested_meals = state.get("suggested_meals", [])

    suggested_meals_text = "\n".join(
        [f"- ID: {meal['meal_id']} {meal['name']}: {meal.get('kcal', 0)} kcal, "
         f"{meal.get('protein', 0)}g protein, "
         f"{meal.get('lipid', 0)}g chất béo, "
         f"{meal.get('carbohydrate', 0)}g carbohydrate"
         for meal in suggested_meals]
    ) if suggested_meals else "Chưa có món ăn gợi ý."

    prompt = f"""
        Bạn là AI chuyên gia dinh dưỡng. Nhiệm vụ: Tạo thực đơn cho một ngày theo dạng JSON.

        Hồ sơ dinh dưỡng người dùng:
        - Năng lượng mục tiêu: {user_profile['kcal']} kcal/ngày
        - Protein: {user_profile['protein']}g
        - Lipid: {user_profile['lipid']}g
        - Carbohydrate: {user_profile['carbohydrate']}g
        - Chế độ ăn: {user_profile['khẩu phần']}

        Danh sách món ăn hiện có:
        {suggested_meals_text}

        --- YÊU CẦU ---
        Trả về duy nhất một JSON theo cấu trúc sau:

        {{
            "meals": [
                {{
                    "meal_name": "Tên bữa",
                    "items": [
                        {{
                            "id": "ID món",
                            "name": "Tên món",
                            "portion": số_lượng_khẩu_phần (float)
                        }}
                    ]
                }}
            ],
            "reason": "Lý do xây dựng thực đơn"
        }}

        --- QUY TẮC ---
        1. Hãy tổ hợp các món ăn trên để tạo thực đơn cho từng bữa (chỉ chọn trong danh sách có sẵn).
        2. Mỗi bữa gồm 1 đến 3 món, tổng năng lượng và dinh dưỡng xấp xỉ giá trị yêu cầu của bữa đó (±15%).
        3. Mỗi món phải có cả "id", "name", "portion".
        4. Điều chỉnh "portion" có thể là 0.5, 1, 1.2... sao cho tổng năng lượng của một ngày đạt cân bằng chính xác.
        5. Đảm bảo tổng giá trị dinh dưỡng toàn ngày gần với hồ sơ người dùng.
        6. "reason" là lý do xây dựng thực đơn bao gồm dinh dưỡng của từng bữa sáng, trưa, tối và tổng lại cả ngày.
        7. Chỉ chọn món đúng chế độ ăn: {user_profile['khẩu phần']}.
        8. KHÔNG được trả lời thêm văn bản nào ngoài JSON.
    """

    print("---Prompt---")
    print(prompt)

    result = llm.invoke(prompt)
    output = result.content

    # Parse JSON an toàn
    try:
        meal_plan = json.loads(output)
        logging.info("Lý do: " + meal_plan.get("reason", "Không có lý do"))
    except Exception as e:
        print("❌ JSON parse error:", e)
        return {"response": "LLM trả về JSON không hợp lệ", "raw_output": output}

    return {"meal_plan": meal_plan}
