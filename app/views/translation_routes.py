from flask import Blueprint, request, jsonify, current_app
from app.services.translation_service import translate_text

# 블루프린트 생성
translation_bp = Blueprint('translation', __name__, url_prefix='/translation')

@translation_bp.route('/translate', methods=['POST'])
def translate():
    """
    텍스트 번역 API 엔드포인트
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': '번역할 텍스트가 없습니다'}), 400
    
    source_language = data.get('source_language', 'ko')
    target_language = data.get('target_language', 'en')
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': '유효한 텍스트가 아닙니다'}), 400
    
    try:
        # 텍스트 번역
        translated_text = translate_text(text, source_language, target_language)
        
        return jsonify({
            'source_language': source_language,
            'target_language': target_language,
            'original_text': text,
            'translated_text': translated_text
        })
    except Exception as e:
        current_app.logger.error(f"Translation Error: {str(e)}")
        return jsonify({'error': f'번역 실패: {str(e)}'}), 500