from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def select_food(state: AgentState):
    print("---NODE: ANALYZE & ANSWER---")

    suggested_meals = state["suggested_meals"]

    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else state.get("question", "")

    # 1. Format dữ liệu món ăn để đưa vào Prompt
    if not suggested_meals:
        return {"response": "Xin lỗi, tôi không tìm thấy món ăn nào phù hợp trong cơ sở dữ liệu."}

    meals_context = ""
    for i, doc in enumerate(suggested_meals):
        meta = doc.metadata
        meals_context += (
            f"Món {i+1}: {meta.get('name', 'Không tên')}\n"
            f"   - Dinh dưỡng: {meta.get('kcal', '?')} kcal | "
            f"P: {meta.get('protein', '?')}g | L: {meta.get('lipid', '?')}g | C: {meta.get('carbohydrate', '?')}g\n"
            f"   - Mô tả/Thành phần: {doc.page_content}...\n"
        )

    # 2. Prompt Trả lời câu hỏi
    # Prompt này linh hoạt hơn: Không ép chọn 1 món nếu user hỏi dạng liệt kê ("Tìm các món gà...")
    system_prompt = f"""
    Bạn là Trợ lý Dinh dưỡng AI thông minh.

    CÂU HỎI: "{user_message}"

    DỮ LIỆU TÌM ĐƯỢC TỪ KHO MÓN ĂN:
    {meals_context}

    YÊU CẦU TRẢ LỜI:
    1. Dựa vào "Dữ liệu tìm được", hãy trả lời câu hỏi của người dùng một cách trực tiếp.
    2. Nếu người dùng hỏi thông tin (VD: "Phở bò bao nhiêu calo?"), hãy lấy số liệu chính xác từ dữ liệu trên để trả lời.
    3. Nếu không có dữ liệu phù hợp trong danh sách, hãy thành thật nói "Tôi không tìm thấy thông tin chính xác về món này trong hệ thống".

    Lưu ý: Chỉ sử dụng thông tin từ danh sách cung cấp, không bịa đặt số liệu.
    """

    # Gọi LLM
    response = llm.invoke(system_prompt)
    content = response.content if hasattr(response, "content") else response

    print("💬 AI Response:")
    print(content)

    return {"response": content}