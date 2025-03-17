// 번역 기능 구현
document.addEventListener("DOMContentLoaded", function () {
  // 번역 버튼 클릭 이벤트
  document
    .getElementById("translate-button")
    .addEventListener("click", translateText);

  // 초기 언어 옵션 설정
  updateTargetLanguageOptions();
});

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

// 목표 언어 변경 시 원본 언어 옵션 업데이트
function updateSourceLanguageOptions() {
  const targetLanguage = document.getElementById("target-language").value;
  const sourceLanguageSelect = document.getElementById("source-language");
  const currentSource = sourceLanguageSelect.value;

  // 현재 옵션들 제거
  while (sourceLanguageSelect.options.length > 0) {
    sourceLanguageSelect.remove(0);
  }

  // 한국어가 목표일 경우, 영어와 일본어만 원본 언어로 가능
  if (targetLanguage === "ko") {
    addOption(sourceLanguageSelect, "en", "영어");
    addOption(sourceLanguageSelect, "ja", "일본어");
  }
  // 영어가 목표일 경우, 한국어와 일본어만 원본 언어로 가능
  else if (targetLanguage === "en") {
    addOption(sourceLanguageSelect, "ko", "한국어");
    addOption(sourceLanguageSelect, "ja", "일본어");
  }
  // 일본어가 목표일 경우, 한국어와 영어만 원본 언어로 가능
  else if (targetLanguage === "ja") {
    addOption(sourceLanguageSelect, "ko", "한국어");
    addOption(sourceLanguageSelect, "en", "영어");
  }

  // 이전 선택 값이 여전히 유효하면 그것을 선택
  for (let i = 0; i < sourceLanguageSelect.options.length; i++) {
    if (sourceLanguageSelect.options[i].value === currentSource) {
      sourceLanguageSelect.selectedIndex = i;
      return;
    }
  }

  // 아니면 첫 번째 옵션 선택
  sourceLanguageSelect.selectedIndex = 0;
}

// 셀렉트 박스에 옵션 추가 헬퍼 함수
function addOption(selectElement, value, text) {
  const option = document.createElement("option");
  option.value = value;
  option.text = text;
  selectElement.add(option);
}

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
      text: sourceText,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("loading-translation").style.display = "none";

      if (data.error) {
        document.getElementById("target-text").value = `오류: ${data.error}`;
      } else {
        document.getElementById("target-text").value = data.translated_text;
      }
    })
    .catch((error) => {
      document.getElementById("loading-translation").style.display = "none";
      document.getElementById("target-text").value = `오류: ${error.message}`;
    });
}

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
