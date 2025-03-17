from flask import Blueprint, request, jsonify, send_file, current_app
import os
from app.services.tts_service import text_to_speech

# 블루프린트 생성
tts_bp = Blueprint('tts', __name__, url_prefix='/tts')

@tts_bp.route('/english', methods=['POST'])
def tts_english():
    """
    영어 텍스트를 음성으로 변환하는 API 엔드포인트
    """
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    # 텍스트가 None이거나 빈 문자열인 경우 확인
    if not text:
        return jsonify({'error': '유효한 텍스트가 아닙니다'}), 400
    
    try:
        # 텍스트를 음성으로 변환
        output_file = text_to_speech(text, language="en")
        
        # 파일 전송
        response = send_file(output_file, as_attachment=True, download_name='output_en.wav')
        
        # 응답 후크 추가
        @response.call_on_close
        def on_response_sent():
            # 응답이 완전히 전송된 후 파일 삭제
            if os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                    current_app.logger.info(f"임시 파일 삭제 성공: {output_file}")
                except Exception as e:
                    current_app.logger.error(f"임시 파일 삭제 실패: {str(e)}")
        
        return response
    except Exception as e:
        current_app.logger.error(f"TTS Error: {str(e)}")
        return jsonify({'error': f'음성 변환 실패: {str(e)}'}), 500

@tts_bp.route('/japanese', methods=['POST'])
def tts_japanese():
    """
    일본어 텍스트를 음성으로 변환하는 API 엔드포인트
    """
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    # 텍스트가 None이거나 빈 문자열인 경우 확인
    if not text:
        return jsonify({'error': '유효한 텍스트가 아닙니다'}), 400
    
    try:
        # 텍스트를 음성으로 변환
        output_file = text_to_speech(text, language="ja")
        
        # 파일 전송
        response = send_file(output_file, as_attachment=True, download_name='output_ja.wav')
        
        # 응답 후크 추가
        @response.call_on_close
        def on_response_sent():
            # 응답이 완전히 전송된 후 파일 삭제
            if os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                    current_app.logger.info(f"임시 파일 삭제 성공: {output_file}")
                except Exception as e:
                    current_app.logger.error(f"임시 파일 삭제 실패: {str(e)}")
        
        return response
    except Exception as e:
        current_app.logger.error(f"TTS Error: {str(e)}")
        return jsonify({'error': f'음성 변환 실패: {str(e)}'}), 500