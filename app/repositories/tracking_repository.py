from app.repositories.base_repository import BaseRepository
from app.schema.be_models import AddMealRequest, AddDrinkRequest, AddExerciseRequest
from datetime import date
import logging

logger = logging.getLogger(__name__)

class TrackingRepository(BaseRepository):
    # Meal
    def insert_meal(self, meal: AddMealRequest) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                    INSERT INTO MealOfUser (time, mealType, weight, UserInfoId, DishId)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """
            values = (meal.date, meal.mealType, meal.weight, meal.userId, meal.dishId)
            cur.execute(insert_sql, values)
            return cur.fetchone()[0]

    def get_total_nutri_meal(self, date: date, userId: int):
        with self.get_cursor() as cur:
            sql = """
                SELECT 
                SUM((ing.kcal        / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_kcal,
                SUM((ing.carbs       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_carbs,
                SUM((ing.sugar       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_sugar,
                SUM((ing.fiber       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_fiber,
                SUM((ing.protein     / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_protein,
                SUM((ing.saturatedFat / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_saturatedFat,
                SUM((ing.monounSaturatedFat / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_monounSaturatedFat,
                SUM((ing.polyunSaturatedFat / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_polyunSaturatedFat,
                SUM((ing.transFat    / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_transFat,
                SUM((ing.cholesterol / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_cholesterol,
                SUM((ing.vitaminA    / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminA,
                SUM((ing.vitaminC    / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminC,
                SUM((ing.vitaminD    / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminD,
                SUM((ing.vitaminB6   / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminB6,
                SUM((ing.vitaminB12  / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminB12,
                SUM((ing.vitaminE    / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminE,
                SUM((ing.vitaminK    / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_vitaminK,
                SUM((ing.choline     / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_choline,
                SUM((ing.canxi       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_canxi,
                SUM((ing.fe          / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_fe,
                SUM((ing.magie       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_magie,
                SUM((ing.photpho     / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_photpho,
                SUM((ing.kali        / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_kali,
                SUM((ing.natri       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_natri,
                SUM((ing.zn          / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_zn,
                SUM((ing.water       / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_water,
                SUM((ing.caffeine     / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_cafeine,
                SUM((ing.alcohol     / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS total_alcohol
                FROM MealOfUser mu
                JOIN Dish d ON mu.Dishid = d.id
                JOIN (
                SELECT Dishid, SUM(weight) AS total_weight
                FROM IngredientInDish
                GROUP BY Dishid
                ) d_weight ON d.id = d_weight.Dishid
                JOIN IngredientInDish iid ON d.id = iid.Dishid
                JOIN Ingredient ing ON iid.Ingredientid = ing.id
                WHERE mu.UserInfoid = %s
                AND DATE(mu.time) = %s
                GROUP BY mu.UserInfoid, DATE(mu.time);
                """
            cur.execute(sql, (userId, date))
            r = cur.fetchone()
            
            if not r:
                return {}

            return {
                "kcal": r[0],
                "totalCarbs": r[1]+r[2]+r[3],
                "carbs": r[1],
                "sugar": r[2],
                "fiber": r[3],
                "protein": r[4],
                "totalFats": r[1]+r[2]+r[3],
                "saturatedFat": r[5],
                "monounSaturatedFat": r[6],
                "polyunSaturatedFat": r[7],
                "transFat": r[8],
                "cholesterol": r[9],
                "vitaminA": r[10],
                "vitaminC": r[11],
                "vitaminD": r[12],
                "vitaminB6": r[13],
                "vitaminB12": r[14],
                "vitaminE": r[15],
                "vitaminK": r[16],
                "choline": r[17],
                "canxi": r[18],
                "fe": r[19],
                "magie": r[20],
                "photpho": r[21],
                "kali": r[22],
                "natri": r[23],
                "zn": r[24],
                "water": r[25],
                "caffeine": r[26],
                "alcohol": r[27],
            }

    def get_meals_in_day(self, date: date, userId: int, mealType: str):
         with self.get_cursor() as cur:
            sql = """
                    SELECT 
                    mu.id,
                    d.name,
                    d.thumbnail,
                    mu.weight,
                    d.isConfirm,
                    mu.createdAt,
                    SUM((ing.kcal / 100.0) * iid.weight * (mu.weight / d_weight.total_weight)) AS kcal
                    FROM MealOfUser mu
                    JOIN Dish d ON mu.Dishid = d.id
                    JOIN (
                    SELECT Dishid, SUM(weight) AS total_weight
                    FROM IngredientInDish
                    GROUP BY Dishid
                    ) d_weight ON d.id = d_weight.Dishid
                    JOIN IngredientInDish iid ON d.id = iid.Dishid
                    JOIN Ingredient ing ON iid.Ingredientid = ing.id
                    WHERE mu.UserInfoid = %s
                    AND mu.mealType = %s
                    AND DATE(mu.time) = %s
                    GROUP BY mu.id, d.name, d.thumbnail, mu.weight, d.isConfirm, mu.createdAt
                    ORDER BY mu.createdAt;
                """
            cur.execute(sql, (userId, mealType, date))
            rows = cur.fetchall()
            return [
                {"id": r[0], "name": r[1], "thumbnail": r[2], "weight": r[3], "isConfirm": r[4], "createdAt": r[5], "kcal": r[6]}
                for r in rows
            ]

    def delete_meal(self, id: int) -> bool:
        with self.get_cursor() as cur:
            sql = """
                DELETE FROM public.mealofuser
                WHERE id = %s
                RETURNING id;
            """
            cur.execute(sql, (id,))
            return cur.fetchone() is not None

    # Drink
    def insert_drink(self, drink: AddDrinkRequest) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                    INSERT INTO DrinkOfUser (time, amount, UnitDrinkId, UserInfoid)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """
            values = (drink.date, drink.amount, drink.unitDrinkId, drink.userId)
            cur.execute(insert_sql, values)
            return cur.fetchone()[0]

    def get_drinks_in_day(self, date: date, userId: int):
        with self.get_cursor() as cur:
            sql = """
                SELECT 
                d.id,
                d.amount,
                u.baseUnit,
                u.thumbnail,
                d.createdAt
                FROM DrinkOfUser d
                JOIN UnitDrink u ON d.UnitDrinkid = u.id
                WHERE d.UserInfoid = %s
                AND DATE(d.time) = %s
                ORDER BY d.createdAt;
                """
            cur.execute(sql, (userId, date))
            rows = cur.fetchall()
            return [
                {"id": r[0], "amount": r[1], "baseUnit": r[2], "thumbnail": r[3], "createdAt": r[4]}
                for r in rows
            ]

    def delete_drink(self, id: int) -> bool:
        with self.get_cursor() as cur:
            sql = """
                DELETE FROM public.drinkofuser
                WHERE id = %s
                RETURNING id;
            """
            cur.execute(sql, (id,))
            return cur.fetchone() is not None

    def get_total_water(self, date: date, userId: int) -> float:
        with self.get_cursor() as cur:
            sql = """
                SELECT 
                SUM(d.amount * ud.mlPerUnit) AS total_ml
                FROM DrinkOfUser d
                JOIN UnitDrink ud ON d.UnitDrinkid = ud.id
                JOIN UserInfo u ON d.UserInfoid = u.id
                WHERE u.id = %s
                AND DATE(d.time) = %s
                GROUP BY u.id;
                """
            cur.execute(sql, (userId, date))
            row = cur.fetchone()
            return row[0] if row else 0

    # Exercise
    def get_all_exercises(self):
        with self.get_cursor() as cur:
            sql = """
                SELECT id,nameExercise,detail,thumbnail FROM public.exercise
                ORDER BY id ASC 
                """
            cur.execute(sql)
            rows = cur.fetchall()
            return [
                {"id": r[0], "nameExercise": r[1], "detail": r[2], "thumbnail": r[3]}
                for r in rows
            ]

    def insert_exercise(self, exercise: AddExerciseRequest) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                    INSERT INTO ExerciseOfUser (time, minute, levelExerciseId, userInfoId)
                    VALUES (
                        %s,
                        %s,
                        (
                            SELECT le.id 
                            FROM LevelExercise le
                            JOIN Exercise e ON le.Exerciseid = e.id
                            WHERE e.id = %s  
                            AND le.level = %s 
                            LIMIT 1
                        ),
                        %s
                    )
                    RETURNING id;
                """
            values = (exercise.date, exercise.time, exercise.exerciseId, exercise.levelExercise, exercise.userId)
            cur.execute(insert_sql, values)
            return cur.fetchone()[0]

    def get_total_kcal_burned(self, date: date, userId: int) -> float:
        with self.get_cursor() as cur:
             sql = """
                SELECT COALESCE(SUM(eou.minute * le.kcalPerMin), 0) AS total_kcal
                FROM ExerciseOfUser eou
                JOIN LevelExercise le ON eou.LevelExerciseid = le.id
                WHERE eou.UserInfoid = %s
                AND DATE(eou.time) = %s;
                """
             cur.execute(sql, (userId, date))
             row = cur.fetchone()
             return row[0] if row else 0

    def get_exercises_in_day(self, date: date, userId: int):
        with self.get_cursor() as cur:
            sql = """
                    SELECT 
                    eu.id,
                    e.nameExercise,
                    e.thumbnail,
                    le.level,
                    eu.minute,
                    le.kcalPerMin,
                    eu.createdAt
                    FROM ExerciseOfUser eu
                    JOIN LevelExercise le ON eu.LevelExerciseid = le.id
                    JOIN Exercise e ON le.Exerciseid = e.id
                    WHERE eu.UserInfoid = %s
                    AND DATE(eu.time) = %s
                    ORDER BY eu.createdAt;
                """
            cur.execute(sql, (userId, date))
            rows = cur.fetchall()
            return [
                {"id": r[0], "nameExercise": r[1], "thumbnail": r[2], "level": r[3], "minute": r[4], "kcalPerMin": r[5], "createdAt": r[6]}
                for r in rows
            ]

    def delete_exercise(self, id: int) -> bool:
         with self.get_cursor() as cur:
            sql = """
                DELETE FROM public.exerciseofuser
                WHERE id = %s
                RETURNING id;
            """
            cur.execute(sql, (id,))
            return cur.fetchone() is not None
