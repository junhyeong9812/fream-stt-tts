# 번역 서비스 문서

## 개요

번역 서비스는 한국어, 영어, 일본어 사이의 텍스트 번역 기능을 제공합니다. 이 서비스는 OpenAI의 GPT 모델을 활용하여 자연스럽고 정확한 번역 결과를 생성합니다.

## 기능

- **언어 간 번역**: 한국어 ↔ 영어, 한국어 ↔ 일본어, 영어 ↔ 일본어 번역 지원
- **정확한 번역**: GPT의 컨텍스트 이해 능력을 활용하여 정확하고 자연스러운 번역 제공
- **원본 텍스트 보존**: 원문의 의미, 어조, 스타일을 유지하는 번역
- **심플한 인터페이스**: 직관적인 API를 통한 쉬운 사용법

## 주요 컴포넌트

### 1. `translation_service.py`

이 파일은 번역 비즈니스 로직을 담당합니다:

```python
import logging
from app.services.gpt_service import GPTService

# 로거 설정
logger = logging.getLogger(__name__)

def translate_text(text, source_language, target_language):
    """
    텍스트를 소스 언어에서 대상 언어로 번역합니다.
    
    Args:
        text (str): 번역할 텍스트
        source_language (str): 소스 언어 코드 (ko, en, ja)
        target_language (str): 대상 언어 코드 (ko, en, ja)
        
    Returns:
        str: 번역된 텍스트
    """
    try:
        # GPT 서비스 초기화
        gpt_service = GPTService()
        
        # 번역 요청
        response = gpt_service.get_translation(text, source_language, target_language)
        
        # 번역 결과 반환
        return response["translated_text"]
        
    except Exception as e:
        logger.error(f"번역 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise
```

### 2. `translation_routes.py`

이 파일은 번역 API 엔드포인트를 정의합니다:

```python
from flask import Blueprint, request, jsonify, current_app
from app.services.translation_service import translate_text

# 블루프린트 생성
translation_bp = Blueprint('translation', __name__, url_prefix='/translation')

@translation_bp.route('/translate', methods=['POST'])
def translate():
    """
    텍스트 번역 API 엔드포인트
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': '번역할 텍스트가 없습니다'}), 400
    
    source_language = data.get('source_language', 'ko')
    target_language = data.get('target_language', 'en')
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': '유효한 텍스트가 아닙니다'}), 400
    
    try:
        # 텍스트 번역
        translated_text = translate_text(text, source_language, target_language)
        
        return jsonify({
            'source_language': source_language,
            'target_language': target_language,
            'original_text': text,
            'translated_text': translated_text
        })
    except Exception as e:
        current_app.logger.error(f"Translation Error: {str(e)}")
        return jsonify({'error': f'번역 실패: {str(e)}'}), 500
```

### 3. GPT 서비스의 번역 메서드

GPT 서비스 내 번역 기능을 담당하는 메서드입니다:

```python
def get_translation(self, text, source_language, target_language):
    """
    텍스트를 한 언어에서 다른 언어로 번역합니다.

    Args:
        text (str): 번역할 텍스트
        source_language (str): 소스 언어 코드 (ko, en, ja)
        target_language (str): 대상 언어 코드 (ko, en, ja)

    Returns:
        dict: 번역 결과
    """
    try:
        # 언어 코드를 언어 이름으로 변환
        language_names = {
            "ko": "Korean",
            "en": "English",
            "ja": "Japanese"
        }

        source_language_name = language_names.get(source_language, "Unknown")
        target_language_name = language_names.get(target_language, "Unknown")

        # 번역 전용 시스템 메시지 구성
        system_message = (
            f"You are a professional translator specialized in {source_language_name} to {target_language_name} translation. "
            "Translate the text provided by the user accurately and naturally, preserving the original meaning, tone, and style. "
            "Respond with only the translated text, without any additional explanations, notes, or quotation marks."
        )

        # GPT API 호출
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            temperature=0.3,  # 번역은 창의성보다 정확성이 중요하므로 낮은 온도값 사용
            max_tokens=1500
        )

        # 응답 추출 및 반환
        translated_text = response.choices[0].message.content
        usage = response.usage.total_tokens if hasattr(response, 'usage') else None

        return {
            "translated_text": translated_text.strip(),
            "model": self.model,
            "usage": {"total_tokens": usage} if usage else None
        }
    except Exception as e:
        logger.error(f"번역 API 호출 중 오류 발생: {str(e)}")
        raise e
```

