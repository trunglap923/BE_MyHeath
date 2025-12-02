import random
import logging
from chatbot.agents.states.state import AgentState
from chatbot.agents.tools.food_retriever import food_retriever_50

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_food_candidates(state: AgentState):
    logger.info("---NODE: RETRIEVAL CANDIDATES (ADVANCED PROFILE)---")
    meals = state.get("meals_to_generate", [])
    profile = state["user_profile"]

    candidates = []

    diet_mode = profile.get('diet', '')       # VD: Chế độ HighProtein
    restrictions = profile.get('limitFood', '') # VD: Dị ứng sữa, Thuần chay
    health_status = profile.get('healthStatus', '') # VD: Suy thận

    constraint_prompt = ""
    if restrictions:
        constraint_prompt += f"Yêu cầu bắt buộc: {restrictions}. "
    if health_status:
        constraint_prompt += f"Phù hợp người bệnh: {health_status}. "
    if diet_mode:
        constraint_prompt += f"Chế độ: {diet_mode}."

    # ĐỊNH NGHĨA TEMPLATE PROMPT
    prompt_templates = {
        "sáng": (
            f"Món ăn sáng, điểm tâm. Ưu tiên món nước hoặc món khô dễ tiêu hóa. "
            f"{constraint_prompt}"
        ),
        "trưa": (
            f"Món ăn chính cho bữa trưa. "
            f"{constraint_prompt}"
        ),
        "tối": (
            f"Món ăn tối, nhẹ bụng. "
            f"{constraint_prompt}"
        ),
    }

    random_vibes = [
        "hương vị truyền thống", "phong cách hiện đại",
        "thanh đạm", "chế biến đơn giản", "phổ biến nhất"
    ]

    for meal_type in meals:
        logger.info(meal_type)
        base_prompt = prompt_templates.get(meal_type, f"Món ăn {meal_type}. {constraint_prompt}")
        vibe = random.choice(random_vibes)
        numerical_query = generate_numerical_constraints(profile, meal_type)

        final_query = f"{base_prompt} Phong cách: {vibe}.{' Ràng buộc: ' + numerical_query if numerical_query != '' else ''}"
        logger.info(f"🔎 Query ({meal_type}): {final_query}")

        docs = food_retriever_50.invoke(final_query)
        ranked_items = rank_candidates(docs, profile, meal_type)
        
        if len(ranked_items) > 0:
            ranked_items_shuffle = random.sample(ranked_items[:30], 30)
            
            k = 20 if len(meals) == 1 else 10
            
            selected_docs = ranked_items_shuffle[:k]
            
            for doc in selected_docs:
                item = doc.copy()
                item["meal_type_tag"] = meal_type
                item["retrieval_vibe"] = vibe
                candidates.append(item)

    unique_candidates = {v['name']: v for v in candidates}.values()
    final_pool = list(unique_candidates)

    logger.info(f"📚 Candidate Pool Size: {len(final_pool)} món")
    return {"candidate_pool": final_pool, "meals_to_generate": meals}

def generate_numerical_constraints(user_profile, meal_type):
    """
    Tạo chuỗi ràng buộc số liệu dinh dưỡng dựa trên cấu hình người dùng.
    """
    ratios = {"sáng": 0.25, "trưa": 0.40, "tối": 0.35}
    meal_ratio = ratios.get(meal_type, 0.3)

    critical_nutrients = {
        "Protein": ("protein", "protein", "g", "range"),
        "Saturated fat": ("saturatedfat", "saturated_fat", "g", "max"),
        "Natri": ("natri", "natri", "mg", "max"), # Quan trọng cho thận/tim
        "Kali": ("kali", "kali", "mg", "range"),  # Quan trọng cho thận
        "Phốt pho": ("photpho", "photpho", "mg", "max"), # Quan trọng cho thận
        "Sugars": ("sugar", "sugar", "g", "max"), # Quan trọng cho tiểu đường
        "Carbohydrate": ("carbohydrate", "carbohydrate", "g", "range"),
    }

    constraints = []

    check_list = set(user_profile.get('Kiêng', []) + user_profile.get('Hạn chế', []))
    for item_name in check_list:
        if item_name not in critical_nutrients: continue

        config = critical_nutrients.get(item_name)
        profile_key, db_key, unit, logic = config
        daily_val = float(user_profile.get(profile_key, 0))
        meal_target = daily_val * meal_ratio

        if logic == 'max':
            # Nới lỏng một chút ở bước tìm kiếm (120-130% target) để không bị lọc hết
            threshold = round(meal_target * 1.3, 2)
            constraints.append(f"{db_key} < {threshold}{unit}")

        elif logic == 'range':
            # Range rộng (50% - 150%) để bắt được nhiều món
            min_val = round(meal_target * 0.5, 2)
            max_val = round(meal_target * 1.5, 2)
            constraints.append(f"{db_key} > {min_val}{unit} - {db_key} < {max_val}{unit}")

    if not constraints: return ""
    return ", ".join(constraints)

