from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def select_food(state: AgentState, config: RunnableConfig):
    print("---NODE: ANALYZE & ANSWER---")

    suggested_meals = state["suggested_meals"]

    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else state.get("question", "")

    if not suggested_meals:
        return {"response": "Xin lỗi, tôi không tìm thấy món ăn nào phù hợp trong cơ sở dữ liệu."}

    meals_context = ""
    for i, doc in enumerate(suggested_meals):
        meta = doc.metadata
        # Format kỹ hơn để LLM dễ đọc
        meals_context += (
            f"--- Món {i+1} ---\n"
            f"Tên: {meta.get('name', 'Không tên')}\n"
            f"Dinh dưỡng (1 suất): {meta.get('kcal', '?')} kcal | "
            f"Đạm: {meta.get('protein', '?')}g | Béo: {meta.get('totalfat', '?')}g | Carb: {meta.get('carbs', '?')}g\n"
            f"Mô tả: {doc.page_content}\n\n"
        )

    # 2. Prompt Trả lời câu hỏi
    system_prompt = f"""
    Bạn là Trợ lý Dinh dưỡng AI thông minh.

    DỮ LIỆU TÌM ĐƯỢC TỪ KHO MÓN ĂN:
    {meals_context}

    YÊU CẦU TRẢ LỜI:
    1. Dựa vào "Dữ liệu tìm được", hãy trả lời câu hỏi của người dùng một cách trực tiếp.
    2. Nếu người dùng hỏi thông tin (VD: "Phở bò bao nhiêu calo?"), hãy lấy số liệu chính xác từ dữ liệu trên để trả lời.
    3. Nếu không có dữ liệu phù hợp trong danh sách, hãy thành thật nói "Tôi không tìm thấy thông tin chính xác về món này trong hệ thống".

    Lưu ý: Chỉ sử dụng thông tin từ danh sách cung cấp, không bịa đặt số liệu.
    """
        
    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ], config=config)

        return {"messages": [response]}

    except Exception as e:
        print(f"Lỗi LLM: {e}")
        return {"messages": [AIMessage(content="Xin lỗi, có lỗi xảy ra.")]}