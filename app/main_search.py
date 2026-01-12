from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.food_management_controller import router as food_management_router
from app.controllers.food_similarity_controller import router as food_similarity_router
from app.core.config import settings

app = FastAPI(
    title="Meal Recommendation - Search API",
    description="Search Service for Vector Database and Food Similarity",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Search/Vector Routers
app.include_router(food_similarity_router)
app.include_router(food_management_router)

@app.get("/")
def root():
    return {"message": "Search API is running 🔍"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_search:app", host="0.0.0.0", port=8002, reload=True)
