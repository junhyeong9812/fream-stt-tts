# 음성 변환 서비스

## 프로젝트 개요
이 프로젝트는 음성 인식(STT, Speech-to-Text)과 음성 합성(TTS, Text-to-Speech) 기능을 제공하는 웹 서비스입니다. 영어와 일본어 두 언어를 지원하며, Flask를 기반으로 RESTful API를 통해 서비스를 제공합니다.

## 주요 기능
1. **음성 인식(STT)**
   - 영어 음성 파일을 텍스트로 변환
   - 일본어 음성 파일을 텍스트로 변환

2. **음성 합성(TTS)**
   - 영어 텍스트를 음성으로 변환
   - 일본어 텍스트를 음성으로 변환

## 사용된 주요 기술 및 라이브러리

### 1. 프레임워크
- **Flask**: 웹 서버 구현을 위한 Python 마이크로 프레임워크

### 2. 음성 인식(STT)
- **Whisper**: OpenAI에서 개발한 강력한 음성 인식 모델
  - 다양한 언어와 악센트를 지원하며 높은 정확도를 제공
  - 프로젝트에서는 'medium' 크기의 모델을 사용

### 3. 음성 합성(TTS)
- **TTS (Text-to-Speech)**: Coqui TTS 라이브러리
  - 영어 모델: `tts_models/en/ljspeech/tacotron2-DDC`
  - 일본어 모델: `tts_models/ja/kokoro/tacotron2-DDC`
  - Tacotron2 아키텍처를 사용한 고품질 음성 합성 제공

### 4. 기타 라이브러리
- **PyTorch**: 딥러닝 모델 운영을 위한 프레임워크
- **soundfile**: 오디오 파일 처리
- **pydub**: 오디오 데이터 조작
- **tempfile**: 임시 파일 관리

## 프로젝트 구조
- 모델 파일 저장 디렉토리: `models/`
- 임시 파일 저장 디렉토리: `temp/`
- 웹 인터페이스: `templates/index.html`

## API 엔드포인트

### 음성 인식(STT) API
1. **영어 음성 인식**
   - URL: `/stt/english`
   - 메서드: POST
   - 입력: 오디오 파일 (WAV 형식)
   - 출력: 인식된 텍스트와 언어 정보 (JSON)

2. **일본어 음성 인식**
   - URL: `/stt/japanese`
   - 메서드: POST
   - 입력: 오디오 파일 (WAV 형식)
   - 출력: 인식된 텍스트와 언어 정보 (JSON)

### 음성 합성(TTS) API
1. **영어 음성 합성**
   - URL: `/tts/english`
   - 메서드: POST
   - 입력: 텍스트 (JSON)
   - 출력: 음성 파일 (WAV 형식)

2. **일본어 음성 합성**
   - URL: `/tts/japanese`
   - 메서드: POST
   - 입력: 텍스트 (JSON)
   - 출력: 음성 파일 (WAV 형식)

### 시스템 관리 API
1. **파일 정리**
   - URL: `/cleanup`
   - 메서드: POST
   - 기능: 특정 임시 파일 삭제

2. **주기적 임시 파일 정리**
   - URL: `/cleanup/temp`
   - 메서드: POST
   - 기능: 1시간 이상 지난 모든 임시 파일 삭제

## 주요 구현 특징
1. **지연 로딩(Lazy Loading)**: 필요할 때만 모델을 메모리에 로드하여 리소스 효율성 향상
2. **임시 파일 관리**: 자동 정리 시스템을 통한 디스크 공간 관리
3. **오류 처리**: 모든 API 엔드포인트에 예외 처리 구현
4. **PyTorch 커스텀 로더**: 모델 로딩 시 호환성 문제 해결을 위한 커스텀 설정

## 설치 및 실행 방법

### 필수 요구사항
- Python 3.7 이상
- PyTorch
- Flask
- Whisper
- TTS (Coqui TTS)
- soundfile
- pydub
- FFmpeg (오디오 처리를 위해 필수)

### 설치 방법
```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# FFmpeg 설치
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg
# macOS
brew install ffmpeg
# Windows: https://ffmpeg.org/download.html 에서 다운로드 후 PATH에 추가

# 필요 라이브러리 설치
pip install flask
pip install openai-whisper
pip install torch
pip install TTS
pip install soundfile
pip install pydub
```

### 실행 방법
```bash
python app.py
```
서버는 기본적으로 http://localhost:5000 에서 실행됩니다.

## 사용 예시

### 음성 인식 (curl 사용)
```bash
# 영어 음성 인식
curl -X POST -F "file=@sample.wav" http://localhost:5000/stt/english

# 일본어 음성 인식
curl -X POST -F "file=@sample.wav" http://localhost:5000/stt/japanese
```

### 음성 합성 (curl 사용)
```bash
# 영어 음성 합성
curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello, world!"}' -o output.wav http://localhost:5000/tts/english

# 일본어 음성 합성
curl -X POST -H "Content-Type: application/json" -d '{"text":"こんにちは世界"}' -o output.wav http://localhost:5000/tts/japanese
```

## 주의사항
1. Whisper와 TTS 모델은 상당한 메모리를 사용합니다. 충분한 RAM이 필요합니다.
2. 초기 모델 로딩 시 시간이 소요될 수 있습니다.
3. 프로덕션 환경에서는 보안 설정과 에러 처리를 강화하는 것이 좋습니다.
4. pydub 라이브러리가 제대로 작동하려면 FFmpeg가 시스템에 올바르게 설치되어 있어야 합니다.
5. 오디오 파일 형식 변환 및 처리를 위해 FFmpeg는 필수적입니다.
