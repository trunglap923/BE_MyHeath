from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from chatbot.routes.chat_router import router as chat_router
from chatbot.routes.daily_plan_route import router as daily_plan_router
from chatbot.routes.food_replace_route import router as food_replace_router
from chatbot.routes.meal_replace_route import router as meal_replace_router
from chatbot.models.embeddings import start_background_model, embeddings_model

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Gọi load model background
    start_background_model()
    print("🚀 Background model loading started")
    yield
    # Nếu cần, có thể thêm cleanup code khi shutdown
    print("Shutdown complete")

app = FastAPI(
    title="AI Meal Chatbot API",
    description="API gợi ý món ăn, thực đơn, và tư vấn dinh dưỡng bằng AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ đổi sau nếu cần bảo mật
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký route
app.include_router(chat_router)
app.include_router(daily_plan_router)
app.include_router(food_replace_router)
app.include_router(meal_replace_router)

# Endpoint root
@app.get("/")
def root():
    return {"message": "AI Meal Chatbot API is running 🚀"}

# Endpoint check trạng thái model
@app.get("/model_status")
def model_status():
    if embeddings_model is None:
        return {"status": "loading"}
    return {"status": "ready"}
