from flask import Flask, request, jsonify, send_file, render_template
import whisper
import torch
import torch.serialization
from TTS.utils.radam import RAdam
from TTS.api import TTS
from collections import defaultdict, OrderedDict
from waitress import serve
import builtins

# torch.load 함수를 오버라이드하여 항상 weights_only=False로 설정
original_load = torch.load
def custom_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_load(*args, **kwargs)

torch.load = custom_load

# 안전한 클래스 목록에 필요한 클래스들 추가
torch.serialization.add_safe_globals([RAdam, defaultdict, OrderedDict, dict, builtins.dict])

import os
import tempfile
import soundfile as sf
from pydub import AudioSegment
import logging
import time
import json
from dotenv import load_dotenv
from gpt_service import GPTService

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# 모델 로드 경로 설정
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# 임시 파일 저장 경로 설정
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# GPT 서비스 초기화
gpt_service = None

def get_gpt_service():
    global gpt_service
    if gpt_service is None:
        app.logger.info("GPT 서비스 초기화 중...")
        gpt_service = GPTService()
        app.logger.info("GPT 서비스 초기화 완료.")
    return gpt_service

# 모델 로딩 함수들 - 필요할 때만 로드하도록 지연 로딩 구현
whisper_model = None
tts_en_model = None
tts_ja_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        app.logger.info("Loading Whisper model...")
        whisper_model = whisper.load_model("medium")
        app.logger.info("Whisper model loaded.")
    return whisper_model

def get_tts_en_model():
    global tts_en_model
    if tts_en_model is None:
        app.logger.info("Loading English TTS model...")
        tts_en_model = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        app.logger.info("English TTS model loaded.")
    return tts_en_model

