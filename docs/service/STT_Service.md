# 음성 인식(STT) 서비스 문서

## 개요

음성 인식(Speech-to-Text, STT) 서비스는 음성 파일을 텍스트로 변환하는 기능을 제공합니다. 이 서비스는 OpenAI의 Whisper 모델을 활용하여 영어와 일본어 음성을 높은 정확도로 인식합니다.

## 기능

- **음성 파일을 텍스트로 변환**: 다양한 형식의 음성 파일을 텍스트로 변환
- **다국어 지원**: 영어 및 일본어 음성 인식 제공
- **높은 정확도**: OpenAI Whisper 모델을 통한 고품질 인식 결과
- **지연 로딩**: 필요한 경우에만 모델을 로드하여 리소스 효율성 향상

## 주요 컴포넌트

### 1. `stt_service.py`

이 파일은 음성 인식의 핵심 기능을 구현합니다:

```python
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
```

### 2. `stt_routes.py`

이 파일은 음성 인식 API 엔드포인트를 정의합니다:

```python
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
```

## JavaScript 인터페이스

웹 인터페이스에서 음성 인식 기능을 사용하기 위한 JavaScript 코드:

```javascript
// STT 기능 구현
async function startRecording() {
  audioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (e) => {
    audioChunks.push(e.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    sendAudioToServer(audioBlob);
  };

  mediaRecorder.start();
  document.getElementById("record-button").disabled = true;
  document.getElementById("stop-button").disabled = false;
}

function stopRecording() {
  mediaRecorder.stop();
  document.getElementById("record-button").disabled = false;
  document.getElementById("stop-button").disabled = true;
}

function uploadAudioFile() {
  const fileInput = document.getElementById("audio-file");
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    sendAudioToServer(file);
  } else {
    alert("파일을 선택해주세요.");
  }
}

// 오디오 서버로 전송 (STT)
function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob);

  const language = document.getElementById("stt-language").value;
  const endpoint = `/stt/${language}`;

  document.getElementById("stt-result").value = "처리 중...";

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("stt-result").value = `오류: ${data.error}`;
      } else {
        document.getElementById("stt-result").value = data.text;
      }
    })
    .catch((error) => {
      document.getElementById("stt-result").value = `오류: ${error}`;
    });
}
```

## 통합 채팅을 위한 음성 인식 기능

통합 채팅 인터페이스에서 음성 입력을 활용하는 기능을 제공합니다:

```javascript
// 통합 채팅 녹음 시작
async function startIntegratedRecording() {
  integratedAudioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  integratedMediaRecorder = new MediaRecorder(stream);

  integratedMediaRecorder.ondataavailable = (e) => {
    integratedAudioChunks.push(e.data);
  };

  integratedMediaRecorder.onstop = () => {
    const audioBlob = new Blob(integratedAudioChunks, {
      type: "audio/wav",
    });
    sendVoiceChatRequest(audioBlob);
  };

  integratedMediaRecorder.start();
  document.getElementById("integrated-record-button").disabled = true;
  document.getElementById("integrated-stop-button").disabled = false;
  document.getElementById("recording-status").textContent = "녹음 중...";
}

// 음성 대화 요청 전송
function sendVoiceChatRequest(audioBlob) {
  const language = document.getElementById("integrated-chat-language").value;
  const endpoint = `/stt-chat-conversation/${language}`;

  document.getElementById("integrated-loading").style.display = "block";

  const formData = new FormData();
  formData.append("file", audioBlob);
  formData.append("history", JSON.stringify(chatHistory));

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("integrated-loading").style.display = "none";

      if (data.error) {
        alert(`오류: ${data.error}`);
      } else {
        // 인식된 사용자 텍스트를 채팅창에 추가
        addMessageToChat("user", data.input_text);

        // 대화 응답을 채팅창에 추가
        addMessageToChat("assistant", data.conversation);

        // 어휘 학습 표시
        if (data.vocabulary) {
          document.getElementById(
            "integrated-vocabulary"
          ).innerHTML = `<p>${data.vocabulary.replace(/\n/g, "<br>")}</p>`;
        } else {
          document.getElementById("integrated-vocabulary").innerHTML =
            "<p>어휘 정보가 없습니다.</p>";
        }

        // 예시 응답 표시
        if (data.example_responses) {
          document.getElementById(
            "integrated-examples"
          ).innerHTML = `<p>${data.example_responses.replace(
            /\n/g,
            "<br>"
          )}</p>`;
        } else {
          document.getElementById("integrated-examples").innerHTML =
            "<p>예시 응답이 없습니다.</p>";
        }

        // TTS 버튼 활성화
        document.getElementById("integrated-tts-button").disabled = false;
      }
    })
    .catch((error) => {
      document.getElementById("integrated-loading").style.display = "none";
      alert(`오류: ${error.message}`);
    });
}
```

## HTML 템플릿

음성 인식을 위한 HTML 인터페이스:

```html
<div class="section">
  <h2>음성 → 텍스트 (STT)</h2>
  <select id="stt-language">
    <option value="english">영어</option>
    <option value="japanese">일본어</option>
  </select>
  <div class="controls">
    <button id="record-button">녹음 시작</button>
    <button id="stop-button" disabled>녹음 중지</button>
  </div>
  <p>또는 파일 업로드:</p>
  <input type="file" id="audio-file" accept="audio/*" />
  <button id="upload-button">파일 업로드</button>
  <div>
    <h3>인식 결과:</h3>
    <textarea id="stt-result" readonly></textarea>
  </div>
</div>
```

## API 요청 및 응답 형식

### 요청 (POST /stt/english 또는 /stt/japanese)

요청은 `multipart/form-data` 형식으로 다음 필드를 포함합니다:

- `file`: 오디오 파일 (WAV, MP3 등 지원 형식)

### 응답

```json
{
  "text": "음성 인식 결과 텍스트",
  "language": "en" // 또는 "ja"
}
```

## 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## STT와 대화 API 통합

STT와 대화 API를 통합한 엔드포인트도 제공합니다:

```python
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
```

## Whisper 모델

이 서비스는 OpenAI의 Whisper 모델을 사용하여 음성 인식을 수행합니다:

- **사용 모델**: Whisper "medium" 크기 모델
- **특징**:
  - 다국어 음성 인식 지원
  - 높은 정확도
  - 다양한 악센트 및 배경 소음에 강인함
- **메모리 요구사항**: 모델 로드 시 약 2GB의 RAM 필요

## 성능 고려 사항

1. **초기 로딩 시간**: 첫 요청 시 모델 로딩에 시간이 소요됩니다.
2. **지연 로딩**: 모델은 필요할 때만 로드되어 메모리 효율성을 높입니다.
3. **변환 시간**: 오디오 길이에 따라 변환 시간이 증가합니다.
4. **메모리 사용량**: Whisper 모델은 상당한 메모리를 사용하므로 충분한 RAM 필요

## 오류 처리

서비스는 다음과 같은 오류 상황을 처리합니다:

1. **파일 없음**: 요청에 오디오 파일이 포함되지 않은 경우
2. **처리 오류**: 음성 인식 중 발생하는 오류
3. **파일 형식 오류**: 지원되지 않는 파일 형식
4. **임시 파일 관리**: 요청 처리 후 임시 파일 자동 삭제

## 향후 개선 사항

1. **추가 언어 지원**: 더 많은 언어 옵션 제공
2. **스트리밍 인식**: 실시간 음성 인식 기능 구현
3. **커스텀 모델**: 특정 도메인에 최적화된 모델 학습 및 적용
4. **성능 최적화**: 더 빠른 처리를 위한 최적화 기법 적용
5. **더 작은 모델 옵션**: 리소스 제약이 있는 환경을 위한 경량 모델 지원

## 사용 예시

### curl을 사용한 영어 음성 인식 요청

```bash
curl -X POST -F "file=@sample_english.wav" http://localhost:5000/stt/english
```

### curl을 사용한 일본어 음성 인식 요청

```bash
curl -X POST -F "file=@sample_japanese.wav" http://localhost:5000/stt/japanese
```

### Python 코드를 사용한 요청

```python
import requests

url = "http://localhost:5000/stt/english"
files = {"file": open("sample_audio.wav", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"인식된 텍스트: {result['text']}")
```
