from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.features.food_service import FoodService
from app.schema.be_models import DishRequest, IngredientRequest, UpdateIngredientRequest
from typing import Optional

router = APIRouter(prefix="/food", tags=["Food & Dish"])

def get_food_service():
    return FoodService()

@router.get("/ingredient/search")
async def search_food(keyword: str = Query("", alias="keyWord"), service: FoodService = Depends(get_food_service)):
    result = service.find_food(keyword)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/ingredient/similar")
async def similar_food(keyword: str = Query(..., alias="keyWord"), service: FoodService = Depends(get_food_service)):
    result = service.similar_food(keyword)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/dish/search")
async def search_dish(keyword: str = Query("", alias="keyWord"), service: FoodService = Depends(get_food_service)):
    result = service.find_dish(keyword)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/dish/similar")
async def similar_dish(keyword: str = Query(..., alias="keyWord"), service: FoodService = Depends(get_food_service)):
    result = service.similar_dish(keyword)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/dish/add")
async def add_dish(data: DishRequest, service: FoodService = Depends(get_food_service)):
    result = service.insert_dish_to_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/dish/update/{id}")
async def update_dish(id: int, data: DishRequest, service: FoodService = Depends(get_food_service)):
    result = service.update_dish_in_db(id, data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/dish/{id}")
async def get_dish(id: int, service: FoodService = Depends(get_food_service)):
    result = service.get_dish_by_id(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/dish/name/{name}")
async def get_dish_by_name(name: str, service: FoodService = Depends(get_food_service)):
    result = service.get_dish_by_name(name)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/ingredient/add")
async def add_ingredient(data: IngredientRequest, service: FoodService = Depends(get_food_service)):
    result = service.insert_ingredient_to_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/ingredient/update")
async def update_ingredient(data: UpdateIngredientRequest, service: FoodService = Depends(get_food_service)):
    result = service.update_ingredient_in_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/ingredient/{id}")
async def get_ingredient(id: int, service: FoodService = Depends(get_food_service)):
    result = service.get_ingredient_by_id(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
