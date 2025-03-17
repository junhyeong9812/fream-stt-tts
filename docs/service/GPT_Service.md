# GPT 서비스 문서

## 개요

GPT 서비스는 OpenAI의 GPT API를 활용하여 다양한 자연어 처리 기능을 제공합니다. 채팅 응답 생성, 어휘 학습 콘텐츠 생성, 번역 등 다양한 기능을 통합된 인터페이스로 제공합니다.

## 주요 기능

1. **기본 대화 응답 생성**

   - 사용자 메시지에 대한 자연스러운 응답 생성
   - 응답에서 핵심 단어 추출 및 학습 자료 제공

2. **확장 응답 생성**

   - 대화 응답에 어휘 학습 자료 추가
   - 사용자의 후속 응답 예시 제안

3. **대화 기록 지원**

   - 이전 대화 맥락을 고려한 응답 생성
   - 일관된 대화 흐름 유지

4. **번역 서비스**
   - 한국어 ↔ 영어, 한국어 ↔ 일본어, 영어 ↔ 일본어 번역
   - 정확하고 자연스러운 번역 결과 제공

## 클래스 구조

`GPTService` 클래스는 다음과 같은 주요 메서드를 제공합니다:

### 1. `__init__(self)`

GPT 서비스를 초기화합니다.

- OpenAI API 키 로드
- HTTP 클라이언트 설정
- 기본 모델 설정

### 2. `get_chat_response(self, user_message, language="en")`

기본 채팅 응답을 생성합니다.

- 사용자 메시지와 언어에 따른 응답 생성
- 응답 텍스트와 메타데이터 반환

### 3. `format_learning_response(self, response_text, language="en")`

GPT 응답에서 대화 부분과 어휘 학습 부분을 분리합니다.

- 영어와 일본어에 대한 응답 형식 처리
- 분리된 응답 데이터 반환

### 4. `get_chat_response_extended(self, user_message, language="en")`

확장된 채팅 응답을 생성합니다.

- 대화 응답, 어휘 학습, 예시 응답을 포함한 확장 콘텐츠 생성
- 언어별 특화된 프롬프트 활용

### 5. `format_extended_response(self, response_text, language="en")`

확장된 GPT 응답에서 각 부분을 분리합니다.

- 대화 부분, 어휘 학습 부분, 예시 응답 부분 추출
- 영어와 일본어에 대한 형식 처리

### 6. `get_chat_conversation(self, user_message, chat_history=None, language="en")`

대화 기록을 고려한 응답을 생성합니다.

- 이전 대화 메시지를 포함한 컨텍스트 구성
- 맥락을 유지한 자연스러운 대화 처리

### 7. `get_translation(self, text, source_language, target_language)`

텍스트 번역 기능을 제공합니다.

- 소스 언어에서 대상 언어로 텍스트 번역
- 번역 전용 프롬프트를 통한 정확한 번역 결과 생성

## 시스템 메시지 설계

GPT 서비스는 각 기능과 언어에 맞는 최적화된 시스템 메시지를 사용합니다:

### 영어 대화 응답 시스템 메시지

```
You are a helpful English conversation partner.
After responding to the user's message, identify 3 key words or phrases from your response.
For each word, provide the Korean meaning and 2 example sentences using that word.
...
```

### 영어 확장 응답 시스템 메시지

```
You are a helpful English conversation partner.
After responding to the user's message, do the following:
1. Identify 3 key words or phrases from YOUR response and provide the Korean meaning and 2 example sentences for each.
2. Provide 3 example responses that the USER could give to continue the conversation with you.
...
```

### 번역 시스템 메시지

```
You are a professional translator specialized in [SourceLanguage] to [TargetLanguage] translation.
Translate the text provided by the user accurately and naturally, preserving the original meaning, tone, and style.
Respond with only the translated text, without any additional explanations, notes, or quotation marks.
```

## 사용 예시

### 기본 대화 응답 얻기

```python
from app.services.gpt_service import GPTService

gpt_service = GPTService()
response = gpt_service.get_chat_response("Hello, how are you today?", language="en")
print(response["answer"])
```

### 번역 수행하기

```python
from app.services.gpt_service import GPTService

gpt_service = GPTService()
result = gpt_service.get_translation("안녕하세요, 오늘 날씨가 좋네요.", "ko", "en")
print(result["translated_text"])
```

### 대화 기록 활용하기

```python
from app.services.gpt_service import GPTService

chat_history = [
    {"role": "user", "content": "What's the weather like today?"},
    {"role": "assistant", "content": "I don't have real-time data, but I can talk about weather in general."}
]

gpt_service = GPTService()
response = gpt_service.get_chat_conversation("Should I bring an umbrella?", chat_history, language="en")
print(response["answer"])
```

## 오류 처리

GPT 서비스는 다음과 같은 오류 처리 전략을 구현합니다:

1. **API 키 유효성 검사**: 초기화 시 API 키가 설정되었는지 확인
2. **네트워크 오류 처리**: API 호출 시 발생할 수 있는 다양한 네트워크 오류 처리
3. **로깅**: 각 프로세스의 상태와 오류를 상세히 로깅하여 디버깅 용이성 확보
4. **예외 전파**: 적절한 컨텍스트를 포함한 예외를 상위 계층으로 전파

## 최적화 및 성능 고려사항

### 토큰 관리

- 대화 기록에는 최대 10개의 이전 메시지만 포함하여 토큰 한도 관리
- 번역 시 정확성을 위해 낮은 temperature 값(0.3) 사용
- 응답 생성 시 적절한 max_tokens 설정으로 균형 유지

### 프롬프트 엔지니어링

- 각 기능에 최적화된 시스템 메시지 구성
- 언어별 특성에 맞는 프롬프트 디자인
- 명확한 출력 형식 지정으로 응답 파싱 용이성 확보

## 참고 자료

- [OpenAI Python 클라이언트 문서](docs/GPT_README.md)
- [OpenAI API 공식 문서](https://platform.openai.com/docs/introduction)
