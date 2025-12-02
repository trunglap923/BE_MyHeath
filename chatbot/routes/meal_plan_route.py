from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from chatbot.agents.states.state import AgentState
from chatbot.agents.graphs.meal_suggestion_graph import meal_plan_graph

# --- Định nghĩa request body ---
class Request(BaseModel):
    user_id: str
    meals_to_generate: list

# --- Tạo router ---
router = APIRouter(
    prefix="/meal-plan",
    tags=["Meal Plan"]
)

# --- Route xử lý chat ---
@router.post("/")
def chat(request: Request):
    try:
        
        print("Nhận được yêu cầu chat từ user:", request.user_id)
        
        # 1. Tạo state mới
        state = AgentState()
        state["user_id"] = request.user_id
        state["meals_to_generate"] = request.meals_to_generate
        
        # 2. Lấy workflow
        graph = meal_plan_graph()

        # 3. Invoke workflow
        result = graph.invoke(state)

        # 4. Trả response
        response = result or "Không có kết quả"
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")
