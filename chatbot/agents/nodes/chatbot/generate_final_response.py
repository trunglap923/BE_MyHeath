from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_final_response(state: AgentState):
    logger.info("---NODE: FINAL RESPONSE---")
    menu = state["response"]["final_menu"]
    profile = state["response"]["user_profile"]

    # Format text để LLM đọc
    menu_text = ""
    current_meal = ""
    for dish in sorted(menu, key=lambda x: x['assigned_meal']): # Sort theo bữa
        if dish['assigned_meal'] != current_meal:
            current_meal = dish['assigned_meal']
            menu_text += f"\n--- BỮA {current_meal.upper()} ---\n"

        menu_text += (
            f"- {dish['name']} (x{dish['portion_scale']} suất): "
            f"{dish['final_kcal']}kcal, {dish['final_protein']}g Protein, {dish['final_lipid']}g Lipid, {dish['final_carb']}g Carbohydrate\n"
        )

    prompt = f"""
    Người dùng có mục tiêu: {profile['targetcalories']} Kcal, {profile['protein']}g Protein, {profile['totalfat']}g Lipid, {profile['carbohydrate']}g Carbohydrate.
    Hệ thống đã tính toán thực đơn tối ưu sau:

    {menu_text}

    Nhiệm vụ:
    1. Trình bày thực đơn này thật đẹp và ngon miệng cho người dùng.
    2. Giải thích ngắn gọn tại sao khẩu phần lại như vậy (Ví dụ: "Mình đã tăng lượng ức gà lên 1.5 suất để đảm bảo đủ Protein cho bạn").
    """

    res = llm.invoke(prompt)
    return {"response": res.content}