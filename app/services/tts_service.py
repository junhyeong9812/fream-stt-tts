from TTS.api import TTS
import logging
import os
from flask import current_app
import tempfile

# 로거 설정
logger = logging.getLogger(__name__)

# 전역 변수로 모델 캐싱
_tts_en_model = None
_tts_ja_model = None

def get_tts_en_model():
    """
    영어 TTS 모델을 로드하고 반환합니다.
    모델은 한 번만 로드되고 캐싱됩니다.
    """
    global _tts_en_model
    if _tts_en_model is None:
        logger.info("Loading English TTS model...")
        _tts_en_model = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        logger.info("English TTS model loaded.")
    return _tts_en_model

def get_tts_ja_model():
    """
    일본어 TTS 모델을 로드하고 반환합니다.
    모델은 한 번만 로드되고 캐싱됩니다.
    """
    global _tts_ja_model
    if _tts_ja_model is None:
        logger.info("Loading Japanese TTS model...")
        _tts_ja_model = TTS("tts_models/ja/kokoro/tacotron2-DDC")
        logger.info("Japanese TTS model loaded.")
    return _tts_ja_model

def text_to_speech(text, language="en", output_path=None):
    """
    텍스트를 음성으로 변환합니다.
    
    Args:
        text (str): 변환할 텍스트
        language (str): 언어 코드 (en: 영어, ja: 일본어)
        output_path (str, optional): 출력 파일 경로. 없으면 임시 파일 생성
        
    Returns:
        str: 생성된 오디오 파일의 경로
    """
    try:
        # 언어별 필요한 처리
        if language == "en":
            # 짧은 텍스트인 경우 문장 종결 표시 추가
            if len(text.split()) < 5 and not text.strip().endswith(('.', '!', '?')):
                text = text + "."
            model = get_tts_en_model()
        elif language == "ja":
            # 짧은 텍스트인 경우 문장 종결 표시 추가
            if len(text.split()) < 5 and not text.strip().endswith(('.', '!', '?', '。', '！', '？')):
                text = text + "。"
            model = get_tts_ja_model()
        else:
            # 기본은 영어로
            model = get_tts_en_model()
            
        # 출력 경로가 지정되지 않은 경우 임시 파일 생성
        temp_file = None
        if not output_path:
            temp_dir = current_app.config['TEMP_DIR']
            temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
            output_path = temp_file.name
            temp_file.close()
        
        # TTS 실행
        model.tts_to_file(text=text, file_path=output_path)
        
        return output_path
        
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        import traceback
        logger.error(traceback.format_exc())
        raise