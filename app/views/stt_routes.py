from flask import Blueprint, request, jsonify, current_app
import os
import tempfile
from app.services.stt_service import transcribe_audio

# 블루프린트 생성
stt_bp = Blueprint('stt', __name__, url_prefix='/stt')

@stt_bp.route('/english', methods=['POST'])
def stt_english():
    """
    영어 음성을 텍스트로 변환하는 API 엔드포인트
    """
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 영어 음성 인식
        result = transcribe_audio(temp_file.name, language="en")
        
        return jsonify({
            'text': result['text'], 
            'language': 'en'
        })
    except Exception as e:
        current_app.logger.error(f"STT Error: {str(e)}")
        return jsonify({'error': f'음성 인식 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

@stt_bp.route('/japanese', methods=['POST'])
def stt_japanese():
    """
    일본어 음성을 텍스트로 변환하는 API 엔드포인트
    """
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 일본어 음성 인식
        result = transcribe_audio(temp_file.name, language="ja")
        
        return jsonify({
            'text': result['text'], 
            'language': 'ja'
        })
    except Exception as e:
        current_app.logger.error(f"STT Error: {str(e)}")
        return jsonify({'error': f'음성 인식 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제