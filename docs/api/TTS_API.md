# TTS(음성 합성) API 문서

## 개요

TTS(Text-to-Speech) API는 텍스트를 음성으로 변환하는 RESTful API 엔드포인트를 제공합니다. 현재 영어와 일본어 음성 합성을 지원합니다.

## 엔드포인트

### 1. 영어 텍스트 음성 변환

- **URL**: `/tts/english`
- **메서드**: `POST`
- **Content-Type**: `application/json`

### 2. 일본어 텍스트 음성 변환

- **URL**: `/tts/japanese`
- **메서드**: `POST`
- **Content-Type**: `application/json`

## 요청 파라미터

### 필수 파라미터

- `text`: 음성으로 변환할 텍스트 (문자열)

## 요청 예시

### cURL 요청

```bash
# 영어 텍스트 음성 변환
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, how are you today?"}' \
  http://localhost:5000/tts/english

# 일본어 텍스트 음성 변환
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"こんにちは、今日はいかがですか？"}' \
  http://localhost:5000/tts/japanese
```

### Python 요청

```python
import requests

# 영어 텍스트 음성 변환
url = "http://localhost:5000/tts/english"
data = {"text": "Hello, how are you today?"}
response = requests.post(url, json=data)
with open("output_en.wav", "wb") as f:
    f.write(response.content)

# 일본어 텍스트 음성 변환
url = "http://localhost:5000/tts/japanese"
data = {"text": "こんにちは、今日はいかがですか？"}
response = requests.post(url, json=data)
with open("output_ja.wav", "wb") as f:
    f.write(response.content)
```

## 응답 형식

### 성공 응답

- 응답은 WAV 형식의 오디오 파일로 직접 반환됩니다.
- HTTP 상태 코드 200과 함께 오디오 파일 다운로드

### 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## 가능한 오류 상황

1. **텍스트 누락**: 변환할 텍스트가 제공되지 않은 경우
2. **빈 텍스트**: 텍스트가 공백이거나 비어있는 경우
3. **텍스트 길이 제한**: 과도하게 긴 텍스트의 경우
4. **음성 합성 처리 오류**: 모델 처리 중 발생하는 기타 오류

## 성능 고려사항

- 텍스트 길이에 따라 음성 변환 시간이 증가할 수 있습니다.
- 초기 모델 로딩 시 약간의 지연이 발생할 수 있습니다.
- 정확하고 문법적으로 올바른 텍스트가 최상의 음성 품질을 보장합니다.

## 추가 통합 API

### TTS와 대화 통합 API

- **URL**: `/chat-tts/english`
- **URL**: `/chat-tts/japanese`
- 대화 응답을 즉시 음성으로 변환합니다.

## 보안 및 제한사항

- API 호출 시 인증이 필요할 수 있습니다.
- 단일 요청의 텍스트 길이에 제한이 있을 수 있습니다.
- 과도한 API 호출에 대한 요율 제한(Rate Limiting)이 적용될 수 있습니다.

## 텍스트 전처리 특징

- 짧은 텍스트(5단어 미만)의 경우 자동으로 문장 종결 부호 추가
- 영어: 마침표(.), 느낌표(!), 물음표(?) 없는 경우 마침표 추가
- 일본어: 마침표(。), 느낌표(!), 물음표(?) 없는 경우 일본어 마침표(。) 추가

## 향후 개선 예정 기능

- 추가 언어 지원
- 음성 커스터마이징 옵션 (속도, 피치 조절)
- SSML(Speech Synthesis Markup Language) 지원
- 대용량 텍스트의 스트리밍 음성 합성
