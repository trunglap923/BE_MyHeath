from datetime import date
from app.core.database import get_connection
from app.schema.be_models import AddMealRequest, AddDrinkRequest, AddExerciseRequest
import logging

logger = logging.getLogger(__name__)

class TrackingService:
    # Meal Tracking
    def insert_meal_to_db(self, meal: AddMealRequest):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            insert_sql = """
                    INSERT INTO MealOfUser (time, mealType, weight, UserInfoId, DishId)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """
            values = (meal.date, meal.mealType, meal.weight, meal.userId, meal.dishId)

            cur.execute(insert_sql, values)
            new_id = cur.fetchone()[0]
            conn.commit()

            return {"success": True, "id": new_id}

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def total_nutri_meal(self, date: date, userId: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

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
            
            values = (userId,date)
            cur.execute(sql,values)
            r = cur.fetchone()

            if not r:
                return {"success": True, "nutriMeal": {}}

            nutri_meal = {
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
            result = {
                "success": True,
                "nutriMeal": nutri_meal
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def stat_meal_in_day(self, date: date, userId: int, mealType: str):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

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
            values = (userId, mealType, date)
            cur.execute(sql,values)
            rows = cur.fetchall()

            if not rows:
                return {"success": False, "error": "Not found"}

            stat_meals = [
                {"id": r[0], "name": r[1], "thumbnail": r[2], "weight": r[3], "isConfirm": r[4], "createdAt": r[5], "kcal": r[6]}
                for r in rows
            ]

            result = {
                "success": True,
                "statMeals": stat_meals
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_meal_of_user(self, id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                DELETE FROM public.mealofuser
                WHERE id = %s
                RETURNING id;
            """
            value=(id,)
            cur.execute(sql,value)
            deleted_row = cur.fetchone()
            conn.commit()

            if not deleted_row:
                return {"success": False, "error": f"MealOfUser with id {id} not found"}

            result = {
                "success": True,
                "deletedId": deleted_row[0]
            }
            return result

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    # Drink Tracking
    def insert_drink_to_db(self, drink: AddDrinkRequest):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            insert_sql = """
                    INSERT INTO DrinkOfUser (time, amount, UnitDrinkId, UserInfoid)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """
            values = (drink.date, drink.amount, drink.unitDrinkId, drink.userId)

            cur.execute(insert_sql, values)
            new_id = cur.fetchone()[0]
            conn.commit()

            return {"success": True, "id": new_id}

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def stat_drink_in_day(self, date: date, userId: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

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
            values = (userId, date)
            cur.execute(sql,values)
            rows = cur.fetchall()

            if not rows:
                return {"success": False, "error": "Not found"}

            stat_drinks = [
                {"id": r[0], "amount": r[1], "baseUnit": r[2], "thumbnail": r[3], "createdAt": r[4]}
                for r in rows
            ]

            result = {
                "success": True,
                "statDrinks": stat_drinks
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_drink_of_user(self, id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                DELETE FROM public.drinkofuser
                WHERE id = %s
                RETURNING id;
            """
            value=(id,)
            cur.execute(sql,value)
            deleted_row = cur.fetchone()
            conn.commit()

            if not deleted_row:
                return {"success": False, "error": f"DrinkOfUser with id {id} not found"}

            result = {
                "success": True,
                "deletedId": deleted_row[0]
            }
            return result

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def get_total_water(self, date: date, userId: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

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
            values = (userId,date)
            cur.execute(sql,values)
            row = cur.fetchone()
            total_water = row[0] if row else 0

            result = {
                "success": True,
                "totalWater": total_water
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    # Exercise Tracking
    def find_exercise(self):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                SELECT id,nameExercise,detail,thumbnail FROM public.exercise
                ORDER BY id ASC 
                """
            cur.execute(sql)
            rows = cur.fetchall()

            if not rows:
                return {"success": False, "error": "Not found"}

            exercise_list = [
                {"id": r[0], "nameExercise": r[1], "detail": r[2], "thumbnail": r[3]}
                for r in rows
            ]

            result = {
                "success": True,
                "exercises": exercise_list
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def insert_exercise_to_db(self, exercise: AddExerciseRequest):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

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
            new_id = cur.fetchone()[0]
            conn.commit()

            return {"success": True, "id": new_id}

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def total_kcal_exercise(self, date: date, userId: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                SELECT COALESCE(SUM(eou.minute * le.kcalPerMin), 0) AS total_kcal
                FROM ExerciseOfUser eou
                JOIN LevelExercise le ON eou.LevelExerciseid = le.id
                WHERE eou.UserInfoid = %s
                AND DATE(eou.time) = %s;
                """
            
            values = (userId,date)
            cur.execute(sql,values)
            total_kcal = cur.fetchone()[0]

            result = {
                "success": True,
                "totalKcal": total_kcal
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def stat_exercise_in_day(self, date: date, userId: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

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
            values = (userId, date)
            cur.execute(sql,values)
            rows = cur.fetchall()

            if not rows:
                return {"success": False, "error": "Not found"}

            stat_exercises = [
                {"id": r[0], "nameExercise": r[1], "thumbnail": r[2], "level": r[3], "minute": r[4], "kcalPerMin": r[5], "createdAt": r[6]}
                for r in rows
            ]

            result = {
                "success": True,
                "statExercises": stat_exercises
            }
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_exercise_of_user(self, id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                DELETE FROM public.exerciseofuser
                WHERE id = %s
                RETURNING id;
            """
            value=(id,)
            cur.execute(sql,value)
            deleted_row = cur.fetchone()
            conn.commit()

            if not deleted_row:
                return {"success": False, "error": f"ExerciseOfUser with id {id} not found"}

            result = {
                "success": True,
                "deletedId": deleted_row[0]
            }
            return result

        except Exception as e:
            if conn: conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()
