from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
from chatbot.agents.tools.info_app_retriever import policy_search
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def policy(state: AgentState):
    logger.info("---POLICY---")
    messages = state["messages"]
    question = messages[-1].content if messages else state.question

    if not question:
        return {"response": "Chưa có câu hỏi."}

    # Tạo retriever, lấy 3 doc gần nhất
    policy_retriever = policy_search.as_retriever(search_kwargs={"k": 3})

    # Lấy các document liên quan
    docs = policy_retriever.invoke(question)

    if not docs:
        return {"response": "Không tìm thấy thông tin phù hợp."}

    # Gom nội dung các doc lại
    context_text = "\n\n".join([doc.page_content for doc in docs])

    # Tạo prompt cho LLM
    prompt_text = f"""
Bạn là trợ lý AI chuyên về chính sách và thông tin app.

Thông tin tham khảo từ hệ thống:
{context_text}

Câu hỏi của người dùng: {question}

Hãy trả lời ngắn gọn, dễ hiểu, chính xác dựa trên thông tin có trong hệ thống.
"""

    # Gọi LLM
    result = llm.invoke(prompt_text)
    answer = result.content

    return {"response": answer}
