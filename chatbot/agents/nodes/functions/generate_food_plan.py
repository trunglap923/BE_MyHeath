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

# --- Generate food plan ---
def generate_food_plan(state: AgentState) -> Dict[str, Any]:
    logger.info("--- GENERATE_FOOD_PLAN ---")
    meals_to_generate: List[str] = state.get("meals_to_generate", [])
    user_profile: Dict[str, Any] = state.get("user_profile", {})

    if not meals_to_generate:
        logger.warning("meals_to_generate rỗng, sử dụng mặc định ['sáng', 'trưa', 'tối']")
        meals_to_generate = ["sáng", "trưa", "tối"]

    meals_text = ", ".join(meals_to_generate)

    query_text = (
        f"Tìm các món ăn phù hợp với người dùng có chế độ ăn: {user_profile.get('khẩu phần', 'ăn chay')}. "
        f"Ưu tiên món phổ biến, cân bằng dinh dưỡng, cho bữa {meals_text}."
    )
    logger.info(f"Query: {query_text}")

    try:
        foods = food_retriever.invoke(query_text)
    except Exception as e:
        logger.error(f"Lỗi khi truy vấn món ăn: {e}")
        foods = []

    suggested_meals = [food.metadata for food in foods] if foods else []
    logger.info(f"Số món được gợi ý: {len(suggested_meals)}")

    return {"suggested_meals": suggested_meals}