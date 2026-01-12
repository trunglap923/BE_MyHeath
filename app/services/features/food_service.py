from app.repositories.food_repository import FoodRepository
from app.schema.be_models import DishRequest, IngredientRequest, UpdateIngredientRequest
import logging

logger = logging.getLogger(__name__)

class FoodService:
    def __init__(self, food_repository: FoodRepository):
        self.food_repository = food_repository

    def similar_food(self, keyword: str):
        try:
            similar_list = self.food_repository.find_similar_ingredients_names(keyword)
            if not similar_list:
                return {"success": False, "error": "Similar food not found"}

            return {"success": True, "similar": similar_list}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_food(self, keyword: str):
        try:
            similar_list = self.food_repository.search_ingredients(keyword)
            if not similar_list:
                return {"success": False, "error": "Similar food not found"}

            return {"success": True, "similar": similar_list}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def similar_dish(self, keyword: str):
        try:
            similar_list = self.food_repository.find_similar_dishes_names(keyword)
            if not similar_list:
                return {"success": False, "error": "Similar food not found"}

            return {"success": True, "similar": similar_list}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_dish(self, keyword: str):
        try:
            similar_list = self.food_repository.search_dishes(keyword)
            if not similar_list:
                return {"success": False, "error": "Similar food not found"}

            return {"success": True, "similar": similar_list}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def insert_dish_to_db(self, dish: DishRequest):
        try:
            new_dish_id = self.food_repository.insert_dish(dish)
            return {"success": True, "id": new_dish_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_dish_by_id(self, id: int):
        try:
            dish = self.food_repository.get_dish_by_id(id)
            if not dish:
                return {"success": False, "error": "Dish not found"}
            return {"success": True, "dish": dish}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_dish_by_name(self, name: str):
        try:
            dish = self.food_repository.get_dish_by_name(name)
            if not dish:
                return {"success": False, "error": "Dish not found"}
            return {"success": True, "dish": dish}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_dish_in_db(self, id: int, dish: DishRequest):
        try:
            success = self.food_repository.update_dish(id, dish)
            if not success:
                return {"success": False, "error": "Dish not found"}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_ingredient_by_id(self, id: int):
        try:
            ingredient = self.food_repository.get_ingredient_by_id(id)
            if not ingredient:
                return {"success": False, "error": "Ingredient not found"}
            return {"success": True, "ingredient": ingredient}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def insert_ingredient_to_db(self, ingredient: IngredientRequest):
        try:
            new_id = self.food_repository.insert_ingredient(ingredient)
            return {"success": True, "id": new_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_ingredient_in_db(self, ingredient: UpdateIngredientRequest):
        try:
            self.food_repository.update_ingredient(ingredient)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
