from app.core.database import get_connection
from app.schema.be_models import UserInfoRequest
from app.helpers.nutrition_calculations import build_required_index_data
import logging

logger = logging.getLogger(__name__)

class UserService:
    def insert_userinfo_to_db(self, user: UserInfoRequest):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            insert_sql = """
                INSERT INTO UserInfo 
                (fullName, gender, age, height, weight, weightTarget, dateTarget, Accountid, ActivityLevelid, Dietid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            values = (
                user.fullName,
                user.gender,
                user.age,
                user.height,
                user.weight,
                user.weightTarget,
                user.dateTarget,
                user.Accountid,
                user.ActivityLevelid,
                user.Dietid,
            )
            cur.execute(insert_sql, values)
            new_id = cur.fetchone()[0]

            if user.LimitFoodid:
                limit_food_data = [(new_id, lf_id) for lf_id in user.LimitFoodid]
                cur.executemany(
                    "INSERT INTO LimitFoodUser (UserInfoid, LimitFoodid) VALUES (%s, %s)",
                    limit_food_data
                )
            if user.HealthStatusid:
                health_status_data = [(new_id, hs_id) for hs_id in user.HealthStatusid]
                cur.executemany(
                    "INSERT INTO HealthStatusUser (UserInfoid, HealthStatusid) VALUES (%s, %s)",
                    health_status_data
                )

            update_sql = """
                UPDATE Account
                SET isCollectionInfo = 1
                WHERE id = %s
            """
            cur.execute(update_sql, (user.Accountid,))

            index_data = build_required_index_data(user)

            required_sql = """
                INSERT INTO RequiredIndex 
                (UserInfoid, bmr, tdee, targetCalories, water, protein, totalFat,
                saturatedFat, monounSaturatedFat, polyunSaturatedFat, transFat,
                carbohydrate, carbs, sugar, fiber, cholesterol, vitaminA, vitaminD,
                vitaminC, vitaminB6, vitaminB12, vitaminE, vitaminK, choline, canxi,
                fe, magie, photpho, kali, natri, zn, caffeine, alcohol)
                VALUES (%(UserInfoid)s, %(bmr)s, %(tdee)s, %(targetCalories)s, %(water)s,
                        %(protein)s, %(totalFat)s, %(saturatedFat)s, %(monounSaturatedFat)s,
                        %(polyunSaturatedFat)s, %(transFat)s, %(carbohydrate)s, %(carbs)s,
                        %(sugar)s, %(fiber)s, %(cholesterol)s, %(vitaminA)s, %(vitaminD)s,
                        %(vitaminC)s, %(vitaminB6)s, %(vitaminB12)s, %(vitaminE)s,
                        %(vitaminK)s, %(choline)s, %(canxi)s, %(fe)s, %(magie)s,
                        %(photpho)s, %(kali)s, %(natri)s, %(zn)s, %(caffeine)s,
                        %(alcohol)s)
                RETURNING id;
            """
            required_values = index_data["requiredIndex"]
            required_values["UserInfoid"] = new_id

            cur.execute(required_sql, required_values)
            required_id = cur.fetchone()[0]

            hashtags = []
            for tag in index_data["banHashtags"]:
                hashtags.append((required_id, tag, "ban"))
            for tag in index_data["encourageHashtags"]:
                hashtags.append((required_id, tag, "encourage"))
            for tag in index_data["limitHashtags"]:
                hashtags.append((required_id, tag, "limit"))

            if hashtags:
                cur.executemany(
                    "INSERT INTO ImportantHashtag (RequiredIndexid, Hashtagid, typeRequest) VALUES (%s, %s, %s)",
                    hashtags
                )

            conn.commit()
            return {"success": True, "id": new_id}

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error inserting user info: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def update_userinfo_in_db(self, id: int, user: UserInfoRequest):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            update_sql = """
                UPDATE UserInfo
                SET height = %s,
                    weight = %s,
                    weightTarget = %s,
                    dateTarget = %s,
                    ActivityLevelid = %s,
                    Dietid = %s
                WHERE id = %s
            """
            cur.execute(update_sql, (
                user.height,
                user.weight,
                user.weightTarget,
                user.dateTarget,
                user.ActivityLevelid,
                user.Dietid,
                id
            ))

            cur.execute("DELETE FROM LimitFoodUser WHERE UserInfoid = %s", (id,))
            if user.LimitFoodid:
                limit_food_data = [(id, lf_id) for lf_id in user.LimitFoodid]
                cur.executemany(
                    "INSERT INTO LimitFoodUser (UserInfoid, LimitFoodid) VALUES (%s, %s)",
                    limit_food_data
                )

            cur.execute("DELETE FROM HealthStatusUser WHERE UserInfoid = %s", (id,))
            if user.HealthStatusid:
                health_status_data = [(id, hs_id) for hs_id in user.HealthStatusid]
                cur.executemany(
                    "INSERT INTO HealthStatusUser (UserInfoid, HealthStatusid) VALUES (%s, %s)",
                    health_status_data
                )

            index_data = build_required_index_data(user)

            cur.execute("SELECT id FROM RequiredIndex WHERE UserInfoid = %s", (id,))
            row = cur.fetchone()

            if row:
                required_id = row[0]
                update_req_sql = """
                    UPDATE RequiredIndex
                    SET bmr = %(bmr)s, tdee = %(tdee)s, targetCalories = %(targetCalories)s,
                        water = %(water)s, protein = %(protein)s, totalFat = %(totalFat)s,
                        saturatedFat = %(saturatedFat)s, monounSaturatedFat = %(monounSaturatedFat)s,
                        polyunSaturatedFat = %(polyunSaturatedFat)s, transFat = %(transFat)s,
                        carbohydrate = %(carbohydrate)s, carbs = %(carbs)s, sugar = %(sugar)s,
                        fiber = %(fiber)s, cholesterol = %(cholesterol)s, vitaminA = %(vitaminA)s,
                        vitaminD = %(vitaminD)s, vitaminC = %(vitaminC)s, vitaminB6 = %(vitaminB6)s,
                        vitaminB12 = %(vitaminB12)s, vitaminE = %(vitaminE)s, vitaminK = %(vitaminK)s,
                        choline = %(choline)s, canxi = %(canxi)s, fe = %(fe)s, magie = %(magie)s,
                        photpho = %(photpho)s, kali = %(kali)s, natri = %(natri)s, zn = %(zn)s,
                        caffeine = %(caffeine)s, alcohol = %(alcohol)s
                    WHERE id = %(required_id)s
                """
                required_values = index_data["requiredIndex"]
                required_values["required_id"] = required_id
                cur.execute(update_req_sql, required_values)
            else:
                required_sql = """
                    INSERT INTO RequiredIndex (UserInfoid, bmr, tdee, targetCalories, water, protein, totalFat,
                    saturatedFat, monounSaturatedFat, polyunSaturatedFat, transFat, carbohydrate, carbs, sugar,
                    fiber, cholesterol, vitaminA, vitaminD, vitaminC, vitaminB6, vitaminB12, vitaminE,
                    vitaminK, choline, canxi, fe, magie, photpho, kali, natri, zn, caffeine, alcohol)
                    VALUES (%(UserInfoid)s, %(bmr)s, %(tdee)s, %(targetCalories)s, %(water)s, %(protein)s,
                    %(totalFat)s, %(saturatedFat)s, %(monounSaturatedFat)s, %(polyunSaturatedFat)s,
                    %(transFat)s, %(carbohydrate)s, %(carbs)s, %(sugar)s, %(fiber)s, %(cholesterol)s,
                    %(vitaminA)s, %(vitaminD)s, %(vitaminC)s, %(vitaminB6)s, %(vitaminB12)s, %(vitaminE)s,
                    %(vitaminK)s, %(choline)s, %(canxi)s, %(fe)s, %(magie)s, %(photpho)s, %(kali)s,
                    %(natri)s, %(zn)s, %(caffeine)s, %(alcohol)s)
                    RETURNING id;
                """
                required_values = index_data["requiredIndex"]
                required_values["UserInfoid"] = id
                cur.execute(required_sql, required_values)
                required_id = cur.fetchone()[0]

            cur.execute("DELETE FROM ImportantHashtag WHERE RequiredIndexid = %s", (required_id,))
            hashtags = []
            for tag in index_data["banHashtags"]:
                hashtags.append((required_id, tag, "ban"))
            for tag in index_data["encourageHashtags"]:
                hashtags.append((required_id, tag, "encourage"))
            for tag in index_data["limitHashtags"]:
                hashtags.append((required_id, tag, "limit"))

            if hashtags:
                cur.executemany(
                    "INSERT INTO ImportantHashtag (RequiredIndexid, Hashtagid, typeRequest) VALUES (%s, %s, %s)",
                    hashtags
                )
            conn.commit()
            return {"success": True, "id": id}

        except Exception as e:
            if conn: conn.rollback()
            logger.error(f"Error updating user info: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def register_account(self, username: str, password: str):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT id FROM Account WHERE userName = %s", (username,))
            if cur.fetchone() is not None:
                return {"success": False, "error": "Username already exists"}

            insert_sql = """
                INSERT INTO Account (userName, passWord, isCollectionInfo)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            cur.execute(insert_sql, (username, password, 0))
            new_id = cur.fetchone()[0]
            conn.commit()

            return {"success": True, "id": new_id}

        except Exception as e:
            if conn: conn.rollback()
            logger.error(f"Error registering account: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def login_account(self, username: str, password: str):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                SELECT id, passWord, isCollectionInfo
                FROM Account
                WHERE userName = %s
            """
            cur.execute(sql, (username,))
            row = cur.fetchone()

            if row is None:
                return {"success": False, "error": "Username not found"}

            account_id, db_password, is_collection_info = row
            if db_password != password:
                return {"success": False, "error": "Incorrect password"}

            result = {
                "success": True,
                "account": {
                    "id": account_id,
                    "userName": username,
                    "isCollectionInfo": is_collection_info
                }
            }

            if is_collection_info == 1:
                cur.execute(
                    "SELECT id FROM UserInfo WHERE Accountid = %s LIMIT 1",
                    (account_id,)
                )
                user_info_row = cur.fetchone()
                if user_info_row:
                    result["idUserInfo"] = user_info_row[0]

            return result

        except Exception as e:
            logger.error(f"Error logging in: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def get_user_info_by_id(self, id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            sql = """
                SELECT
                  u.id,
                  u.fullname,
                  u.age,
                  u.height,
                  u.weight,
                  al.title AS activityLevel,
                  STRING_AGG(DISTINCT lf.title, ', ') FILTER (WHERE lf.title IS NOT NULL) AS limitFood,
                  STRING_AGG(DISTINCT hs.title, ', ') FILTER (WHERE hs.title IS NOT NULL) AS healthStatus,
                  d.title AS diet,
                  ri.bmr,
                  ri.tdee,
                  u.gender
                FROM public.userinfo u
                LEFT JOIN public.activitylevel al ON u.activitylevelid = al.id
                LEFT JOIN public.diet d ON u.dietid = d.id
                LEFT JOIN public.requiredindex ri ON ri.userinfoid = u.id
                LEFT JOIN public.limitfooduser lfu ON lfu.userinfoid = u.id
                LEFT JOIN public.limitfood lf ON lfu.limitfoodid = lf.id
                LEFT JOIN public.healthstatususer hsu ON hsu.userinfoid = u.id
                LEFT JOIN public.healthstatus hs ON hsu.healthstatusid = hs.id
                WHERE u.id = %s
                GROUP BY
                  u.id, u.fullname, u.age, u.height, u.weight,
                  al.title, d.title, ri.bmr, ri.tdee, u.gender;
            """
            values = (id,)
            cur.execute(sql, values)
            row = cur.fetchone()

            if not row:
                return {"success": False, "error": "User not found"}

            user_info = {
                "id": row[0],
                "fullname": row[1],
                "age": row[2],
                "height": row[3],
                "weight": row[4],
                "activityLevel": row[5],
                "limitFood": row[6],
                "healthStatus": row[7],
                "diet": row[8],
                "bmr": row[9],
                "tdee": row[10],
                "gender": row[11],
            }

            return {"success": True, "userInfo": user_info}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()

    def get_required_index_by_id(self, id: int):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            value = (id,)

            sql = """
                SELECT *
                FROM requiredindex
                WHERE id = %s;
            """
            cur.execute(sql, value)
            r = cur.fetchone()

            if not r:
                return {"success": False, "error": "RequiredIndex not found"}

            required_index = {
                "id": r[0],
                "userinfoid": r[1],
                "bmr": r[2],
                "tdee": r[3],
                "targetcalories": r[4],
                "water": r[5],
                "protein": r[6],
                "totalfat": r[7],
                "saturatedfat": r[8],
                "monounsaturatedfat": r[9],
                "polyunsaturatedfat": r[10],
                "transfat": r[11],
                "carbohydrate": r[12],
                "carbs": r[13],
                "sugar": r[14],
                "fiber": r[15],
                "cholesterol": r[16],
                "vitamina": r[17],
                "vitamind": r[18],
                "vitaminc": r[19],
                "vitaminb6": r[20],
                "vitaminb12": r[21],
                "vitamine": r[22],
                "vitamink": r[23],
                "choline": r[24],
                "canxi": r[25],
                "fe": r[26],
                "magie": r[27],
                "photpho": r[28],
                "kali": r[29],
                "natri": r[30],
                "zn": r[31],
                "caffeine": r[32],
                "alcohol": r[33],
            }

            return {"success": True, "requiredIndex": required_index}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                cur.close()
                conn.close()
