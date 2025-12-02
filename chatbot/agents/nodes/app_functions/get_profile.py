import logging

from chatbot.agents.states.state import AgentState
from chatbot.utils.user_profile import get_user_by_id
from chatbot.utils.restriction import get_restrictions

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_profile(state: AgentState):
    logger.info("---NODE: GET USER PROFILE---")
    user_id = state.get("user_id", 1)

    raw_profile = get_user_by_id(user_id)
    restrictions = get_restrictions(raw_profile["healthStatus"])

    final_profile = {**raw_profile, **restrictions}
    
    logger.info(f"Tổng hợp user profile cho user_id={user_id} thành công!")

    return {"user_profile": final_profile}
