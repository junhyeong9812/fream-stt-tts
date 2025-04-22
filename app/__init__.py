from flask import Flask
from config.settings import Config

def create_app(config_class=Config):
    # 앱 초기화
    app = Flask(__name__, 
               static_url_path='/talk/static', 
               static_folder='../static',
               template_folder='../templates')
    
    # 설정 적용
    app.config.from_object(config_class)

    # APPLICATION_ROOT 설정 추가
    # app.config['APPLICATION_ROOT'] = '/talk'
    
    # 라우트 등록
    from app.views.main_routes import main_bp
    from app.views.stt_routes import stt_bp
    from app.views.tts_routes import tts_bp
    from app.views.chat_routes import chat_bp
    from app.views.utility_routes import utility_bp
    from app.views.translation_routes import translation_bp
    # 배포환경
    # app.register_blueprint(main_bp)
    # app.register_blueprint(stt_bp)
    # app.register_blueprint(tts_bp)
    # app.register_blueprint(chat_bp)
    # app.register_blueprint(utility_bp)
    # app.register_blueprint(translation_bp)
    # 로컬 환경
    app.register_blueprint(main_bp)
    app.register_blueprint(stt_bp,         url_prefix='/talk')
    app.register_blueprint(tts_bp, url_prefix='/talk/tts') 
    app.register_blueprint(chat_bp,        url_prefix='/talk')
    app.register_blueprint(utility_bp,     url_prefix='/talk')
    app.register_blueprint(translation_bp, url_prefix='/talk')
    
    return app