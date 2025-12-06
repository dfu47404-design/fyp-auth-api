from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = os.getenv('APP_NAME', 'FYPAuthAPI')
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXP_MIN = int(os.getenv('JWT_EXP_MIN', '60'))
