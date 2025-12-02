from scipy.optimize import minimize_scalar
from chatbot.agents.states.state import SwapState
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_top_options(state: SwapState):
    logger.info("---NODE: SCIPY RANKING (MATH FILTER)---")
    candidates = state["candidates"]
    food_old = state["food_old"]

    if not candidates: return {"top_candidates": []}

    # 1. Xác định "KPI" từ món cũ
    old_scale = float(food_old.get("portion_scale", 1.0))
    target_vector = np.array([
        float(food_old.get("kcal", 0)) * old_scale,
        float(food_old.get("protein", 0)) * old_scale,
        float(food_old.get("lipid", 0)) * old_scale,
        float(food_old.get("carbohydrate", 0)) * old_scale
    ])
    weights = np.array([3.0, 2.0, 1.0, 1.0])

    # Bound của món cũ
    bounds = food_old.get("solver_bounds", (0.5, 2.0))

    # Hàm tính toán (giữ nguyên logic cũ)
    def calculate_score(candidate):
        base_vector = np.array([
            float(candidate.get("kcal", 0)),
            float(candidate.get("protein", 0)),
            float(candidate.get("lipid", 0)),
            float(candidate.get("carbohydrate", 0))
        ])
        if np.sum(base_vector) == 0: return float('inf'), 1.0

        def objective(x):
            current_vector = base_vector * x
            diff = (current_vector - target_vector) / (target_vector + 1e-5)
            loss = np.sum(weights * (diff ** 2))
            return loss

        res = minimize_scalar(objective, bounds=bounds, method='bounded')
        return res.fun, res.x

    # 3. Chấm điểm hàng loạt
    scored_candidates = []
    for item in candidates:
        loss, scale = calculate_score(item)

        # Chỉ lấy những món có sai số chấp nhận được (Loss < 5.0)
        if loss < 5.0:
            item_score = item.copy()
            item_score["optimization_loss"] = round(loss, 4)
            item_score["portion_scale"] = round(scale, 2)

            # Tính chỉ số hiển thị sau khi scale
            item_score["final_kcal"] = int(item["kcal"] * scale)
            item_score["final_protein"] = int(item["protein"] * scale)
            item_score["final_lipid"] = int(item["lipid"] * scale)
            item_score["final_carb"] = int(item["carbohydrate"] * scale)

            scored_candidates.append(item_score)

    # 4. Lấy Top 10 tốt nhất
    # Sắp xếp theo Loss (thấp nhất là giống dinh dưỡng nhất)
    scored_candidates.sort(key=lambda x: x["optimization_loss"])
    top_10 = scored_candidates[:10]

    logger.info(f"📊 Scipy đã lọc ra {len(top_10)} ứng viên tiềm năng.")
    for item in top_10:
        logger.info(f"   - {item['name']} (Scale x{item['portion_scale']} | Loss: {item['optimization_loss']})")

    return {"top_candidates": top_10}