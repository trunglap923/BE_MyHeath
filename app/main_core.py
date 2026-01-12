from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.user_controller import router as user_router
from app.controllers.food_controller import router as food_router
from app.controllers.tracking_controller import router as tracking_router
from app.controllers.notification_controller import router as notification_router
from app.core.config import settings

app = FastAPI(
    title="Meal Recommendation - Core API",
    description="Core Service for User, Food, and Tracking Management",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Core Routers
app.include_router(user_router)
app.include_router(food_router)
app.include_router(tracking_router)
app.include_router(notification_router)

@app.get("/")
def root():
    return {"message": "Core API is running 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_core:app", host="0.0.0.0", port=8000, reload=True)
