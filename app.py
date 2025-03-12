from flask import Flask, request, jsonify, send_file, render_template
import whisper
import torch
import torch.serialization
from TTS.utils.radam import RAdam
from TTS.api import TTS
from collections import defaultdict, OrderedDict
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

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# 모델 로드 경로 설정
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# 임시 파일 저장 경로 설정
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

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
    
    try:
        temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
        temp_file.close()
        
        # 영어 TTS 모델 사용
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
    
    try:
        temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False, suffix='.wav')
        temp_file.close()
        
        # 일본어 TTS 모델 사용
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)