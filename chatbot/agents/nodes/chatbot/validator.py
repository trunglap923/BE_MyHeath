
from chatbot.agents.states.state import AgentState
from chatbot.knowledge.field_requirement import TOPIC_REQUIREMENTS
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def universal_validator(state: AgentState):
    print("---NODE: UNIVERSAL VALIDATOR---")

    topic = state.get("topic", "general_chat")
    missing_from_prev = set(state.get("missing_fields", []))

    requirement_groups = TOPIC_REQUIREMENTS.get(topic, [])

    if not requirement_groups:
        logger.info(f"   ✅ Topic '{topic}' không có requirement. Pass.")
        return {"is_valid": True, "missing_fields": []}

    all_group_missing = []

    for group in requirement_groups:
        missing_in_group = list(set(group) & missing_from_prev)

        if not missing_in_group:
            logger.info(
                f"   ✅ Topic '{topic}' thỏa mãn requirement group: {group}"
            )
            return {"is_valid": True, "missing_fields": []}

        all_group_missing.append(missing_in_group)

    final_missing = min(all_group_missing, key=len)

    logger.info(
        f"   ⛔ Topic '{topic}' chưa đủ requirement. "
        f"Còn thiếu (ưu tiên hỏi): {final_missing}"
    )

    return {
        "is_valid": False,
        "missing_fields": final_missing
    }