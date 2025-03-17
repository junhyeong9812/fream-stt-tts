import logging
from app.services.gpt_service import GPTService

# 로거 설정
logger = logging.getLogger(__name__)

def translate_text(text, source_language, target_language):
    """
    텍스트를 소스 언어에서 대상 언어로 번역합니다.
    
    Args:
        text (str): 번역할 텍스트
        source_language (str): 소스 언어 코드 (ko, en, ja)
        target_language (str): 대상 언어 코드 (ko, en, ja)
        
    Returns:
        str: 번역된 텍스트
    """
    try:
        # GPT 서비스 초기화
        gpt_service = GPTService()
        
        # 번역 요청
        response = gpt_service.get_translation(text, source_language, target_language)
        
        # 번역 결과 반환
        return response["translated_text"]
        
    except Exception as e:
        logger.error(f"번역 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise