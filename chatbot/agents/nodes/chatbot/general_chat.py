from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
from chatbot.utils.chat_history import get_chat_history
from langchain_core.runnables import RunnableConfig
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def general_chat(state: AgentState, config: RunnableConfig):
    logger.info("---GENERAL CHAT---")

    messages = state["messages"]
    question = messages[-1].content
    history = get_chat_history(state["messages"], max_tokens=1000)

    system_prompt = f"""
    Bạn là một chuyên gia dinh dưỡng và ẩm thực AI.
    Hãy trả lời các câu hỏi về:
    - món ăn, thành phần, dinh dưỡng, calo, protein, chất béo, carb,
    - chế độ ăn (ăn chay, keto, giảm cân, tăng cơ...),
    - sức khỏe, lối sống, chế độ tập luyện liên quan đến ăn uống.
    - chức năng, điều khoản, chính sách của ứng dụng.

    Lịch sử hội thoại: {history}

    Quy tắc:
    - Không trả lời các câu hỏi ngoài chủ đề này (hãy từ chối lịch sự).
    - Giải thích ngắn gọn, tự nhiên, rõ ràng.
    - Dựa vào lịch sử trò chuyện để trả lời mạch lạc nếu có câu hỏi nối tiếp.
    """

    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ], config=config)

        return {"messages": [response]}

    except Exception as e:
        print(f"Lỗi LLM: {e}")
        return {"messages": [AIMessage(content="Xin lỗi, có lỗi xảy ra.")]}