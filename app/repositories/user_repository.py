from app.repositories.base_repository import BaseRepository
from app.schema.be_models import UserInfoRequest
from app.helpers.nutrition_calculations import build_required_index_data
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    def insert_user_info(self, user: UserInfoRequest):
        with self.get_cursor() as cur:
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

            return new_id

    def update_user_info(self, id: int, user: UserInfoRequest):
        with self.get_cursor() as cur:
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
            
            return id

    def check_username_exists(self, username: str) -> bool:
        with self.get_cursor() as cur:
            cur.execute("SELECT id FROM Account WHERE userName = %s", (username,))
            return cur.fetchone() is not None

    def create_account(self, username: str, password: str) -> int:
        with self.get_cursor() as cur:
            insert_sql = """
                INSERT INTO Account (userName, passWord, isCollectionInfo)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            cur.execute(insert_sql, (username, password, 0))
            return cur.fetchone()[0]

    def get_account_by_username(self, username: str):
        with self.get_cursor() as cur:
            sql = """
                SELECT id, passWord, isCollectionInfo
                FROM Account
                WHERE userName = %s
            """
            cur.execute(sql, (username,))
            return cur.fetchone()

    def get_user_info_id_by_account_id(self, account_id: int):
        with self.get_cursor() as cur:
            cur.execute(
                "SELECT id FROM UserInfo WHERE Accountid = %s LIMIT 1",
                (account_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None

    def get_user_info_details(self, id: int):
        with self.get_cursor() as cur:
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
            cur.execute(sql, (id,))
            return cur.fetchone()

    def get_required_index(self, id: int):
        with self.get_cursor() as cur:
            sql = """
                SELECT *
                FROM requiredindex
                WHERE id = %s;
            """
            cur.execute(sql, (id,))
            return cur.fetchone()
