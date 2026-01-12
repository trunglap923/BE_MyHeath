from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    ELASTIC_CLOUD_URL = os.getenv('ELASTIC_CLOUD_URL')
    ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY')
    FOOD_DB_INDEX = os.getenv('FOOD_DB_INDEX')
    POLICY_DB_INDEX = os.getenv('POLICY_DB_INDEX')
    API_BASE_URL = os.getenv('API_BASE_URL')

    # Database
    DB_HOST = os.getenv('DB_HOST', "localhost")
    DB_NAME = os.getenv('DB_NAME', "DataMyHealthFinal")
    DB_USER = os.getenv('DB_USER', "postgres")
    DB_PASS = os.getenv('DB_PASS', "1234")
    DB_PORT = os.getenv('DB_PORT', "5432")

settings = Config()
