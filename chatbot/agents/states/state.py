from typing import Annotated, Optional, Literal, Sequence, TypedDict, List, Dict, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # ========== Thông tin cơ bản ==========
    user_id: Optional[str]
    question: str

    # ========== Ngữ cảnh hội thoại ==========
    topic: Optional[str]
    user_profile: Optional[Dict[str, Any]]

    # ========== Gợi ý & lựa chọn món ăn ==========
    meals_to_generate: Optional[List[str]]
    suggested_meals: Optional[List[Dict[str, Any]]]

    # ========== Kết quả & phản hồi ==========
    response: Optional[str]
    messages: Annotated[list, add_messages]

    # ========== Mục tiêu & truy vấn ==========
    candidate_pool: List[dict]
    selected_structure: List[dict]
    reason: Optional[str]
    final_menu: List[dict]

    food_old: Optional[Dict[str, Any]]

class SwapState(TypedDict):
    user_profile: Dict[str, Any]
    food_old: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    top_candidates: List[Dict[str, Any]]
    best_replacement: Dict[str, Any]

__all__ = ["AgentState", "SwapState"]
