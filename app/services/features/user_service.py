from app.repositories.user_repository import UserRepository
from app.schema.be_models import UserInfoRequest
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def insert_userinfo_to_db(self, user: UserInfoRequest):
        try:
            new_id = self.user_repository.insert_user_info(user)
            return {"success": True, "id": new_id}
        except Exception as e:
            logger.error(f"Error inserting user info: {e}")
            return {"success": False, "error": str(e)}

    def update_userinfo_in_db(self, id: int, user: UserInfoRequest):
        try:
            result_id = self.user_repository.update_user_info(id, user)
            return {"success": True, "id": result_id}
        except Exception as e:
            logger.error(f"Error updating user info: {e}")
            return {"success": False, "error": str(e)}

    def register_account(self, username: str, password: str):
        try:
            if self.user_repository.check_username_exists(username):
                return {"success": False, "error": "Username already exists"}

            new_id = self.user_repository.create_account(username, password)
            return {"success": True, "id": new_id}

        except Exception as e:
            logger.error(f"Error registering account: {e}")
            return {"success": False, "error": str(e)}

    def login_account(self, username: str, password: str):
        try:
            row = self.user_repository.get_account_by_username(username)
            
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
                user_info_id = self.user_repository.get_user_info_id_by_account_id(account_id)
                if user_info_id:
                    result["idUserInfo"] = user_info_id

            return result

        except Exception as e:
            logger.error(f"Error logging in: {e}")
            return {"success": False, "error": str(e)}

    def get_user_info_by_id(self, id: int):
        try:
            row = self.user_repository.get_user_info_details(id)

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

    def get_required_index_by_id(self, id: int):
        try:
            r = self.user_repository.get_required_index(id)

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