## 번역 UI 구현

`translation.js` 파일은 번역 기능의 프론트엔드 인터페이스를 구현합니다:

```javascript
// 번역 기능 구현
document.addEventListener("DOMContentLoaded", function() {
  // 번역 버튼 클릭 이벤트
  document.getElementById("translate-button").addEventListener("click", translateText);
  
  // 초기 언어 옵션 설정
  updateTargetLanguageOptions();
});

// 번역 실행 함수
function translateText() {
  const sourceLanguage = document.getElementById("source-language").value;
  const targetLanguage = document.getElementById("target-language").value;
  const sourceText = document.getElementById("source-text").value.trim();
  
  if (!sourceText) {
    alert("번역할 텍스트를 입력해주세요.");
    return;
  }
  
  // 로딩 표시
  document.getElementById("loading-translation").style.display = "block";
  document.getElementById("target-text").value = "번역 중...";
  
  // 번역 API 호출
  fetch("/translation/translate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source_language: sourceLanguage,
      target_language: targetLanguage,
      text: sourceText
    })
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById("loading-translation").style.display = "none";
    
    if (data.error) {
      document.getElementById("target-text").value = `오류: ${data.error}`;
    } else {
      document.getElementById("target-text").value = data.translated_text;
    }
  })
  .catch(error => {
    document.getElementById("loading-translation").style.display = "none";
    document.getElementById("target-text").value = `오류: ${error.message}`;
  });
}
```

## 언어 선택 UI의 동적 업데이트

번역 UI는 소스 언어를 선택하면 자동으로 대상 언어 옵션을 업데이트합니다:

```javascript
// 원본 언어 변경 시 목표 언어 옵션 업데이트
function updateTargetLanguageOptions() {
  const sourceLanguage = document.getElementById("source-language").value;
  const targetLanguageSelect = document.getElementById("target-language");
  const currentTarget = targetLanguageSelect.value;
  
  // 현재 옵션들 제거
  while (targetLanguageSelect.options.length > 0) {
    targetLanguageSelect.remove(0);
  }
  
  // 한국어가 원본일 경우, 영어와 일본어만 목표 언어로 가능
  if (sourceLanguage === "ko") {
    addOption(targetLanguageSelect, "en", "영어");
    addOption(targetLanguageSelect, "ja", "일본어");
  } 
  // 영어가 원본일 경우, 한국어와 일본어만 목표 언어로 가능
  else if (sourceLanguage === "en") {
    addOption(targetLanguageSelect, "ko", "한국어");
    addOption(targetLanguageSelect, "ja", "일본어");
  } 
  // 일본어가 원본일 경우, 한국어와 영어만 목표 언어로 가능
  else if (sourceLanguage === "ja") {
    addOption(targetLanguageSelect, "ko", "한국어");
    addOption(targetLanguageSelect, "en", "영어");
  }
  
  // 이전 선택 값이 여전히 유효하면 그것을 선택
  for (let i = 0; i < targetLanguageSelect.options.length; i++) {
    if (targetLanguageSelect.options[i].value === currentTarget) {
      targetLanguageSelect.selectedIndex = i;
      return;
    }
  }
  
  // 아니면 첫 번째 옵션 선택
  targetLanguageSelect.selectedIndex = 0;
}
```

## 언어 스왑 기능

사용자가 소스 언어와 타겟 언어를 쉽게 바꿀 수 있는 기능을 제공합니다:

```javascript
// 언어 스왑 기능
function swapLanguages() {
  const sourceLanguageSelect = document.getElementById("source-language");
  const targetLanguageSelect = document.getElementById("target-language");
  const sourceText = document.getElementById("source-text");
  const targetText = document.getElementById("target-text");
  
  // 언어 선택 스왑
  const tempLang = sourceLanguageSelect.value;
  sourceLanguageSelect.value = targetLanguageSelect.value;
  targetLanguageSelect.value = tempLang;
  
  // 텍스트 내용 스왑
  const tempText = sourceText.value;
  sourceText.value = targetText.value;
  targetText.value = tempText;
  
  // 옵션 업데이트
  updateTargetLanguageOptions();
  updateSourceLanguageOptions();
}
```

## 번역 결과 복사 기능

사용자가 번역 결과를 쉽게 복사할 수 있도록 합니다:

