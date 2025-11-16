from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from chatbot.agents.states.state import AgentState
from chatbot.agents.graphs.meal_suggestion_json_graph import workflow_meal_suggestion_json

# --- Định nghĩa request body ---
class Request(BaseModel):
    user_id: str

# --- Tạo router ---
router = APIRouter(
    prefix="/daily-plan",
    tags=["Daily Plan"]
)

# --- Route xử lý chat ---
@router.post("/")
def chat(request: Request):
    try:
        
        print("Nhận được yêu cầu chat từ user:", request.user_id)
        
        # 1. Tạo state mới
        state = AgentState()
        state["user_id"] = request.user_id
        
        # 2. Lấy workflow
        graph = workflow_meal_suggestion_json()

        # 3. Invoke workflow
        result = graph.invoke(state)

        # 4. Trả response
        response = result["meal_plan_day"] or "Không có kết quả"
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")
