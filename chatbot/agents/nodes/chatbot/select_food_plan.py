from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def select_food_plan(state: AgentState):
    logger.info("---SELECT FOOD PLAN---")

    user_profile = state["user_profile"]
    suggested_meals = state["suggested_meals"]
    messages = state["messages"]
    user_message = messages[-1].content if messages else state.question

    suggested_meals_text = "\n".join(
        f"{i+1}. {doc.metadata.get('name', 'Không rõ')} - "
        f"{doc.metadata.get('kcal', '?')} kcal, "
        f"Protein:{doc.metadata.get('protein', '?')}g, "
        f"Chất béo:{doc.metadata.get('lipid', '?')}g, "
        f"Carbohydrate:{doc.metadata.get('carbohydrate', '?')}g"
        for i, doc in enumerate(suggested_meals)
    )

    prompt = f"""
Bạn là chuyên gia dinh dưỡng AI.
Bạn có thể sử dụng thông tin người dùng có hồ sơ dinh dưỡng sau nếu cần thiết cho câu hỏi của người dùng:
- Tổng năng lượng mục tiêu: {user_profile['targetcalories']} kcal/ngày
- Protein: {user_profile['protein']}g
- Chất béo (lipid): {user_profile['totalfat']}g
- Carbohydrate: {user_profile['carbohydrate']}g
- Chế độ ăn: {user_profile['diet']}

Câu hỏi của người dùng: "{user_message}"

Danh sách món ăn hiện có để chọn:
{suggested_meals_text}

Yêu cầu:
1. Chọn một món ăn phù hợp nhất với yêu cầu của người dùng, dựa trên dinh dưỡng và chế độ ăn.
2. Nếu không có món nào phù hợp, hãy trả về:
  "Không tìm thấy món phù hợp trong danh sách hiện có."
3. Không tự tạo thêm món mới hoặc tên món không có trong danh sách.
4. Nếu có nhiều món gần giống nhau, hãy chọn món có năng lượng và thành phần dinh dưỡng gần nhất với mục tiêu người dùng.
    """

    logger.info("Prompt:")
    logger.info(prompt)

    result = llm.invoke(prompt)

    logger.info(result.content if hasattr(result, "content") else result)

    return {"response": result.content}