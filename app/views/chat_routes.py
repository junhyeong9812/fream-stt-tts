from flask import Blueprint, request, jsonify, current_app
import os
import tempfile
import json
from app.services.stt_service import transcribe_audio
from app.services.tts_service import text_to_speech
from app.services.gpt_service import GPTService

# 블루프린트 생성
chat_bp = Blueprint('chat', __name__)

# GPT 서비스 인스턴스
_gpt_service = None

def get_gpt_service():
    """
    GPT 서비스 인스턴스를 반환합니다. 싱글톤 패턴 적용.
    """
    global _gpt_service
    if _gpt_service is None:
        current_app.logger.info("GPT 서비스 초기화 중...")
        _gpt_service = GPTService()
        current_app.logger.info("GPT 서비스 초기화 완료.")
    return _gpt_service

# 기본 채팅 엔드포인트 (영어)
@chat_bp.route('/chat/english', methods=['POST'])
def chat_english():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    try:
        # GPT 서비스를 통해 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response(text, language="en")
        
        # 응답 포맷팅 (대화 부분과 어휘 학습 부분 분리)
        formatted_response = gpt.format_learning_response(response["answer"], language="en")
        
        return jsonify({
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"Chat Error: {str(e)}")
        return jsonify({'error': f'대화 처리 실패: {str(e)}'}), 500

# 기본 채팅 엔드포인트 (일본어)
@chat_bp.route('/chat/japanese', methods=['POST'])
def chat_japanese():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    try:
        # GPT 서비스를 통해 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response(text, language="ja")
        
        # 응답 포맷팅 (대화 부분과 어휘 학습 부분 분리)
        formatted_response = gpt.format_learning_response(response["answer"], language="ja")
        
        return jsonify({
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"Chat Error: {str(e)}")
        return jsonify({'error': f'대화 처리 실패: {str(e)}'}), 500

# 확장된 GPT 대화 API (영어 - 예시 응답 포함)
@chat_bp.route('/chat-extended/english', methods=['POST'])
def chat_extended_english():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    try:
        # GPT 서비스를 통해 확장 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response_extended(text, language="en")
        
        # 응답 포맷팅 (대화 부분, 어휘 학습 부분, 예시 응답 부분 분리)
        formatted_response = gpt.format_extended_response(response["answer"], language="en")
        
        return jsonify({
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"확장 Chat Error: {str(e)}")
        return jsonify({'error': f'확장 대화 처리 실패: {str(e)}'}), 500

# 확장된 GPT 대화 API (일본어 - 예시 응답 포함)
@chat_bp.route('/chat-extended/japanese', methods=['POST'])
def chat_extended_japanese():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    try:
        # GPT 서비스를 통해 확장 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response_extended(text, language="ja")
        
        # 응답 포맷팅 (대화 부분, 어휘 학습 부분, 예시 응답 부분 분리)
        formatted_response = gpt.format_extended_response(response["answer"], language="ja")
        
        return jsonify({
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"확장 Chat Error: {str(e)}")
        return jsonify({'error': f'확장 대화 처리 실패: {str(e)}'}), 500

# STT 결과를 GPT 대화에 바로 연결하는 통합 API (영어)
@chat_bp.route('/stt-chat/english', methods=['POST'])
def stt_chat_english():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. 영어 음성 인식
        result = transcribe_audio(temp_file.name, language="en")
        recognized_text = result["text"]
        
        # 2. GPT 서비스를 통해 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response(recognized_text, language="en")
        
        # 3. 응답 포맷팅
        formatted_response = gpt.format_learning_response(response["answer"], language="en")
        
        return jsonify({
            'input_text': recognized_text,
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"STT-Chat Error: {str(e)}")
        return jsonify({'error': f'음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# STT 결과를 GPT 대화에 바로 연결하는 통합 API (일본어)
@chat_bp.route('/stt-chat/japanese', methods=['POST'])
def stt_chat_japanese():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. 일본어 음성 인식
        result = transcribe_audio(temp_file.name, language="ja")
        recognized_text = result["text"]
        
        # 2. GPT 서비스를 통해 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response(recognized_text, language="ja")
        
        # 3. 응답 포맷팅
        formatted_response = gpt.format_learning_response(response["answer"], language="ja")
        
        return jsonify({
            'input_text': recognized_text,
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"STT-Chat Error: {str(e)}")
        return jsonify({'error': f'음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# 확장된 STT+GPT 통합 API (영어 - 예시 응답 포함)
@chat_bp.route('/stt-chat-extended/english', methods=['POST'])
def stt_chat_extended_english():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. 영어 음성 인식
        result = transcribe_audio(temp_file.name, language="en")
        recognized_text = result["text"]
        
        # 2. GPT 서비스를 통해 확장 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response_extended(recognized_text, language="en")
        
        # 3. 응답 포맷팅
        formatted_response = gpt.format_extended_response(response["answer"], language="en")
        
        return jsonify({
            'input_text': recognized_text,
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"확장 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'확장 음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# 확장된 STT+GPT 통합 API (일본어 - 예시 응답 포함)
@chat_bp.route('/stt-chat-extended/japanese', methods=['POST'])
def stt_chat_extended_japanese():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. 일본어 음성 인식
        result = transcribe_audio(temp_file.name, language="ja")
        recognized_text = result["text"]
        
        # 2. GPT 서비스를 통해 확장 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response_extended(recognized_text, language="ja")
        
        # 3. 응답 포맷팅
        formatted_response = gpt.format_extended_response(response["answer"], language="ja")
        
        return jsonify({
            'input_text': recognized_text,
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"확장 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'확장 음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# GPT 응답을 TTS로 변환하는 통합 API (영어)
@chat_bp.route('/chat-tts/english', methods=['POST'])
def chat_tts_english():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    try:
        # 1. GPT 서비스를 통해 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response(text, language="en")
        
        # 2. 응답 포맷팅
        formatted_response = gpt.format_learning_response(response["answer"], language="en")
        
        # 3. 대화 부분만 TTS로 변환
        conversation_text = formatted_response["conversation"]
        
        # 음성 파일 생성
        audio_file = text_to_speech(conversation_text, language="en")
        
        # 응답 데이터 준비
        response_data = {
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"],
            'audio_file': audio_file  # 클라이언트에서 이 파일을 요청할 수 있도록
        }
        
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"Chat-TTS Error: {str(e)}")
        return jsonify({'error': f'대화-음성 변환 실패: {str(e)}'}), 500

# GPT 응답을 TTS로 변환하는 통합 API (일본어)
@chat_bp.route('/chat-tts/japanese', methods=['POST'])
def chat_tts_japanese():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    try:
        # 1. GPT 서비스를 통해 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_response(text, language="ja")
        
        # 2. 응답 포맷팅
        formatted_response = gpt.format_learning_response(response["answer"], language="ja")
        
        # 3. 대화 부분만 TTS로 변환
        conversation_text = formatted_response["conversation"]
        
        # 음성 파일 생성
        audio_file = text_to_speech(conversation_text, language="ja")
        
        # 응답 데이터 준비
        response_data = {
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"],
            'audio_file': audio_file  # 클라이언트에서 이 파일을 요청할 수 있도록
        }
        
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"Chat-TTS Error: {str(e)}")
        return jsonify({'error': f'대화-음성 변환 실패: {str(e)}'}), 500

# 대화 기록이 포함된 텍스트 채팅 API (영어)
@chat_bp.route('/chat-conversation/english', methods=['POST'])
def chat_conversation_english():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    chat_history = data.get('history', [])
    
    try:
        # GPT 서비스를 통해 대화 기록 포함 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_conversation(text, chat_history, language="en")
        
        # 응답 포맷팅
        formatted_response = gpt.format_extended_response(response["answer"], language="en")
        
        return jsonify({
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"대화 기록 Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 처리 실패: {str(e)}'}), 500

# 대화 기록이 포함된 텍스트 채팅 API (일본어)
@chat_bp.route('/chat-conversation/japanese', methods=['POST'])
def chat_conversation_japanese():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    chat_history = data.get('history', [])
    
    try:
        # GPT 서비스를 통해 대화 기록 포함 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_conversation(text, chat_history, language="ja")
        
        # 응답 포맷팅
        formatted_response = gpt.format_extended_response(response["answer"], language="ja")
        
        return jsonify({
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"대화 기록 Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 처리 실패: {str(e)}'}), 500

# 대화 기록이 포함된 음성 채팅 API (영어)
@chat_bp.route('/stt-chat-conversation/english', methods=['POST'])
def stt_chat_conversation_english():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 채팅 기록 가져오기
    chat_history_json = request.form.get('history', '[]')
    try:
        chat_history = json.loads(chat_history_json)
    except:
        chat_history = []
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. 영어 음성 인식
        result = transcribe_audio(temp_file.name, language="en")
        recognized_text = result["text"]
        
        # 2. GPT 서비스를 통해 대화 기록 포함 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_conversation(recognized_text, chat_history, language="en")
        
        # 3. 응답 포맷팅
        formatted_response = gpt.format_extended_response(response["answer"], language="en")
        
        return jsonify({
            'input_text': recognized_text,
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"대화 기록 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 음성 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# 대화 기록이 포함된 음성 채팅 API (일본어)
@chat_bp.route('/stt-chat-conversation/japanese', methods=['POST'])
def stt_chat_conversation_japanese():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 채팅 기록 가져오기
    chat_history_json = request.form.get('history', '[]')
    try:
        chat_history = json.loads(chat_history_json)
    except:
        chat_history = []
    
    # 임시 파일로 저장
    temp_dir = current_app.config['TEMP_DIR']
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. 일본어 음성 인식
        result = transcribe_audio(temp_file.name, language="ja")
        recognized_text = result["text"]
        
        # 2. GPT 서비스를 통해 대화 기록 포함 응답 얻기
        gpt = get_gpt_service()
        response = gpt.get_chat_conversation(recognized_text, chat_history, language="ja")
        
        # 3. 응답 포맷팅
        formatted_response = gpt.format_extended_response(response["answer"], language="ja")
        
        return jsonify({
            'input_text': recognized_text,
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'example_responses': formatted_response["example_responses"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"]
        })
    except Exception as e:
        current_app.logger.error(f"대화 기록 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 음성 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제