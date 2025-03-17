# 번역 API 문서

## 개요

번역 API는 한국어, 영어, 일본어 간의 텍스트 번역을 제공하는 RESTful API 엔드포인트입니다. OpenAI의 GPT 모델을 활용하여 정확하고 자연스러운 번역을 생성합니다.

## 엔드포인트

### 텍스트 번역

- **URL**: `/translation/translate`
- **메서드**: `POST`
- **Content-Type**: `application/json`

## 지원되는 언어 쌍

- 한국어 ↔ 영어
- 한국어 ↔ 일본어
- 영어 ↔ 일본어

## 요청 파라미터

- `source_language`: 원본 언어 코드 (필수)
  - 가능한 값: `ko` (한국어), `en` (영어), `ja` (일본어)
- `target_language`: 목표 언어 코드 (필수)
  - 가능한 값: `ko` (한국어), `en` (영어), `ja` (일본어)
- `text`: 번역할 텍스트 (필수)

## 요청 예시

### cURL 요청

```bash
# 한국어 → 영어 번역
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "source_language": "ko",
    "target_language": "en",
    "text": "안녕하세요, 오늘 날씨가 좋네요."
  }' \
  http://localhost:5000/translation/translate

# 영어 → 일본어 번역
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "source_language": "en",
    "target_language": "ja",
    "text": "Hello, how are you today?"
  }' \
  http://localhost:5000/translation/translate
```

### Python 요청

```python
import requests

# 번역 요청
url = "http://localhost:5000/translation/translate"
data = {
    "source_language": "ko",
    "target_language": "en",
    "text": "프로그래밍은 정말 재미있습니다."
}
response = requests.post(url, json=data)
result = response.json()
print(result['translated_text'])
```

## 응답 형식

### 성공 응답

```json
{
  "source_language": "원본 언어 코드",
  "target_language": "목표 언어 코드",
  "original_text": "원본 텍스트",
  "translated_text": "번역된 텍스트"
}
```

## 오류 응답

```json
{
  "error": "오류 메시지"
}
```

## 가능한 오류 상황

1. **텍스트 누락**: 번역할 텍스트가 제공되지 않은 경우
2. **언어 코드 오류**: 지원되지 않는 언어 코드 사용
3. **빈 텍스트**: 공백이거나 내용이 없는 텍스트
4. **API 처리 오류**: GPT 모델 호출 중 발생하는 기타 오류

## 성능 고려사항

- 텍스트 길이에 따라 번역 시간이 증가할 수 있습니다.
- 토큰 사용량에 따라 추가 비용이 발생할 수 있습니다.
- 복잡한 문장이나 전문 용어의 경우 번역 정확도가 달라질 수 있습니다.

## 번역 특징

- 원문의 의미, 어조, 스타일 보존에 중점
- 낮은 temperature(0.3) 설정으로 창의성보다 정확성 중시
- 최대 1,500 토큰 길이의 텍스트 처리 가능

## 보안 및 제한사항

- API 호출 시 인증이 필요할 수 있습니다.
- 과도한 API 호출에 대한 요율 제한(Rate Limiting)이 적용될 수 있습니다.
- 번역 내용의 개인정보 보호 및 보안 고려

## 향후 개선 예정 기능

- 번역 메모리 시스템 구축
- 전문 분야별 특화 번역 모델 개발
- 언어 자동 감지 기능 추가
- 대량 텍스트 번역을 위한 배치 처리 API 개발
- 더 많은 언어 지원 확대

## 사용 시 팁

1. 간결하고 명확한 문장 사용
2. 전문 용어는 가능한 원문 그대로 유지
3. 긴 텍스트는 여러 부분으로 나누어 번역 고려
4. 번역 결과는 항상 최종 검토 권장
