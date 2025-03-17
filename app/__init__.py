from flask import Flask
from config.settings import Config

def create_app(config_class=Config):
    # 앱 초기화
    app = Flask(__name__, 
               static_folder='../static',
               template_folder='../templates')
    
    # 설정 적용
    app.config.from_object(config_class)
    
    # 라우트 등록
    from app.views.main_routes import main_bp
    from app.views.stt_routes import stt_bp
    from app.views.tts_routes import tts_bp
    from app.views.chat_routes import chat_bp
    from app.views.utility_routes import utility_bp
    from app.views.translation_routes import translation_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(stt_bp)
    app.register_blueprint(tts_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(utility_bp)
    app.register_blueprint(translation_bp)
    
    return app