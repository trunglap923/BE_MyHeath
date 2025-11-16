import logging
from typing import List, Dict, Any

from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import query_constructor, food_retriever
from langgraph.graph import END, StateGraph
from chatbot.models.llm_setup import llm
from langchain.tools import tool
from chatbot.utils.user_profile import get_user_by_id

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_meal_plan(state: AgentState):
    logger.info("--- GENERATE_MEAL_PLAN ---")
    user_profile = state.get("user_profile", {})
    suggested_meals = state.get("suggested_meals", [])
    meals_to_generate = state.get("meals_to_generate", [])
    question = state.get("question", "Hãy tạo thực đơn cho tôi.")

    meals_text = ", ".join(meals_to_generate)

    suggested_meals_text = "\n".join(
        [f"- {meal['name']}: {meal.get('kcal', 0)} kcal, "
         f"{meal.get('protein', 0)}g protein, "
         f"{meal.get('lipid', 0)}g chất béo, "
         f"{meal.get('carbohydrate', 0)}g carbohydrate"
         for meal in suggested_meals]
    ) if suggested_meals else "Chưa có món ăn gợi ý."

    prompt = f"""
        Bạn có thể sử dụng thông tin người dùng có hồ sơ dinh dưỡng sau nếu cần thiết cho câu hỏi của người dùng:
        - Tổng năng lượng mục tiêu: {user_profile['kcal']} kcal/ngày
        - Protein: {user_profile['protein']}g
        - Chất béo (lipid): {user_profile['lipid']}g
        - Carbohydrate: {user_profile['carbohydrate']}g
        - Chế độ ăn: {user_profile['khẩu phần']}

        Câu hỏi của người dùng: "{question}"

        Các bữa cần xây dựng:
        {meals_text}

        Danh sách món ăn hiện có để chọn:
        {suggested_meals_text}

        Yêu cầu:
        1. Hãy tổ hợp các món ăn trên để tạo thực đơn cho từng bữa (chỉ chọn trong danh sách có sẵn).
        2. Mỗi bữa gồm 1 đến 3 món, tổng năng lượng và dinh dưỡng xấp xỉ giá trị yêu cầu của bữa đó (±15%).
        3. Nếu cần, hãy ước tính khẩu phần mỗi món (ví dụ: 0.5 khẩu phần hoặc 1.2 khẩu phần) để đạt cân bằng chính xác.
        4. Đảm bảo tổng giá trị dinh dưỡng toàn ngày gần với hồ sơ người dùng.
        5. Chỉ chọn những món phù hợp với chế độ ăn: {user_profile['khẩu phần']}.
    """

    logger.info(prompt)
    
    try:
        result = llm.invoke(prompt, timeout=60)
        response_content = getattr(result, "content", str(result))
    except Exception as e:
        logger.error(f"Lỗi khi gọi LLM: {e}")
        response_content = "Không thể tạo thực đơn lúc này, vui lòng thử lại sau."

    logger.info("Meal plan suggestion generated.")
    return {"response": response_content}