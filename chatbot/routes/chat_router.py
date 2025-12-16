from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from chatbot.agents.graphs.chatbot_graph import workflow_chatbot
import logging
import json
from chatbot.models.llm_setup import llm_stream

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# # --- Định nghĩa request body ---
class ChatRequest(BaseModel):
    user_id: str
    thread_id: str
    message: str

# --- Tạo router ---
router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)

try:
    chatbot_app = workflow_chatbot()
    logger.info("✅ Chatbot Graph compiled successfully!")
except Exception as e:
    logger.error(f"❌ Failed to compile Chatbot Graph: {e}")
    raise e

async def generate_chat_response(initial_state, config):
    async for event in chatbot_app.astream_events(
        initial_state, 
        config=config, 
        version="v2" 
    ):
        if event["event"] == "on_chat_model_stream":
            
            data = event.get("data", {})
            chunk = data.get("chunk")
            
            if chunk and hasattr(chunk, "content") and chunk.content:
                yield chunk.content

@router.post("/")
async def chat(request: ChatRequest):
    logger.info(f"Nhận được tin nhắn chat từ user: {request.user_id}")
    config = {"configurable": {"thread_id": request.thread_id}}

    initial_state = {
        "user_id": request.user_id,
        "messages": [HumanMessage(content=request.message)]
    }
    
    return StreamingResponse(
        generate_chat_response(initial_state, config), 
        media_type="text/plain"
    )
