import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

class Config:
    # 기본 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # 경로 설정
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")
    TEMP_DIR = os.path.join(os.path.dirname(BASE_DIR), "temp")
    
    # OpenAI API 설정
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')