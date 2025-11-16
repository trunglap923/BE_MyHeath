from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from chatbot.agents.states.state import AgentState
from chatbot.agents.graphs.food_similarity_graph import food_similarity_graph

# --- Định nghĩa request body ---
class Request(BaseModel):
    user_id: str
    food_old: dict

# --- Tạo router ---
router = APIRouter(
    prefix="/food-replace",
    tags=["Food Replace"]
)

@router.post("/")
def chat(request: Request):
    try:
        
        print("Nhận được yêu cầu chat từ user:", request.user_id)
        
        # 1. Tạo state mới
        state = AgentState()
        state["user_id"] = request.user_id
        state["food_old"] = request.food_old

        # 2. Lấy workflow
        graph = food_similarity_graph()

        # 3. Invoke workflow
        result = graph.invoke(state)

        # 4. Trả response
        response = result["food_new"] or "Không có kết quả"
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chatbot: {e}")
