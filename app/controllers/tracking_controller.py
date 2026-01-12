from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.features.tracking_service import TrackingService
from app.schema.be_models import AddMealRequest, AddDrinkRequest, AddExerciseRequest
from datetime import date as DateType

router = APIRouter(tags=["Tracking (Meal, Drink, Exercise)"])

def get_tracking_service():
    return TrackingService()

# --- MEAL ---
@router.post("/meal/add")
async def add_meal(data: AddMealRequest, service: TrackingService = Depends(get_tracking_service)):
    result = service.insert_meal_to_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/meal/stat")
async def get_stat_meal(date: DateType, userId: int, mealType: str, service: TrackingService = Depends(get_tracking_service)):
    result = service.stat_meal_in_day(date, userId, mealType)
    if not result["success"]:
        # "Not found" returns success=False in logic.py, but usually empty list is better.
        # But to keep compatibility we follow logic.py
        if result["error"] == "Not found":
            return {"success": True, "statMeals": []}
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/meal/total-nutri")
async def get_total_nutri_meal(date: DateType, userId: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.total_nutri_meal(date, userId)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/meal/delete/{id}")
async def delete_meal(id: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.delete_meal_of_user(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# --- DRINK ---
@router.post("/drink/add")
async def add_drink(data: AddDrinkRequest, service: TrackingService = Depends(get_tracking_service)):
    result = service.insert_drink_to_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/drink/stat")
async def get_stat_drink(date: DateType, userId: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.stat_drink_in_day(date, userId)
    if not result["success"]:
         if result["error"] == "Not found":
            return {"success": True, "statDrinks": []}
         raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/drink/total-water")
async def get_total_water(date: DateType, userId: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.get_total_water(date, userId)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/drink/delete/{id}")
async def delete_drink(id: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.delete_drink_of_user(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# --- EXERCISE ---
@router.post("/exercise/add")
async def add_exercise(data: AddExerciseRequest, service: TrackingService = Depends(get_tracking_service)):
    result = service.insert_exercise_to_db(data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/exercise/list")
async def get_exercises(service: TrackingService = Depends(get_tracking_service)):
    result = service.find_exercise()
    if not result["success"]:
         raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/exercise/stat")
async def get_stat_exercise(date: DateType, userId: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.stat_exercise_in_day(date, userId)
    if not result["success"]:
         if result["error"] == "Not found":
            return {"success": True, "statExercises": []}
         raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/exercise/total-kcal")
async def get_total_kcal_exercise(date: DateType, userId: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.total_kcal_exercise(date, userId)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/exercise/delete/{id}")
async def delete_exercise(id: int, service: TrackingService = Depends(get_tracking_service)):
    result = service.delete_exercise_of_user(id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
