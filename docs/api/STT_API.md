# STT(음성 인식) API 문서

## 개요

STT(Speech-to-Text) API는 음성 파일을 텍스트로 변환하는 RESTful API 엔드포인트를 제공합니다. 현재 영어와 일본어 음성 인식을 지원합니다.

## 엔드포인트

### 1. 영어 음성 인식

- **URL**: `/stt/english`
- **메서드**: `POST`
- **Content-Type**: `multipart/form-data`

### 2. 일본어 음성 인식

- **URL**: `/stt/japanese`
- **메서드**: `POST`
- **Content-Type**: `multipart/form-data`

## 요청 파라미터

### 필수 파라미터

- `file`: 음성 파일 (지원 형식: WAV, MP3)

## 요청 예시

### cURL 요청

```bash
# 영어 음성 인식
curl -X POST -F "file=@english_audio.wav" http://localhost:5000/stt/english

# 일본어 음성 인식
curl -X POST -F "file=@japanese_audio.wav" http://localhost:5000/stt/japanese
```

### Python 요청

```python
import requests

# 영어 음성 인식
url = "http://localhost:5000/stt/english"
files = {"file": open("english_audio.wav", "rb")}
response = requests.post(url, files=files)
result = response.json()
print(result['text'])  # 인식된 텍스트 출력

# 일본어 음성 인식
url = "http://localhost:5000/stt/japanese"
files = {"file": open("japanese_audio.wav", "rb")}
response = requests.post(url, files=files)
result = response.json()
print(result['text'])  # 인식된 텍스트 출력
```

## 응답 형식

### 성공 응답

```json
{
  "text": "인식된 음성 텍스트",
  "language": "en" // 또는 "ja"
}
```

### 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## 가능한 오류 상황

1. **파일 누락**: 요청에 음성 파일이 포함되지 않은 경우
2. **파일 형식 오류**: 지원되지 않는 파일 형식
3. **음성 인식 처리 오류**: 모델 처리 중 발생하는 기타 오류

## 성능 고려사항

- 음성 품질이 좋을수록 인식 정확도가 높아집니다.
- 배경 소음이 적은 환경에서 최상의 결과를 얻을 수 있습니다.
- 첫 요청 시 모델 로딩으로 인해 약간의 지연이 발생할 수 있습니다.

## 추가 통합 API

### STT와 대화 통합 API

- **URL**: `/stt-chat-conversation/english`
- **URL**: `/stt-chat-conversation/japanese`
- 음성 인식 결과를 즉시 대화 API와 연결합니다.

## 보안 및 제한사항

- API 호출 시 인증이 필요할 수 있습니다.
- 단일 요청의 음성 파일 크기에 제한이 있을 수 있습니다.
- 과도한 API 호출에 대한 요율 제한(Rate Limiting)이 적용될 수 있습니다.

## 향후 개선 예정 기능

- 추가 언어 지원
- 실시간 음성 인식 기능
- 화자 식별 기능
- 도메인별 특화 모델 개발
