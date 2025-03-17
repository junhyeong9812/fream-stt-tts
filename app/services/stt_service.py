import whisper
import logging
import os
import torch
import torch.serialization
from TTS.utils.radam import RAdam
from collections import defaultdict, OrderedDict
import builtins
from flask import current_app

# 로거 설정
logger = logging.getLogger(__name__)

# torch.load 함수를 오버라이드하여 항상 weights_only=False로 설정
original_load = torch.load
def custom_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_load(*args, **kwargs)

# torch.load 함수 오버라이드
torch.load = custom_load

# 안전한 클래스 목록에 필요한 클래스들 추가
torch.serialization.add_safe_globals([RAdam, defaultdict, OrderedDict, dict, builtins.dict])

# 전역 변수로 모델 캐싱
_whisper_model = None

def get_whisper_model():
    """
    Whisper 음성 인식 모델을 로드하고 반환합니다.
    모델은 한 번만 로드되고 캐싱됩니다.
    """
    global _whisper_model
    if _whisper_model is None:
        logger.info("Loading Whisper model...")
        _whisper_model = whisper.load_model("medium")
        logger.info("Whisper model loaded.")
    return _whisper_model

def transcribe_audio(audio_file_path, language=None):
    """
    오디오 파일을 텍스트로 변환합니다.
    
    Args:
        audio_file_path (str): 오디오 파일 경로
        language (str, optional): 언어 코드. 예: "en", "ja"
        
    Returns:
        dict: 변환 결과
    """
    try:
        model = get_whisper_model()
        
        # 언어가 지정된 경우 해당 언어로 인식, 아니면 자동 감지
        if language:
            result = model.transcribe(audio_file_path, language=language)
        else:
            result = model.transcribe(audio_file_path)
            
        return {
            'text': result["text"],
            'language': language or result.get("language", "unknown")
        }
    except Exception as e:
        logger.error(f"STT Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise