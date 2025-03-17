# 음성 합성(TTS) 서비스 문서

## 개요

음성 합성(Text-to-Speech, TTS) 서비스는 텍스트를 자연스러운 음성으로 변환하는 기능을 제공합니다. 이 서비스는 Coqui TTS 라이브러리를 활용하여 영어와 일본어 텍스트를 고품질 음성으로 합성합니다.

## 기능

- **텍스트를 음성으로 변환**: 텍스트 입력을 자연스러운 음성 파일로 변환
- **다국어 지원**: 영어 및 일본어 음성 합성 제공
- **고품질 음성**: Tacotron2 아키텍처 기반의 음성 모델을 통한 자연스러운 발화
- **지연 로딩**: 필요한 경우에만 모델을 로드하여 리소스 효율성 향상
- **자동 문장 종결**: 짧은 텍스트 입력 시 자동으로 문장 종결 처리

## 주요 컴포넌트

### 1. `tts_service.py`

이 파일은 텍스트 음성 변환의 핵심 기능을 구현합니다:

```python
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
```

### 2. `tts_routes.py`

이 파일은 음성 합성 API 엔드포인트를 정의합니다:

```python
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
```

## JavaScript 인터페이스

웹 인터페이스에서 음성 합성 기능을 사용하기 위한 JavaScript 코드:

```javascript
// 텍스트 변환 (TTS)
function convertToSpeech() {
  const text = document.getElementById("tts-text").value;
  if (!text) {
    alert("텍스트를 입력해주세요.");
    return;
  }

  const language = document.getElementById("tts-language").value;
  const endpoint = `/tts/${language}`;

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("음성 변환에 실패했습니다.");
      }
      return response.blob();
    })
    .then((blob) => {
      const audioUrl = URL.createObjectURL(blob);
      const audioPlayer = document.getElementById("tts-audio");
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = "block";
    })
    .catch((error) => {
      alert(`오류: ${error.message}`);
    });
}
```

## 대화 응답 TTS 변환

대화 응답을 음성으로 변환하는 기능도 제공합니다:

```javascript
// 대화 응답 TTS 변환
function playChatResponse() {
  const text = document.getElementById("chat-response").innerText.trim();

  if (!text || text.includes("오류:")) {
    alert("변환할 대화 응답이 없습니다.");
    return;
  }

  const language = document.getElementById("chat-language").value;
  const endpoint = `/tts/${language}`;

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("음성 변환에 실패했습니다.");
      }
      return response.blob();
    })
    .then((blob) => {
      const audioUrl = URL.createObjectURL(blob);
      const audioPlayer = document.getElementById("chat-audio");
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = "block";
    })
    .catch((error) => {
      alert(`오류: ${error.message}`);
    });
}
```

## 통합 채팅을 위한 음성 합성 기능

통합 채팅 인터페이스에서 최근 응답을 음성으로 변환하는 기능을 제공합니다:

```javascript
// 통합 채팅 응답 TTS 변환
function playIntegratedResponse() {
  // 마지막 AI 응답 메시지 찾기
  const messages = document
    .getElementById("integrated-chat-messages")
    .querySelectorAll(".message-assistant");
  if (messages.length === 0) {
    alert("재생할 응답이 없습니다.");
    return;
  }

  const lastMessage = messages[messages.length - 1];
  const text = lastMessage.querySelector(".message-content").innerText.trim();

  if (!text) {
    alert("변환할 대화 응답이 없습니다.");
    return;
  }

  const language = document.getElementById("integrated-chat-language").value;
  const endpoint = `/tts/${language}`;

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("음성 변환에 실패했습니다.");
      }
      return response.blob();
    })
    .then((blob) => {
      const audioUrl = URL.createObjectURL(blob);
      const audioPlayer = document.getElementById("integrated-audio");
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = "block";
      audioPlayer.play(); // 자동 재생
    })
    .catch((error) => {
      alert(`오류: ${error.message}`);
    });
}
```

## HTML 템플릿

음성 합성을 위한 HTML 인터페이스:

```html
<div class="section">
  <h2>텍스트 → 음성 (TTS)</h2>
  <select id="tts-language">
    <option value="english">영어</option>
    <option value="japanese">일본어</option>
  </select>
  <div>
    <textarea
      id="tts-text"
      placeholder="변환할 텍스트를 입력하세요..."
    ></textarea>
    <button id="convert-button">음성 변환</button>
  </div>
  <div>
    <h3>변환 결과:</h3>
    <audio id="tts-audio" controls class="audio-player"></audio>
  </div>
</div>
```

## TTS와 대화 API 통합

TTS와 대화 API를 통합한 엔드포인트도 제공합니다:

```python
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

        temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
        temp_file.close()

        # 영어 TTS 모델 사용
        tts_model = get_tts_en_model()
        tts_model.tts_to_file(text=conversation_text, file_path=temp_file.name)

        # 응답 데이터 준비
        response_data = {
            'conversation': formatted_response["conversation"],
            'vocabulary': formatted_response["vocabulary"],
            'full_response': response["answer"],
            'model': response["model"],
            'usage': response["usage"],
            'audio_file': temp_file.name
        }

        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"Chat-TTS Error: {str(e)}")
        return jsonify({'error': f'대화-음성 변환 실패: {str(e)}'}), 500
```

## API 요청 및 응답 형식

### 요청 (POST /tts/english 또는 /tts/japanese)

```json
{
  "text": "변환할 텍스트"
}
```

### 응답

응답은 생성된 오디오 파일(WAV 형식)이 직접 반환됩니다. 파일 다운로드 형식으로 응답이 제공됩니다.

## 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## 사용된 TTS 모델

이 서비스는 Coqui TTS 라이브러리의 모델을 사용합니다:

1. **영어 TTS 모델**:

   - 모델 경로: `tts_models/en/ljspeech/tacotron2-DDC`
   - 특징: LJSpeech 데이터셋으로 학습된 Tacotron2 아키텍처
   - 음성 특성: 여성 화자의 자연스러운 영어 발화

2. **일본어 TTS 모델**:
   - 모델 경로: `tts_models/ja/kokoro/tacotron2-DDC`
   - 특징: 일본어 데이터셋으로 학습된 Tacotron2 아키텍처
   - 음성 특성: 자연스러운 일본어 발화

## 텍스트 전처리

더 나은 음성 품질을 위해 다음과 같은 텍스트 전처리를 수행합니다:

1. **자동 문장 종결 추가**:

   - 짧은 문장(5단어 미만)에 대해 자동으로 문장 종결 부호 추가
   - 영어: 마침표(.), 느낌표(!), 물음표(?) 없는 경우 마침표 추가
   - 일본어: 마침표(。), 느낌표(!), 물음표(?) 없는 경우 일본어 마침표(。) 추가

2. **텍스트 유효성 검사**:
   - 빈 텍스트 또는 공백만 있는 텍스트에 대한 처리

## 임시 파일 관리

TTS 서비스는 생성된 오디오 파일을 임시 디렉토리에 저장하고 관리합니다:

1. **임시 파일 생성**: 오디오 생성 시 고유한 임시 파일 생성
2. **파일 전송 후 삭제**: 클라이언트에 파일 전송 완료 후 자동 삭제
3. **오류 시 파일 정리**: 예외 발생 시 생성된 임시 파일 삭제

## 성능 고려 사항

1. **초기 로딩 시간**: 첫 요청 시 모델 로딩에 시간이 소요됩니다.
2. **지연 로딩**: 모델은 필요할 때만 로드되어 메모리 효율성을 높입니다.
3. **변환 시간**: 텍스트 길이에 따라 합성 시간이 증가합니다.
4. **메모리 사용량**: TTS 모델은 상당한 메모리를 사용하므로 충분한 RAM 필요

## 오류 처리

서비스는 다음과 같은 오류 상황을 처리합니다:

1. **텍스트 누락**: 요청에 텍스트가 포함되지 않은 경우
2. **빈 텍스트**: 텍스트가 비어있거나 공백만 있는 경우
3. **처리 오류**: 음성 합성 중 발생하는 오류
4. **임시 파일 관리**: 요청 처리 후 임시 파일 자동 삭제

## 향후 개선 사항

1. **추가 언어 지원**: 한국어 등 더 많은 언어 옵션 제공
2. **음성 커스터마이징**: 다양한 음색, 속도, 피치 조절 기능 추가
3. **SSML 지원**: Speech Synthesis Markup Language를 통한 세밀한 발화 제어
4. **스트리밍 지원**: 대용량 텍스트의 점진적 합성 및 스트리밍 재생
5. **발화 속도 조절**: 사용자가 말하는 속도를 조절할 수 있는 기능

## 사용 예시

### curl을 사용한 영어 TTS 요청

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello, this is a test."}' --output speech.wav http://localhost:5000/tts/english
```

### curl을 사용한 일본어 TTS 요청

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"こんにちは、これはテストです。"}' --output speech.wav http://localhost:5000/tts/japanese
```

### Python 코드를 사용한 요청

```python
import requests
import io
import soundfile as sf
import sounddevice as sd
import numpy as np

url = "http://localhost:5000/tts/english"
data = {"text": "Hello, this is a test of the text to speech service."}

response = requests.post(url, json=data)

if response.status_code == 200:
    # 오디오 데이터 읽기
    audio_data, samplerate = sf.read(io.BytesIO(response.content))

    # 오디오 재생
    sd.play(audio_data, samplerate)
    sd.wait()
else:
    print(f"Error: {response.text}")
```
