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

def get_user_profile(state: AgentState) -> Dict[str, Any]:
    """
    Node: Lấy profile người dùng và chuẩn hóa key.
    """
    logger.info("--- GET_USER_PROFILE ---")
    user_id = state.get("user_id", "")
    user_profile = get_user_by_id(user_id)

    # Chuẩn hóa khóa
    mapping = {"fat": "lipid", "carbs": "carbohydrate", "protein": "protein",
               "kcal": "kcal", "lipid": "lipid", "carbohydrate": "carbohydrate"}
    normalized_profile = {mapping.get(k.lower(), k.lower()): v for k, v in user_profile.items()}

    # Fallback default nếu thiếu
    defaults = {"kcal": 1700, "protein": 120, "lipid": 56, "carbohydrate": 170, "khẩu phần": "ăn chay"}
    for key, val in defaults.items():
        normalized_profile.setdefault(key, val)

    logger.info(f"User profile chuẩn hóa: {normalized_profile}")

    return {"user_profile": normalized_profile, "daily_goal": normalized_profile, "suggested_meals": []}