def rank_candidates(candidates, user_profile, meal_type):
    """
    Chấm điểm (Scoring) các món ăn dựa trên cấu hình dinh dưỡng chi tiết.
    """
    print("---NODE: RANKING CANDIDATES (ADVANCED SCORING)---")

    ratios = {"sáng": 0.25, "trưa": 0.40, "tối": 0.35}
    meal_ratio = ratios.get(meal_type, 0.3)

    nutrient_config = {
        # --- Nhóm Đa lượng (Macro) ---
        "Protein": ("protein", "protein", "g", "range"),
        "Total Fat": ("totalfat", "lipid", "g", "max"),
        "Carbohydrate": ("carbohydrate", "carbohydrate", "g", "range"),
        "Saturated fat": ("saturatedfat", "saturated_fat", "g", "max"),
        "Monounsaturated fat": ("monounsaturatedfat", "monounsaturated_fat", "g", "max"),
        "Trans fat": ("transfat", "trans_fat", "g", "max"),
        "Sugars": ("sugar", "sugar", "g", "max"),
        "Chất xơ": ("fiber", "fiber", "g", "min"),

        # --- Nhóm Vi chất (Micro) ---
        "Vitamin A": ("vitamina", "vit_a", "mg", "min"),
        "Vitamin C": ("vitaminc", "vit_c", "mg", "min"),
        "Vitamin D": ("vitamind", "vit_d", "mg", "min"),
        "Vitamin E": ("vitamine", "vit_e", "mg", "min"),
        "Vitamin K": ("vitamink", "vit_k", "mg", "min"),
        "Vitamin B6": ("vitaminb6", "vit_b6", "mg", "min"),
        "Vitamin B12": ("vitaminb12", "vit_b12", "mg", "min"),

        # --- Khoáng chất ---
        "Canxi": ("canxi", "canxi", "mg", "min"),
        "Sắt": ("fe", "sat", "mg", "min"),
        "Magie": ("magie", "magie", "mg", "min"),
        "Kẽm": ("zn", "kem", "mg", "min"),
        "Kali": ("kali", "kali", "mg", "range"),
        "Natri": ("natri", "natri", "mg", "max"),
        "Phốt pho": ("photpho", "photpho", "mg", "max"),

        # --- Khác ---
        "Cholesterol": ("cholesterol", "cholesterol", "mg", "max"),
        "Choline": ("choline", "choline", "mg", "min"),
        "Caffeine": ("caffeine", "caffeine", "mg", "max"),
        "Alcohol": ("alcohol", "alcohol", "g", "max"),
    }

    scored_list = []

    for doc in candidates:
        item = doc.metadata
        score = 0
        reasons = [] # Lưu lý do để debug hoặc giải thích cho user

        # --- 1. CHẤM ĐIỂM NHÓM "BỔ SUNG" (BOOST) ---
        # Logic: Càng nhiều càng tốt
        for nutrient in user_profile.get('Bổ sung', []):
            config = nutrient_config.get(nutrient)
            if not config: continue

            p_key, db_key, unit, logic = config

            # Lấy giá trị thực tế trong món ăn và mục tiêu
            val = float(item.get(db_key, 0))
            daily_target = float(user_profile.get(p_key, 0))
            meal_target = daily_target * meal_ratio

            if meal_target == 0: continue

            # Chấm điểm
            # Nếu đạt > 50% target bữa -> +10 điểm
            if val >= meal_target * 0.5:
                score += 10
                reasons.append(f"Giàu {nutrient}")
            # Nếu đạt > 80% target -> +15 điểm (thưởng thêm)
            if val >= meal_target * 0.8:
                score += 5

        # --- 2. CHẤM ĐIỂM NHÓM "HẠN CHẾ" & "KIÊNG" (PENALTY/REWARD) ---
        # Gộp chung vì logic giống nhau: Càng thấp càng tốt
        check_list = set(user_profile.get('Hạn chế', []) + user_profile.get('Kiêng', []))

        for nutrient in check_list:
            config = nutrient_config.get(nutrient)
            if not config: continue

            p_key, db_key, unit, logic = config
            val = float(item.get(db_key, 0))
            daily_target = float(user_profile.get(p_key, 0))
            meal_target = daily_target * meal_ratio

            if meal_target == 0: continue

            if logic == 'max':
                # Nếu thấp hơn target -> +10 điểm (Tốt)
                if val <= meal_target:
                    score += 10
                # Nếu thấp hơn hẳn (chỉ bằng 50% target) -> +15 điểm (Rất an toàn)
                if val <= meal_target * 0.5:
                    score += 5
                # Nếu vượt quá target -> -10 điểm (Phạt)
                if val > meal_target:
                    score -= 10

            elif logic == 'range':
                # Logic cho Kali/Protein: Tốt nhất là nằm trong khoảng, không thấp quá, không cao quá
                min_safe = meal_target * 0.5
                max_safe = meal_target * 1.5

                if min_safe <= val <= max_safe:
                    score += 10 # Nằm trong vùng an toàn
                elif val > max_safe:
                    score -= 10 # Cao quá (nguy hiểm cho thận)
                # Thấp quá thì không trừ điểm nặng, chỉ không được cộng

        # --- 3. ĐIỂM THƯỞNG CHO SỰ PHÙ HỢP CƠ BẢN (BASE HEALTH) ---
        # Ít đường (< 5g) -> +2 điểm
        if float(item.get('sugar', 0)) < 5: score += 2

        # Ít saturated fat (< 3g) -> +2 điểm
        if float(item.get('saturated_fat', 0)) < 3: score += 2

        # Giàu xơ (> 3g) -> +3 điểm
        if float(item.get('fiber', 0)) > 3: score += 3

        # Lưu kết quả
        item_copy = item.copy()
        item_copy["health_score"] = score
        item_copy["score_reason"] = ", ".join(reasons[:3]) # Chỉ lấy 3 lý do chính
        scored_list.append(item_copy)

    # 4. SẮP XẾP & TRẢ VỀ
    # Sort giảm dần theo điểm (Điểm cao nhất lên đầu)
    scored_list.sort(key=lambda x: x["health_score"], reverse=True)

    # # Debug: In Top 3
    # logger.info("🏆 Top 3 Món Tốt Nhất (Sau khi chấm điểm):")
    # for i, m in enumerate(scored_list[:3]):
    #     logger.info(f"   {i+1}. {m['name']} (Score: {m['health_score']}) | {m.get('score_reason')}")

    return scored_list