```javascript
// 번역 결과 복사 기능
function copyTranslation() {
  const targetText = document.getElementById("target-text");
  
  if (!targetText.value) {
    alert("복사할 번역 결과가 없습니다.");
    return;
  }
  
  targetText.select();
  document.execCommand("copy");
  
  // 복사 완료 알림
  const copyButton = document.getElementById("copy-result");
  const originalText = copyButton.textContent;
  copyButton.textContent = "복사됨!";
  
  setTimeout(() => {
    copyButton.textContent = originalText;
  }, 2000);
}
```

## HTML 템플릿 구현

번역 기능에 대한 HTML 템플릿은 다음과 같습니다:

```html
<div id="translation" class="tab-content">
  <div class="container">
    <div class="section">
      <h2>언어 번역</h2>
      <div class="translation-container">
        <div class="translation-row">
          <div class="translation-column">
            <label for="source-language">원본 언어:</label>
            <select id="source-language" onchange="updateTargetLanguageOptions()">
              <option value="ko">한국어</option>
              <option value="en">영어</option>
              <option value="ja">일본어</option>
            </select>
            <textarea id="source-text" placeholder="번역할 텍스트를 입력하세요..." rows="6"></textarea>
          </div>
          
          <div class="translation-arrows">
            <button id="swap-languages" onclick="swapLanguages()">
              &#8644;
            </button>
          </div>
          
          <div class="translation-column">
            <label for="target-language">목표 언어:</label>
            <select id="target-language" onchange="updateSourceLanguageOptions()">
              <option value="en">영어</option>
              <option value="ja">일본어</option>
              <option value="ko">한국어</option>
            </select>
            <textarea id="target-text" placeholder="번역 결과가 여기에 표시됩니다..." rows="6" readonly></textarea>
          </div>
        </div>
        
        <div class="translation-controls">
          <button id="translate-button">번역하기</button>
          <button id="copy-result" onclick="copyTranslation()">결과 복사</button>
          <div id="loading-translation" class="loading"></div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## API 요청 및 응답 형식

### 요청 (POST /translation/translate)

```json
{
  "source_language": "ko",
  "target_language": "en",
  "text": "안녕하세요, 오늘 날씨가 좋네요."
}
```

### 응답

```json
{
  "source_language": "ko",
  "target_language": "en",
  "original_text": "안녕하세요, 오늘 날씨가 좋네요.",
  "translated_text": "Hello, the weather is nice today."
}
```

## 오류 처리

번역 서비스는 다음과 같은 오류 상황을 처리합니다:

1. **텍스트 누락**: 번역할 텍스트가 제공되지 않은 경우
2. **빈 텍스트**: 텍스트가 비어있거나 공백만 있는 경우
3. **API 오류**: GPT API 호출 중 발생하는 오류
4. **네트워크 오류**: 네트워크 연결 실패 등의 오류

## 주의사항 및 성능 고려사항

1. **토큰 한도**: 번역할 텍스트가 너무 길면 토큰 한도를 초과할 수 있습니다.
2. **비용 효율성**: API 호출당 비용이 발생하므로 큰 텍스트의 경우 분할 처리 고려
3. **응답 시간**: 번역은 API 호출을 통해 이루어지므로 네트워크 지연이 발생할 수 있습니다.
4. **정확성 최적화**: 번역의 정확성을 높이기 위해 temperature 값을 낮게 설정(0.3)

## 향후 개선 사항

1. **캐싱 시스템**: 자주 번역되는 텍스트의 결과를 캐싱하여 API 호출 비용 절감
2. **배치 처리**: 대량 번역 요청을 효율적으로 처리하는 배치 API 추가
3. **번역 메모리**: 이전 번역 내용을 활용한 일관성 있는 번역 결과 제공
4. **언어 자동 감지**: 입력 텍스트의 언어를 자동으로 감지하는 기능 추가

## 사용 예시

### 프로그래밍 방식 사용

```python
import requests

response = requests.post(
    "http://localhost:5000/translation/translate",
    json={
        "source_language": "ko",
        "target_language": "en",
        "text": "프로그래밍은 재미있습니다."
    }
)

result = response.json()
print(result["translated_text"])  # Output: Programming is fun.
```

### curl 사용 예시

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"source_language": "ko", "target_language": "en", "text": "안녕하세요, 세계!"}' \
  http://localhost:5000/translation/translate
```