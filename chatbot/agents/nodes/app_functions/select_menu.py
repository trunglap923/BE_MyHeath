from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal, List
from collections import defaultdict
import logging
from chatbot.agents.states.state import AgentState
from chatbot.models.llm_setup import llm

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DATA MODELS ---
class SelectedDish(BaseModel):
    name: str = Field(description="Tên món ăn chính xác trong danh sách")
    meal_type: str = Field(description="Bữa ăn (sáng/trưa/tối)")
    role: Literal["main", "carb", "side"] = Field(
        description="Vai trò: 'main' (Món mặn/Đạm), 'carb' (Cơm/Tinh bột), 'side' (Rau/Canh)"
    )
    reason: str = Field(description="Lý do chọn (ngắn gọn)")

class DailyMenuStructure(BaseModel):
    dishes: List[SelectedDish] = Field(description="Danh sách các món ăn được chọn")

# --- NODE LOGIC ---
def select_menu_structure(state: AgentState):
    logger.info("---NODE: AI SELECTOR (FULL MACRO AWARE)---")
    profile = state["user_profile"]
    candidates = state.get("candidate_pool", [])
    meals_req = state["meals_to_generate"]
    
    if len(candidates) == 0:
        logger.warning("⚠️ Danh sách ứng viên rỗng, không thể chọn món.")
        return {"selected_structure": []}

    # 1. TÍNH TOÁN MỤC TIÊU CHI TIẾT TỪNG BỮA (Budgeting)
    daily_targets = {
        "kcal": float(profile.get('targetcalories', 2000)),
        "protein": float(profile.get('protein', 150)),
        "lipid": float(profile.get('totalfat', 60)),
        "carbohydrate": float(profile.get('carbohydrate', 200))
    }
    ratios = {"sáng": 0.25, "trưa": 0.40, "tối": 0.35}

    # Tính target chi tiết cho từng bữa
    # Kết quả dạng: {'sáng': {'kcal': 500, 'protein': 37.5, ...}, 'trưa': ...}
    meal_targets = {}
    for meal, ratio in ratios.items():
        meal_targets[meal] = {
            k: int(v * ratio) for k, v in daily_targets.items()
        }

    # --- LOGIC TẠO HƯỚNG DẪN ĐỘNG ---
    health_condition = profile.get('healthStatus', 'Bình thường')
    safety_instruction = f"""
    - Tình trạng sức khỏe: {health_condition}.
    - Ưu tiên: Các món thanh đạm, chế biến đơn giản (Hấp/Luộc) nếu người dùng có nhiều bệnh nền.
    """

    # 2. TIỀN XỬ LÝ & PHÂN NHÓM CANDIDATES
    candidates_by_meal = {"sáng": [], "trưa": [], "tối": []}

    for m in candidates:
        if m.get('kcal', 0) > 1500: continue
        if m.get('kcal', 0) < 100: continue

        tag = m.get('meal_type_tag', '').lower()
        if "sáng" in tag: candidates_by_meal["sáng"].append(m)
        elif "trưa" in tag: candidates_by_meal["trưa"].append(m)
        elif "tối" in tag: candidates_by_meal["tối"].append(m)

    def format_list(items):
        if not items: return ""
        return "\n".join([
            f"- {m['name']}: {m.get('kcal')} kcal | P:{m.get('protein')}g | L:{m.get('lipid')}g | C:{m.get('carbohydrate')}g"
            for m in items
        ])

    def get_target_str(meal):
        t = meal_targets.get(meal, {})
        return f"{t.get('kcal')} Kcal (P: {t.get('protein')}g, L: {t.get('lipid')}g, C: {t.get('carbohydrate')}g)"

    # 3. XÂY DỰNG PROMPT (Kèm full chỉ số P/L/C)
    guidance_sang = ""
    if 'sáng' in meals_req:
        guidance_sang = f"""BỮA SÁNG (Mục tiêu ~{get_target_str('sáng')}):
        - Chọn 1 món chính có năng lượng ĐỦ LỚN (gần {get_target_str('sáng')}).
        - Có thể bổ sung 1 món phụ sao cho dinh dưỡng cân bằng.
        - Ưu tiên món nước (Phở/Bún) hoặc Bánh mì/Xôi, không nên ăn lẩu vào bữa sáng."""

    guidance_trua = ""
    if 'trưa' in meals_req:
        guidance_trua = f"""BỮA TRƯA (Mục tiêu ~{get_target_str('trưa')}):
        - Chọn tổ hợp gồm 3 món:
        1. Main: Món cung cấp Protein chính.
        2. Carb: Nguồn tinh bột thanh đạm như cơm trắng, cơm lứt, khoai, bún/phở (ít gia vị/dầu mỡ nếu Main đã đậm đà).
        3. Side: Rau/Canh để bổ sung Xơ.
        - Hoặc chọn 1 món Hỗn hợp (VD: Cơm chiên/Mì xào) nhưng không chọn thêm món mặn.
        - Lưu ý: Món 'Main' và 'Side' phải tách biệt. Đừng chọn món rau xào thịt làm món Side (đó là Main)."""

    guidance_toi = ""
    if 'tối' in meals_req:
        guidance_toi = f"""BỮA TỐI (Mục tiêu ~{get_target_str('tối')}):
        - Tương tự như bữa trưa.
        - Ưu tiên các món nhẹ bụng, dễ tiêu hóa.
        - Giảm lượng tinh bột so với bữa trưa."""

    # 2. Ghép vào prompt chính
    system_prompt = f"""
    Bạn là Chuyên gia Dinh dưỡng AI.
    Nhiệm vụ: Chọn thực đơn cho các bữa: {', '.join(meals_req)} từ danh sách ứng viên đã được lọc sơ bộ. Mỗi bữa bao gồm từ 1 đến 3 món.

    TỔNG MỤC TIÊU NGÀY: {int(daily_targets['kcal'])} Kcal | Protein: {int(daily_targets['protein'])}g | Lipid: {int(daily_targets['lipid'])}g | Carbohydrate: {int(daily_targets['carbohydrate'])}g.

    NGUYÊN TẮC CỐT LÕI:
    1. Nhìn vào số liệu: Hãy chọn món sao cho tổng dinh dưỡng xấp xỉ với Mục Tiêu Chi Tiết của từng bữa.
    2. Cảm quan đầu bếp: Món ăn phải hợp vị (VD: Canh chua đi với Cá kho).
    3. Ước lượng: Không cần tính chính xác tuyệt đối, nhưng đừng chọn món 5g Protein cho mục tiêu 60g Protein.

    NGUYÊN TẮC AN TOÀN:
    Mặc dù danh sách món đã được lọc, bạn vẫn là chốt chặn cuối cùng. Hãy tuân thủ:
    {safety_instruction}

    HƯỚNG DẪN TỪNG BỮA
    {guidance_sang}
    {guidance_trua}
    {guidance_toi}

    DANH SÁCH ỨNG VIÊN
    {format_list(candidates_by_meal['sáng'])}
    {format_list(candidates_by_meal['trưa'])}
    {format_list(candidates_by_meal['tối'])}
    """

    logger.info("Prompt:")
    logger.info(system_prompt)

    # Gọi LLM
    llm_structured = llm.with_structured_output(DailyMenuStructure, strict=True)
    result = llm_structured.invoke(system_prompt)

    # In danh sách các món đã chọn lần lượt theo bữa
    def print_menu_by_meal(daily_menu):
        menu_by_meal = defaultdict(list)
        for dish in daily_menu.dishes:
            menu_by_meal[dish.meal_type.lower()].append(dish)
        meal_order = ["sáng", "trưa", "tối"]
        for meal in meal_order:
            if meal in menu_by_meal:
                logger.info(f"\n🍽 Bữa {meal.upper()}:")
                for d in menu_by_meal[meal]:
                    logger.info(f" - {d.name} ({d.role}): {d.reason}")

    logger.info("\n--- MENU ĐÃ CHỌN ---")
    print_menu_by_meal(result)

    # 4. HẬU XỬ LÝ (Gán Bounds)
    selected_full_info = []
    all_clean_candidates = []
    for sublist in candidates_by_meal.values():
        all_clean_candidates.extend(sublist)
    candidate_map = {m['name']: m for m in all_clean_candidates}

    for choice in result.dishes:
        if choice.name in candidate_map:
            dish_data = candidate_map[choice.name].copy()
            dish_data["assigned_meal"] = choice.meal_type

            # Lấy thông tin dinh dưỡng món hiện tại
            d_kcal = float(dish_data.get("kcal", 0))
            d_pro = float(dish_data.get("protein", 0))

            # Lấy target bữa hiện tại (VD: Trưa)
            t_target = meal_targets.get(choice.meal_type.lower(), {})
            t_kcal = t_target.get("kcal", 500)
            t_pro = t_target.get("protein", 30)

            # --- GIAI ĐOẠN 1: TỰ ĐỘNG SỬA SAI VAI TRÒ (ROLE CORRECTION) ---
            final_role = choice.role # Bắt đầu bằng role AI chọn

            # 1. Phát hiện "Carb trá hình" (Cơm chiên/Mì xào quá nhiều thịt)
            if final_role == "carb" and d_pro > 15:
                print(f"   ⚠️ Phát hiện Carb giàu đạm ({choice.name}: {d_pro}g Pro). Đổi role sang 'main'.")
                final_role = "main"

            # 2. Phát hiện "Side giàu đạm" (Salad gà/bò, Canh sườn)
            elif final_role == "side" and d_pro > 10:
                print(f"   ⚠️ Phát hiện Side giàu đạm ({choice.name}: {d_pro}g Pro). Đổi role sang 'main'.")
                final_role = "main"

            # Cập nhật lại role chuẩn vào dữ liệu
            dish_data["role"] = final_role


            # --- GIAI ĐOẠN 2: THIẾT LẬP BOUNDS CƠ BẢN (BASE BOUNDS) ---
            lower_bound = 0.5
            upper_bound = 1.5

            if final_role == "carb":
                # Cơm/Bún thuần: Cho phép co dãn cực mạnh để bù Kcal
                lower_bound, upper_bound = 0.4, 3.0

            elif final_role == "side":
                # Rau/Canh: Co dãn rộng để bù thể tích ăn
                lower_bound, upper_bound = 0.5, 2.0

            elif final_role == "main":
                # Món mặn: Co dãn vừa phải để giữ hương vị
                lower_bound, upper_bound = 0.6, 1.8


            # --- GIAI ĐOẠN 3: KIỂM TRA AN TOÀN & GHI ĐÈ  ---

            # Override A: Nếu món Main có Protein quá khủng so với Target
            # (VD: Món 52g Pro vs Target Bữa 30g Pro) -> Phải cho phép giảm sâu
            if final_role == "main" and d_pro > t_pro:
                print(f"   ⚠️ Món {choice.name} thừa đạm ({d_pro}g > {t_pro}g). Mở rộng bound xuống thấp.")
                lower_bound = 0.3  # Cho phép giảm xuống 30% suất
                upper_bound = min(upper_bound, 1.2) # Không cho phép tăng quá nhiều

            # Override B: Nếu món quá nhiều Calo (Chiếm > 80% Kcal cả bữa)
            if d_kcal > (t_kcal * 0.8):
                print(f"   ⚠️ Món {choice.name} quá đậm năng lượng ({d_kcal} kcal). Siết chặt bound.")
                lower_bound = 0.3
                upper_bound = min(upper_bound, 1.0) # Chặn không cho tăng

            # Override C: Nếu là món Side nhưng Protein vẫn hơi cao (5-10g)
            # Cho phép giảm để nhường quota Protein cho món Main
            if final_role == "side" and d_pro > 5:
                lower_bound = 0.2 # Cho phép ăn ít rau này lại

            # --- KẾT THÚC: GÁN VÀO DỮ LIỆU ---
            dish_data["solver_bounds"] = (lower_bound, upper_bound)
            selected_full_info.append(dish_data)

    return {
        "selected_structure": selected_full_info,
    }