def get_tts_ja_model():
    global tts_ja_model
    if tts_ja_model is None:
        app.logger.info("Loading Japanese TTS model...")
        tts_ja_model = TTS("tts_models/ja/kokoro/tacotron2-DDC")
        app.logger.info("Japanese TTS model loaded.")
    return tts_ja_model

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stt/english', methods=['POST'])
def stt_english():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # Whisper로 영어 음성 인식
        model = get_whisper_model()
        result = model.transcribe(temp_file.name, language="en")
        text = result["text"]
        
        return jsonify({
            'text': text, 
            'language': 'en'
        })
    except Exception as e:
        app.logger.error(f"STT Error: {str(e)}")
        return jsonify({'error': f'음성 인식 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

@app.route('/stt/japanese', methods=['POST'])
def stt_japanese():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # Whisper로 일본어 음성 인식
        model = get_whisper_model()
        result = model.transcribe(temp_file.name, language="ja")
        text = result["text"]
        
        return jsonify({
            'text': text, 
            'language': 'ja'
        })
    except Exception as e:
        app.logger.error(f"STT Error: {str(e)}")
        return jsonify({'error': f'음성 인식 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

@app.route('/tts/english', methods=['POST'])
def tts_english():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    # 텍스트가 None이거나 빈 문자열인 경우 확인
    if not text:
        return jsonify({'error': '유효한 텍스트가 아닙니다'}), 400
    
    # 짧은 텍스트인 경우 문장 종결 표시 추가
    if len(text.split()) < 5 and not text.strip().endswith(('.', '!', '?')):
        text = text + "."
    
    try:
        temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
        temp_file.close()
        
        # 영어 TTS 모델 사용 - 심플하게 호출
        model = get_tts_en_model()
        model.tts_to_file(text=text, file_path=temp_file.name)
        
        response = send_file(temp_file.name, as_attachment=True, download_name='output_en.wav')
        
        # 응답 후크 추가
        @response.call_on_close
        def on_response_sent():
            # 응답이 완전히 전송된 후 파일 삭제
            if os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                    app.logger.info(f"임시 파일 삭제 성공: {temp_file.name}")
                except Exception as e:
                    app.logger.error(f"임시 파일 삭제 실패: {str(e)}")
        
        return response
    except Exception as e:
        app.logger.error(f"TTS Error: {str(e)}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return jsonify({'error': f'음성 변환 실패: {str(e)}'}), 500

@app.route('/tts/japanese', methods=['POST'])
def tts_japanese():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': '텍스트가 없습니다'}), 400
    
    text = data['text']
    
    # 텍스트가 None이거나 빈 문자열인 경우 확인
    if not text:
        return jsonify({'error': '유효한 텍스트가 아닙니다'}), 400
    
    # 짧은 텍스트인 경우 문장 종결 표시 추가
    if len(text.split()) < 5 and not text.strip().endswith(('.', '!', '?', '。', '！', '？')):
        text = text + "。"
    
    try:
        temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
        temp_file.close()
        
        # 일본어 TTS 모델 사용 - 심플하게 호출
        model = get_tts_ja_model()
        model.tts_to_file(text=text, file_path=temp_file.name)
        
        response = send_file(temp_file.name, as_attachment=True, download_name='output_ja.wav')
        
        # 응답 후크 추가
        @response.call_on_close
        def on_response_sent():
            # 응답이 완전히 전송된 후 파일 삭제
            if os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                    app.logger.info(f"임시 파일 삭제 성공: {temp_file.name}")
                except Exception as e:
                    app.logger.error(f"임시 파일 삭제 실패: {str(e)}")
        
        return response
    except Exception as e:
        app.logger.error(f"TTS Error: {str(e)}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return jsonify({'error': f'음성 변환 실패: {str(e)}'}), 500

# 새로운 GPT 대화 API 추가 (영어 대화)
@app.route('/chat/english', methods=['POST'])
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
        app.logger.error(f"Chat Error: {str(e)}")
        return jsonify({'error': f'대화 처리 실패: {str(e)}'}), 500

# 새로운 GPT 대화 API 추가 (일본어 대화)
@app.route('/chat/japanese', methods=['POST'])
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
        app.logger.error(f"Chat Error: {str(e)}")
        return jsonify({'error': f'대화 처리 실패: {str(e)}'}), 500

# STT 결과를 GPT 대화에 바로 연결하는 통합 API (영어)
@app.route('/stt-chat/english', methods=['POST'])
def stt_chat_english():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. Whisper로 영어 음성 인식
        whisper_model = get_whisper_model()
        result = whisper_model.transcribe(temp_file.name, language="en")
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
        app.logger.error(f"STT-Chat Error: {str(e)}")
        return jsonify({'error': f'음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# STT 결과를 GPT 대화에 바로 연결하는 통합 API (일본어)
@app.route('/stt-chat/japanese', methods=['POST'])
def stt_chat_japanese():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. Whisper로 일본어 음성 인식
        whisper_model = get_whisper_model()
        result = whisper_model.transcribe(temp_file.name, language="ja")
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
        app.logger.error(f"STT-Chat Error: {str(e)}")
        return jsonify({'error': f'음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# GPT 응답을 TTS로 변환하는 통합 API (영어)
@app.route('/chat-tts/english', methods=['POST'])
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
        
        temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
        temp_file.close()
        
        # 영어 TTS 모델 사용 - 심플하게 호출
        tts_model = get_tts_en_model()
        tts_model.tts_to_file(text=conversation_text, file_path=temp_file.name)
        
        # 응답 데이터 준비
        response_data = {
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"],
            'audio_file': temp_file.name  # 클라이언트에서 이 파일을 요청할 수 있도록
        }
        
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f"Chat-TTS Error: {str(e)}")
        return jsonify({'error': f'대화-음성 변환 실패: {str(e)}'}), 500

# GPT 응답을 TTS로 변환하는 통합 API (일본어)
@app.route('/chat-tts/japanese', methods=['POST'])
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
        
        temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
        temp_file.close()
        
        # 일본어 TTS 모델 사용 - 심플하게 호출
        tts_model = get_tts_ja_model()
        tts_model.tts_to_file(text=conversation_text, file_path=temp_file.name)
        
        # 응답 데이터 준비
        response_data = {
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"],
            'audio_file': temp_file.name  # 클라이언트에서 이 파일을 요청할 수 있도록
        }
        
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f"Chat-TTS Error: {str(e)}")
        return jsonify({'error': f'대화-음성 변환 실패: {str(e)}'}), 500

# 생성된 오디오 파일 제공 API
@app.route('/audio/<path:filename>', methods=['GET'])
def get_audio(filename):
    full_path = os.path.join(TEMP_DIR, os.path.basename(filename))
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        return jsonify({'error': '파일을 찾을 수 없습니다'}), 404

# 임시 파일 정리를 위한 경로
@app.route('/cleanup', methods=['POST'])
def cleanup():
    filename = request.json.get('filename')
    if filename and os.path.exists(filename):
        try:
            os.unlink(filename)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'success': False})

# 주기적으로 오래된 임시 파일 정리 (1시간 이상 지난 파일)
@app.route('/cleanup/temp', methods=['POST'])
def cleanup_temp():
    now = time.time()
    count = 0
    
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path):
            # 파일의 수정 시간이 1시간 이상 지났는지 확인
            if now - os.path.getmtime(file_path) > 3600:  # 3600초 = 1시간
                try:
                    os.unlink(file_path)
                    count += 1
                except Exception as e:
                    app.logger.error(f"임시 파일 정리 실패: {str(e)}")
    
    return jsonify({'success': True, 'deleted_files': count})

# 확장된 GPT 대화 API (영어 - 예시 응답 포함)
@app.route('/chat-extended/english', methods=['POST'])
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
        app.logger.error(f"확장 Chat Error: {str(e)}")
        return jsonify({'error': f'확장 대화 처리 실패: {str(e)}'}), 500

# 확장된 GPT 대화 API (일본어 - 예시 응답 포함)
@app.route('/chat-extended/japanese', methods=['POST'])
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
        app.logger.error(f"확장 Chat Error: {str(e)}")
        return jsonify({'error': f'확장 대화 처리 실패: {str(e)}'}), 500

# 확장된 STT+GPT 통합 API (영어 - 예시 응답 포함)
@app.route('/stt-chat-extended/english', methods=['POST'])
def stt_chat_extended_english():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. Whisper로 영어 음성 인식
        whisper_model = get_whisper_model()
        result = whisper_model.transcribe(temp_file.name, language="en")
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
        app.logger.error(f"확장 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'확장 음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# 확장된 STT+GPT 통합 API (일본어 - 예시 응답 포함)
@app.route('/stt-chat-extended/japanese', methods=['POST'])
def stt_chat_extended_japanese():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    audio_file = request.files['file']
    
    # 임시 파일로 저장
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. Whisper로 일본어 음성 인식
        whisper_model = get_whisper_model()
        result = whisper_model.transcribe(temp_file.name, language="ja")
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
        app.logger.error(f"확장 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'확장 음성 대화 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# 대화 기록이 포함된 텍스트 채팅 API (영어)
@app.route('/chat-conversation/english', methods=['POST'])
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
        app.logger.error(f"대화 기록 Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 처리 실패: {str(e)}'}), 500

# 대화 기록이 포함된 텍스트 채팅 API (일본어)
@app.route('/chat-conversation/japanese', methods=['POST'])
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
        app.logger.error(f"대화 기록 Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 처리 실패: {str(e)}'}), 500

# 대화 기록이 포함된 음성 채팅 API (영어)
@app.route('/stt-chat-conversation/english', methods=['POST'])
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
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. Whisper로 영어 음성 인식
        whisper_model = get_whisper_model()
        result = whisper_model.transcribe(temp_file.name, language="en")
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
        app.logger.error(f"대화 기록 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 음성 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제

# 대화 기록이 포함된 음성 채팅 API (일본어)
@app.route('/stt-chat-conversation/japanese', methods=['POST'])
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
    temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # 1. Whisper로 일본어 음성 인식
        whisper_model = get_whisper_model()
        result = whisper_model.transcribe(temp_file.name, language="ja")
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
        app.logger.error(f"대화 기록 STT-Chat Error: {str(e)}")
        return jsonify({'error': f'대화 기록 음성 처리 실패: {str(e)}'}), 500
    finally:
        os.unlink(temp_file.name)  # 임시 파일 삭제


# 플라스크 활용 시 활성화
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

# Gunicorn 활용 시 (Unix/Linux환경)
# gunicorn -w 4 --threads 8 -b 0.0.0.0:5000 app:app
# 위 명령어로 실행 

# Waitress 활용(window) ==>멀티스레드 환경 제공
if __name__ == '__main__':
    print("Starting Waitress server...")
    serve(app, host="0.0.0.0", port=5000, threads=8)
