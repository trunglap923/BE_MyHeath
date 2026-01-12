from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.meal_controller import router as meal_router
from app.controllers.chatbot_controller import router as chatbot_router
from app.core.config import settings

app = FastAPI(
    title="Meal Recommendation - Chatbot Agent API",
    description="AI Service for Chatbot and Meal Planning Agents",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include AI Agent Routers
app.include_router(meal_router)
app.include_router(chatbot_router)

@app.get("/")
def root():
    return {"message": "Chatbot Agent API is running 🤖"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_chatbot:app", host="0.0.0.0", port=8001, reload=True)
