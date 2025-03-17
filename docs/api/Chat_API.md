# 대화 API 문서

## 개요

대화 API는 OpenAI의 GPT 모델을 활용하여 다양한 형태의 대화 기능을 제공합니다. 영어와 일본어로 대화 응답을 생성하며, 다양한 기능을 지원합니다.

## 엔드포인트

### 1. 기본 대화 응답 (영어)

- **URL**: `/chat/english`
- **메서드**: `POST`
- **Content-Type**: `application/json`

### 2. 기본 대화 응답 (일본어)

- **URL**: `/chat/japanese`
- **메서드**: `POST`
- **Content-Type**: `application/json`

### 3. 확장 대화 응답 (영어)

- **URL**: `/chat-extended/english`
- **메서드**: `POST`
- **Content-Type**: `application/json`

### 4. 확장 대화 응답 (일본어)

- **URL**: `/chat-extended/japanese`
- **메서드**: `POST`
- **Content-Type**: `application/json`

### 5. 대화 기록 포함 대화 (영어)

- **URL**: `/chat-conversation/english`
- **메서드**: `POST`
- **Content-Type**: `application/json`

### 6. 대화 기록 포함 대화 (일본어)

- **URL**: `/chat-conversation/japanese`
- **메서드**: `POST`
- **Content-Type**: `application/json`

## 요청 파라미터

### 기본 대화 및 확장 대화 요청

- `text`: 사용자의 메시지 (필수)

### 대화 기록 포함 대화 요청

- `text`: 사용자의 메시지 (필수)
- `history`: 이전 대화 기록 (선택적, JSON 배열)

## 요청 예시

### cURL 요청

```bash
# 기본 영어 대화
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, how are you?"}' \
  http://localhost:5000/chat/english

# 확장 일본어 대화
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"こんにちは、今日はどうですか？"}' \
  http://localhost:5000/chat-extended/japanese

# 대화 기록 포함 영어 대화
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Should I bring an umbrella?",
    "history":[
      {"role":"user", "content":"What\s the weather like today?"},
      {"role":"assistant", "content":"I don\t have real-time data, but I can talk about weather in general."}
    ]
  }' \
  http://localhost:5000/chat-conversation/english
```

### Python 요청

```python
import requests

# 기본 대화 응답
url = "http://localhost:5000/chat/english"
data = {"text": "Hello, how are you?"}
response = requests.post(url, json=data)
result = response.json()

# 대화 기록 포함 대화
url = "http://localhost:5000/chat-conversation/english"
data = {
    "text": "Should I bring an umbrella?",
    "history": [
        {"role": "user", "content": "What's the weather like today?"},
        {"role": "assistant", "content": "I don't have real-time data, but I can talk about weather in general."}
    ]
}
response = requests.post(url, json=data)
result = response.json()
```

## 응답 형식

### 기본 대화 응답

```json
{
  "conversation": "AI의 대화 응답",
  "vocabulary": "학습 단어 및 예문",
  "full_response": "전체 AI 응답",
  "model": "사용된 GPT 모델",
  "usage": {
    "total_tokens": "토큰 사용량"
  }
}
```

### 확장 대화 응답

```json
{
  "conversation": "AI의 대화 응답",
  "vocabulary": "학습 단어 및 예문",
  "example_responses": "사용자의 가능한 후속 응답",
  "full_response": "전체 AI 응답",
  "model": "사용된 GPT 모델",
  "usage": {
    "total_tokens": "토큰 사용량"
  }
}
```

### 대화 기록 포함 대화 응답

```json
{
  "conversation": "이전 대화 맥락을 고려한 AI 응답",
  "vocabulary": "학습 단어 및 예문",
  "example_responses": "사용자의 가능한 후속 응답",
  "full_response": "전체 AI 응답",
  "model": "사용된 GPT 모델",
  "usage": {
    "total_tokens": "토큰 사용량"
  }
}
```

## 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## 가능한 오류 상황

1. **텍스트 누락**: 사용자 메시지가 제공되지 않은 경우
2. **대화 기록 형식 오류**: 잘못된 형식의 대화 기록
3. **API 처리 오류**: GPT 모델 호출 중 발생하는 기타 오류

## 성능 고려사항

- 대화 기록은 최대 10개의 이전 메시지로 제한됩니다.
- 토큰 사용량에 따라 추가 비용이 발생할 수 있습니다.
- 응답 생성 시간은 메시지 복잡성에 따라 달라집니다.

## 추가 통합 API

### STT와 결합된 대화 API

- **URL**: `/stt-chat-conversation/english`
- **URL**: `/stt-chat-conversation/japanese`
- 음성 인식 결과를 직접 대화 API와 연결합니다.

### TTS와 결합된 대화 API

- **URL**: `/chat-tts/english`
- **URL**: `/chat-tts/japanese`
- 대화 응답을 즉시 음성으로 변환합니다.

## 보안 및 제한사항

- API 호출 시 인증이 필요할 수 있습니다.
- 과도한 API 호출에 대한 요율 제한(Rate Limiting)이 적용될 수 있습니다.
- 대화의 적절성과 안전성을 위한 콘텐츠 필터링 적용

## 프롬프트 엔지니어링 특징

- 언어별 특화된 시스템 메시지 사용
- 어휘 학습 및 예시 응답 생성
- 일관된 대화 맥락 유지를 위한 고급 프롬프트 설계

## 향후 개선 예정 기능

- 사용자 맞춤형 대화 스타일 학습
- 다양한 대화 토픽 및 스타일 지원
- 감정 및 톤 인식 개선
- 다국어 대화 지원 확대
