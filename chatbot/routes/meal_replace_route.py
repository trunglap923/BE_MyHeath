from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from chatbot.agents.states.state import AgentState
from chatbot.agents.graphs.meal_similarity_graph import meal_similarity_graph

# --- Định nghĩa request body ---
class Request(BaseModel):
    user_id: str
    meal_old: list

# --- Tạo router ---
router = APIRouter(
    prefix="/meal-replace",
    tags=["Meal Replace"]
)

@router.post("/")
def chat(request: Request):
    try:
        
        print("Nhận được yêu cầu chat từ user:", request.user_id)
        
        # 1. Tạo state mới
        state = AgentState()
        state["user_id"] = request.user_id
        state["meal_old"] = request.meal_old

        # 2. Lấy workflow
        graph = meal_similarity_graph()

        # 3. Invoke workflow
        result = graph.invoke(state)

        # 4. Trả response
        response = result["meal_new"] or "Không có kết quả"
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")
