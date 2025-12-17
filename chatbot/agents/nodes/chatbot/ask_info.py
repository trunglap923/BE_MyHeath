from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
from chatbot.knowledge.field_requirement import FIELD_NAMES_VN
from langchain_core.runnables import RunnableConfig
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ask_missing_info(state: AgentState, config: RunnableConfig):
    logger.info("---NODE: ASK MISSING INFO---")

    missing_fields = state.get("missing_fields", [])
    topic = state.get("topic", "")

    # 1. Chuyển tên trường kỹ thuật sang tiếng Việt
    missing_vn = [FIELD_NAMES_VN.get(f, f) for f in missing_fields]
    missing_str = ", ".join(missing_vn)

    system_instruction = ""
    
    if topic == "meal_suggestion":
        system_instruction = f"""
        Bạn là Trợ lý Dinh dưỡng AI. Nhiệm vụ của bạn là yêu cầu người dùng cung cấp thông tin còn thiếu để lên thực đơn.
        
        Thông tin đang thiếu: **{missing_str}**.

        Hãy soạn một câu trả lời thân thiện, tự nhiên nhưng ngắn gọn, hướng dẫn người dùng cung cấp theo 1 trong 2 cách sau:
        1. Cung cấp thông tin cơ thể (Cân nặng, Chiều cao, Tuổi, Giới tính, Mức độ vận động) -> Để AI tự tính toán.
        2. Hoặc cung cấp mục tiêu dinh dưỡng cụ thể nếu đã biết (Kcal, Protein, Fat, Carb).
        
        Gợi ý ví dụ nhập liệu nhanh cho họ (ví dụ: "Mình 60kg, cao 1m7...").
        """
    else:
        system_instruction = f"""
        Bạn là Trợ lý AI. Người dùng đang yêu cầu một tác vụ nhưng thiếu thông tin.
        Thông tin cần bổ sung: **{missing_str}**.
        Hãy yêu cầu người dùng cung cấp các thông tin này một cách lịch sự, ngắn gọn và rõ ràng.
        """
        
    try:
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content="Hãy hỏi người dùng thông tin còn thiếu.")
        ]

        response = await llm.ainvoke(messages, config=config)
        
        return {"messages": [response]}

    except Exception as e:
        logger.error(f"Lỗi LLM trong ask_missing_info: {e}")
        return {"messages": [AIMessage(content=f"Mình cần thêm thông tin về {missing_str} để tiếp tục.")]}