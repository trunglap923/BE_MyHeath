from langchain_core.pydantic_v1 import BaseModel, Field
from chatbot.models.llm_setup import llm
from chatbot.agents.states.state import SwapState
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChefDecision(BaseModel):
    # Thay đổi tên trường cho rõ nghĩa
    selected_meal_id: int = Field(description="ID (meal_id) của món ăn được chọn từ danh sách")
    reason: str = Field(description="Lý do ẩm thực ngắn gọn")

def llm_finalize_choice(state: SwapState):
    logger.info("---NODE: LLM FINAL SELECTION (BY REAL MEAL_ID)---")
    top_candidates = state["top_candidates"]
    food_old = state["food_old"]

    if not top_candidates: return {"best_replacement": None}

    # 1. Format danh sách hiển thị kèm Real ID
    options_text = ""
    for item in top_candidates:
        # Lấy meal_id thực tế từ dữ liệu
        real_id = item.get("meal_id")

        options_text += (
            f"ID [{real_id}] - {item['name']}\n"  # <--- Hiển thị ID thật
            f"   - Số liệu: {item['final_kcal']} Kcal | P:{item['final_protein']}g | L:{item['final_lipid']}g | C:{item['final_carb']}g\n"
            f"   - Độ lệch (Loss): {item['optimization_loss']}\n"
        )

    # 2. Prompt cập nhật
    system_prompt = f"""
    Bạn là Bếp trưởng. Người dùng muốn đổi món '{food_old.get('name')}'.
    Dưới đây là các ứng viên thay thế:

    {options_text}

    NHIỆM VỤ:
    1. Chọn ra 1 món thay thế tốt nhất về mặt ẩm thực.
    2. Trả về chính xác ID (số trong ngoặc vuông []) của món đó.
    """

    # 3. Gọi LLM
    try:
        llm_structured = llm.with_structured_output(ChefDecision)
        decision = llm_structured.invoke(system_prompt)
        target_id = decision.selected_meal_id
    except Exception as e:
        logger.info(f"⚠️ LLM Error: {e}. Fallback to first option.")
        # Fallback lấy ID của món đầu tiên
        target_id = top_candidates[0].get("meal_id")
        decision = ChefDecision(selected_meal_id=target_id, reason="Fallback do lỗi hệ thống.")

    # 4. Mapping lại bằng meal_id (Chính xác tuyệt đối)
    selected_full_candidate = None

    for item in top_candidates:
        # So sánh ID (lưu ý ép kiểu nếu cần thiết để tránh lỗi string vs int)
        if int(item.get("meal_id")) == int(target_id):
            selected_full_candidate = item
            break

    # Fallback an toàn
    if not selected_full_candidate:
        logger.info(f"⚠️ ID {target_id} không tồn tại trong list. Chọn món Top 1.")
        selected_full_candidate = top_candidates[0]

    # Bổ sung lý do
    selected_full_candidate["chef_reason"] = decision.reason

    # Bổ sung lý do
    selected_full_candidate["chef_reason"] = decision.reason

    #-------------------------------------------------------------------
    # --- PHẦN MỚI: IN BẢNG SO SÁNH (VISUAL COMPARISON) ---
    logger.info(f"\n✅ CHEF SELECTED: {selected_full_candidate['name']} (ID: {selected_full_candidate['meal_id']})")
    logger.info(f"📝 Lý do: {decision.reason}")

    # Lấy thông tin món cũ (đã scale ở menu gốc)
    # Lưu ý: food_old trong state là thông tin gốc hoặc đã tính toán ở daily menu
    old_kcal = float(food_old.get('final_kcal', food_old['kcal']))
    old_pro = float(food_old.get('final_protein', food_old['protein']))
    old_fat = float(food_old.get('final_lipid', food_old['lipid']))
    old_carb = float(food_old.get('final_carb', food_old['carbohydrate']))

    # Lấy thông tin món mới (đã re-scale bởi Scipy)
    new_kcal = selected_full_candidate['final_kcal']
    new_pro = selected_full_candidate['final_protein']
    new_fat = selected_full_candidate['final_lipid']
    new_carb = selected_full_candidate['final_carb']
    scale = selected_full_candidate['portion_scale']

    # In bảng
    logger.info("\n   📊 BẢNG SO SÁNH THAY THẾ:")
    headers = ["Chỉ số", "Món Cũ (Gốc)", "Món Mới (Re-scale)", "Chênh lệch"]
    row_fmt = "   | {:<10} | {:<15} | {:<20} | {:<12} |"

    logger.info("   " + "-"*68)
    logger.info(row_fmt.format(*headers))
    logger.info("   " + "-"*68)

    # Helper in dòng
    def print_row(label, old_val, new_val, unit=""):
        diff = new_val - old_val
        diff_str = f"{diff:+.1f}"

        # Đánh dấu màu (Logic text)
        status = "✅"
        # Nếu lệch > 20% thì cảnh báo
        if old_val > 0 and abs(diff)/old_val > 0.2: status = "⚠️"

        logger.info(row_fmt.format(
            label,
            f"{old_val:.0f} {unit}",
            f"{new_val:.0f} {unit} (x{scale} suất)",
            f"{diff_str} {status}"
        ))

    print_row("Năng lượng", old_kcal, new_kcal, "Kcal")
    print_row("Protein", old_pro, new_pro, "g")
    print_row("Lipid", old_fat, new_fat, "g")
    print_row("Carb", old_carb, new_carb, "g")
    logger.info("   " + "-"*68)

    logger.info(f"✅ Chef Selected: ID {selected_full_candidate['meal_id']} - {selected_full_candidate['name']}")

    return {"best_replacement": selected_full_candidate}