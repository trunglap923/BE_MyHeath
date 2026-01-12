from app.repositories.base_repository import BaseRepository
from app.schema.be_models import DishRequest, IngredientRequest, UpdateIngredientRequest
from app.helpers.nutrition_calculations import calculate_dish_hashtags
import logging

logger = logging.getLogger(__name__)

class FoodRepository(BaseRepository):
    def find_similar_ingredients_names(self, keyword: str, limit: int = 10):
        with self.get_cursor() as cur:
            sql = """
                SELECT name, similarity(name, %s) AS sml
                FROM ingredient
                WHERE name ILIKE %s OR name %% %s
                ORDER BY sml DESC
                LIMIT %s;
            """
            cur.execute(sql, (keyword, f"%{keyword}%", keyword, limit))
            rows = cur.fetchall()
            return [r[0] for r in rows]

    def search_ingredients(self, keyword: str = None):
        with self.get_cursor() as cur:
            if not keyword:
                sql = """
                SELECT id,name,thumbnail,kcal,baseUnit,isConfirm
                FROM ingredient
                ORDER BY id ASC;
                """
                cur.execute(sql)
            else:
                sql = """
                SELECT id,name,thumbnail,kcal,baseUnit,isConfirm
                FROM ingredient
                WHERE name ILIKE %s OR name %% %s
                ORDER BY similarity(name, %s) DESC;
                """
                cur.execute(sql, (f"%{keyword}%", keyword, keyword))
            rows = cur.fetchall()
            return [
                {"id": r[0], "name": r[1], "thumbnail": r[2], "kcal": r[3],"baseUnit": r[4],"isConfirm": r[5]}
                for r in rows
            ]

    def find_similar_dishes_names(self, keyword: str, limit: int = 10):
        with self.get_cursor() as cur:
            sql = """
                SELECT name, similarity(name, %s) AS sml
                FROM dish
                WHERE name ILIKE %s OR name %% %s
                ORDER BY sml DESC
                LIMIT %s;
            """
            cur.execute(sql, (keyword, f"%{keyword}%", keyword, limit))
            rows = cur.fetchall()
            return [r[0] for r in rows]

    def search_dishes(self, keyword: str = None):
        with self.get_cursor() as cur:
            if not keyword:
                sql = """
                SELECT d.id,
                       d.name,
                       d.thumbnail,
                       d.isconfirm,
                       COALESCE(SUM(iid.weight * ing.gramperunit), 0) AS totalgram,
                       COALESCE(SUM((iid.weight * ing.gramperunit / 100.0) * ing.kcal), 0) AS totalkcal
                FROM dish d
                LEFT JOIN ingredientindish iid ON d.id = iid.dishid
                LEFT JOIN ingredient ing ON iid.ingredientid = ing.id
                GROUP BY d.id, d.name, d.thumbnail, d.isconfirm
                ORDER BY d.id ASC;
                """
                cur.execute(sql)
            else:
                sql = """
                SELECT d.id,
                       d.name,
                       d.thumbnail,
                       d.isconfirm,
                       COALESCE(SUM(iid.weight * ing.gramperunit), 0) AS totalgram,
                       COALESCE(SUM((iid.weight * ing.gramperunit / 100.0) * ing.kcal), 0) AS totalkcal
                FROM dish d
                LEFT JOIN ingredientindish iid ON d.id = iid.dishid
                LEFT JOIN ingredient ing ON iid.ingredientid = ing.id
                WHERE d.name ILIKE %s OR d.name %% %s
                GROUP BY d.id, d.name, d.thumbnail, d.isconfirm
                ORDER BY similarity(d.name, %s) DESC;
                """
                cur.execute(sql, (f"%{keyword}%", keyword, keyword))
            
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "thumbnail": r[2],
                    "isConfirm": r[3],
                    "totalGram": float(r[4]),
                    "totalKcal": float(r[5]),
                }
                for r in rows
            ]

    def insert_dish(self, dish: DishRequest) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                INSERT INTO Dish
                (name, thumbnail, isConfirm, description, preparationSteps, cookingSteps)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            values = (
                dish.name,
                dish.thumbnail,
                dish.isConfirm,
                dish.description,
                dish.preparationSteps,
                dish.cookingSteps,
            )
            cur.execute(insert_sql, values)
            new_dish_id = cur.fetchone()[0]

            if dish.ingredients:
                dish_ingredient_data = [
                    (ing.ingredientId, new_dish_id, ing.weight)
                    for ing in dish.ingredients
                ]
                cur.executemany(
                    """
                    INSERT INTO IngredientInDish (Ingredientid, Dishid, weight)
                    VALUES (%s, %s, %s)
                    """,
                    dish_ingredient_data
                )

            all_hashtags = []
            if dish.hashtagId:
                all_hashtags.extend(dish.hashtagId)

            auto_hashtags = calculate_dish_hashtags(new_dish_id)
            if auto_hashtags:
                all_hashtags.extend(auto_hashtags)

            if all_hashtags:
                hashtag_data = [
                    (hashtag_id, new_dish_id) for hashtag_id in all_hashtags
                ]
                cur.executemany(
                    """
                    INSERT INTO HashtagOfDish (Hashtagid, Dishid)
                    VALUES (%s, %s)
                    """,
                    hashtag_data
                )
            
            return new_dish_id

    def get_dish_by_id(self, id: int):
        with self.get_cursor() as cur:
            sql1 = """
                SELECT id,name,thumbnail,isConfirm,description,preparationSteps,cookingSteps
                FROM Dish
                WHERE id = %s; 
                """
            cur.execute(sql1, (id,))
            r1 = cur.fetchone()

            if not r1:
                return None

            dish = {"id": r1[0], "name": r1[1], "thumbnail": r1[2], "isConfirm": r1[3], "description": r1[4], "preparationSteps": r1[5], "cookingSteps": r1[6]}

            sql2 = """
                SELECT iid.IngredientId,i.name,iid.weight,i.baseUnit,i.thumbnail
                FROM IngredientInDish iid
                JOIN Ingredient i ON iid.IngredientId = i.id
                WHERE iid.DishId = %s;
                """
            cur.execute(sql2, (id,))
            r2 = cur.fetchall()

            ingredients = [
                {
                    "ingredientId": r[0],
                    "name": r[1],
                    "weight": r[2],
                    "unit": r[3],
                    "thumbnail": r[4]
                }
                for r in r2
            ]
            dish["ingredients"] = ingredients

            sql3 = """
                SELECT h.id,h.title
                FROM HashtagOfDish hd
                JOIN Hashtag h ON hd.HashtagId = h.id
                WHERE hd.DishId = %s;
                """
            cur.execute(sql3, (id,))
            r3 = cur.fetchall()
            hashtags = [{"id": r[0], "title": r[1]} for r in r3]
            dish["hashtags"] = hashtags
            return dish

    def get_dish_by_name(self, name: str):
         with self.get_cursor() as cur:
            sql1 = """
                SELECT id, name, thumbnail, isConfirm, description, preparationSteps, cookingSteps
                FROM Dish
                WHERE name ILIKE %s
                ORDER BY similarity(name, %s) DESC, LENGTH(name)
                LIMIT 1;
            """
            cur.execute(sql1, (f"%{name}%", name))
            r1 = cur.fetchone()

            if not r1:
                return None

            dish = {
                "id": r1[0],
                "name": r1[1],
                "thumbnail": r1[2],
                "isConfirm": r1[3],
                "description": r1[4],
                "preparationSteps": r1[5],
                "cookingSteps": r1[6]
            }
            dish_id_value = (dish["id"],)

            sql2 = """
                SELECT iid.IngredientId, i.name, iid.weight, i.baseUnit, i.thumbnail
                FROM IngredientInDish iid
                JOIN Ingredient i ON iid.IngredientId = i.id
                WHERE iid.DishId = %s;
            """
            cur.execute(sql2, dish_id_value)
            r2 = cur.fetchall()

            ingredients = [
                {
                    "ingredientId": r[0],
                    "name": r[1],
                    "weight": r[2],
                    "unit": r[3],
                    "thumbnail": r[4]
                }
                for r in r2
            ]
            dish["ingredients"] = ingredients

            sql3 = """
                SELECT h.id, h.title
                FROM HashtagOfDish hd
                JOIN Hashtag h ON hd.HashtagId = h.id
                WHERE hd.DishId = %s;
            """
            cur.execute(sql3, dish_id_value)
            r3 = cur.fetchall()
            hashtags = [{"id": r[0], "title": r[1]} for r in r3]
            dish["hashtags"] = hashtags
            return dish

    def update_dish(self, id: int, dish: DishRequest) -> bool:
        with self.get_cursor() as cur:
            sql1 = """
                UPDATE Dish
                SET name = %s,
                    thumbnail = %s,
                    isConfirm = %s,
                    description = %s,
                    preparationSteps = %s,
                    cookingSteps = %s
                WHERE id = %s;
            """
            value1 = (
                dish.name,
                dish.thumbnail,
                dish.isConfirm,
                dish.description,
                dish.preparationSteps,
                dish.cookingSteps,
                id
            )
            cur.execute(sql1, value1)

            if cur.rowcount == 0:
                return False

            sql2 = "DELETE FROM IngredientInDish WHERE DishId = %s;"
            value2 = (id,)
            cur.execute(sql2, value2)

            if dish.ingredients:
                sql2_insert = """
                    INSERT INTO IngredientInDish (Dishid, Ingredientid, weight)
                    VALUES (%s, %s, %s)
                """
                data_ing = [
                    (id, ing.ingredientId, ing.weight)
                    for ing in dish.ingredients
                ]
                cur.executemany(sql2_insert, data_ing)

            sql3 = "DELETE FROM HashtagOfDish WHERE DishId = %s;"
            value3 = (id,)
            cur.execute(sql3, value3)

            all_hashtags = []
            if dish.hashtagId:
                all_hashtags.extend(dish.hashtagId)

            auto_hashtags = calculate_dish_hashtags(id)
            if auto_hashtags:
                all_hashtags.extend(auto_hashtags)

            if all_hashtags:
                sql3_insert = """
                    INSERT INTO HashtagOfDish (Hashtagid, Dishid)
                    VALUES (%s, %s)
                """
                data_hash = [(h_id, id) for h_id in all_hashtags]
                cur.executemany(sql3_insert, data_hash)
            
            return True

    def get_ingredient_by_id(self, id: int):
        with self.get_cursor() as cur:
            sql = """
                SELECT *
                FROM public.ingredient
                WHERE id = %s;
            """
            cur.execute(sql, (id,))
            row = cur.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "thumbnail": row[2],
                "baseUnit": row[3],
                "gramPerUnit": row[4],
                "isConfirm": row[5],
                "kcal": row[6],
                "carbs": row[7],
                "sugar": row[8],
                "fiber": row[9],
                "protein": row[10],
                "saturatedFat": row[11],
                "monounSaturatedFat": row[12],
                "polyunSaturatedFat": row[13],
                "transFat": row[14],
                "cholesterol": row[15],
                "vitaminA": row[16],
                "vitaminD": row[17],
                "vitaminC": row[18],
                "vitaminB6": row[19],
                "vitaminB12": row[20],
                "vitaminE": row[21],
                "vitaminK": row[22],
                "choline": row[23],
                "canxi": row[24],
                "fe": row[25],
                "magie": row[26],
                "photpho": row[27],
                "kali": row[28],
                "natri": row[29],
                "zn": row[30],
                "water": row[31],
                "caffeine": row[32],
                "alcohol": row[33],
            }

    def insert_ingredient(self, ingredient: IngredientRequest) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                INSERT INTO Ingredient (
                    name, thumbnail, baseUnit, gramPerUnit, isConfirm, kcal, carbs, sugar, fiber, protein,
                    saturatedFat, monounSaturatedFat, polyunSaturatedFat, transFat, cholesterol,
                    vitaminA, vitaminD, vitaminC, vitaminB6, vitaminB12, vitaminE, vitaminK,
                    choline, canxi, fe, magie, photpho, kali, natri, zn, water, caffeine, alcohol
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id;
            """

            values = (
                ingredient.name,
                ingredient.thumbnail,
                ingredient.baseUnit,
                ingredient.gramPerUnit,
                ingredient.isConfirm,
                ingredient.kcal,
                ingredient.carbs,
                ingredient.sugar,
                ingredient.fiber,
                ingredient.protein,
                ingredient.saturatedFat,
                ingredient.monounSaturatedFat,
                ingredient.polyunSaturatedFat,
                ingredient.transFat,
                ingredient.cholesterol,
                ingredient.vitaminA,
                ingredient.vitaminD,
                ingredient.vitaminC,
                ingredient.vitaminB6,
                ingredient.vitaminB12,
                ingredient.vitaminE,
                ingredient.vitaminK,
                ingredient.choline,
                ingredient.canxi,
                ingredient.fe,
                ingredient.magie,
                ingredient.photpho,
                ingredient.kali,
                ingredient.natri,
                ingredient.zn,
                ingredient.water,
                ingredient.caffeine,
                ingredient.alcohol
            )

            cur.execute(insert_sql, values)
            new_id = cur.fetchone()[0]
            return new_id

    def update_ingredient(self, ingredient: UpdateIngredientRequest):
        with self.get_cursor() as cur:
            update_sql = """
                UPDATE Ingredient
                SET
                    name = %s,
                    thumbnail = %s,
                    baseUnit = %s,
                    gramPerUnit = %s,
                    isConfirm = %s,
                    kcal = %s,
                    carbs = %s,
                    sugar = %s,
                    fiber = %s,
                    protein = %s,
                    saturatedFat = %s,
                    monounSaturatedFat = %s,
                    polyunSaturatedFat = %s,
                    transFat = %s,
                    cholesterol = %s,
                    vitaminA = %s,
                    vitaminD = %s,
                    vitaminC = %s,
                    vitaminB6 = %s,
                    vitaminB12 = %s,
                    vitaminE = %s,
                    vitaminK = %s,
                    choline = %s,
                    canxi = %s,
                    fe = %s,
                    magie = %s,
                    photpho = %s,
                    kali = %s,
                    natri = %s,
                    zn = %s,
                    water = %s,
                    caffeine = %s,
                    alcohol = %s
                WHERE id = %s;
            """

            values = (
                ingredient.name,
                ingredient.thumbnail,
                ingredient.baseUnit,
                ingredient.gramPerUnit,
                ingredient.isConfirm,
                ingredient.kcal,
                ingredient.carbs,
                ingredient.sugar,
                ingredient.fiber,
                ingredient.protein,
                ingredient.saturatedFat,
                ingredient.monounSaturatedFat,
                ingredient.polyunSaturatedFat,
                ingredient.transFat,
                ingredient.cholesterol,
                ingredient.vitaminA,
                ingredient.vitaminD,
                ingredient.vitaminC,
                ingredient.vitaminB6,
                ingredient.vitaminB12,
                ingredient.vitaminE,
                ingredient.vitaminK,
                ingredient.choline,
                ingredient.canxi,
                ingredient.fe,
                ingredient.magie,
                ingredient.photpho,
                ingredient.kali,
                ingredient.natri,
                ingredient.zn,
                ingredient.water,
                ingredient.caffeine,
                ingredient.alcohol,
                ingredient.id
            )

            cur.execute(update_sql, values)
