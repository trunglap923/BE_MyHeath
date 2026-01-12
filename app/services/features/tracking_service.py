from datetime import date
from app.repositories.tracking_repository import TrackingRepository
from app.schema.be_models import AddMealRequest, AddDrinkRequest, AddExerciseRequest
import logging

logger = logging.getLogger(__name__)

class TrackingService:
    def __init__(self, tracking_repository: TrackingRepository):
        self.tracking_repository = tracking_repository

    # Meal Tracking
    def insert_meal_to_db(self, meal: AddMealRequest):
        try:
            new_id = self.tracking_repository.insert_meal(meal)
            return {"success": True, "id": new_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def total_nutri_meal(self, date: date, userId: int):
        try:
            nutri_meal = self.tracking_repository.get_total_nutri_meal(date, userId)
            return {"success": True, "nutriMeal": nutri_meal}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stat_meal_in_day(self, date: date, userId: int, mealType: str):
        try:
            stat_meals = self.tracking_repository.get_meals_in_day(date, userId, mealType)
            if not stat_meals:
                return {"success": False, "error": "Not found"}
            
            return {
                "success": True,
                "statMeals": stat_meals
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_meal_of_user(self, id: int):
        try:
            success = self.tracking_repository.delete_meal(id)
            if not success:
                return {"success": False, "error": f"MealOfUser with id {id} not found"}
            
            return {
                "success": True,
                "deletedId": id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Drink Tracking
    def insert_drink_to_db(self, drink: AddDrinkRequest):
        try:
            new_id = self.tracking_repository.insert_drink(drink)
            return {"success": True, "id": new_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stat_drink_in_day(self, date: date, userId: int):
        try:
            stat_drinks = self.tracking_repository.get_drinks_in_day(date, userId)
            if not stat_drinks:
                return {"success": False, "error": "Not found"}

            return {
                "success": True,
                "statDrinks": stat_drinks
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_drink_of_user(self, id: int):
        try:
            success = self.tracking_repository.delete_drink(id)
            if not success:
                 return {"success": False, "error": f"DrinkOfUser with id {id} not found"}

            return {
                "success": True,
                "deletedId": id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_total_water(self, date: date, userId: int):
        try:
            total_water = self.tracking_repository.get_total_water(date, userId)
            return {
                "success": True,
                "totalWater": total_water
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Exercise Tracking
    def find_exercise(self):
        try:
            exercises = self.tracking_repository.get_all_exercises()
            if not exercises:
                return {"success": False, "error": "Not found"}
                
            return {
                "success": True,
                "exercises": exercises
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def insert_exercise_to_db(self, exercise: AddExerciseRequest):
        try:
            new_id = self.tracking_repository.insert_exercise(exercise)
            return {"success": True, "id": new_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def total_kcal_exercise(self, date: date, userId: int):
        try:
            total_kcal = self.tracking_repository.get_total_kcal_burned(date, userId)
            return {
                "success": True,
                "totalKcal": total_kcal
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stat_exercise_in_day(self, date: date, userId: int):
        try:
            stat_exercises = self.tracking_repository.get_exercises_in_day(date, userId)
            if not stat_exercises:
                 return {"success": False, "error": "Not found"}
                 
            return {
                "success": True,
                "statExercises": stat_exercises
            }
        except Exception as e:
             return {"success": False, "error": str(e)}

    def delete_exercise_of_user(self, id: int):
        try:
            success = self.tracking_repository.delete_exercise(id)
            if not success:
                return {"success": False, "error": f"ExerciseOfUser with id {id} not found"}
                
            return {
                "success": True,
                "deletedId": id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
