// 공통 변수 및 함수들
let mediaRecorder;
let audioChunks = [];
let fullMediaRecorder;
let fullAudioChunks = [];
let integratedMediaRecorder;
let integratedAudioChunks = [];
let chatHistory = [];

// 탭 관리
function showTab(tabId) {
  // 모든 탭 콘텐츠를 숨김
  document.querySelectorAll(".tab-content").forEach((tab) => {
    tab.classList.remove("active");
  });

  // 모든 탭 버튼을 비활성화
  document.querySelectorAll(".tab").forEach((button) => {
    button.classList.remove("active");
  });

  // 선택된 탭 콘텐츠를 표시
  document.getElementById(tabId).classList.add("active");

  // 선택된 탭 버튼을 활성화
  Array.from(document.querySelectorAll(".tab"))
    .find((tab) => tab.textContent.includes(tabId))
    .classList.add("active");
}

// 토글 상세 정보 (어휘, 예시 등)
function toggleDetails(element) {
  element.classList.toggle("active");
}

// 입력 유형 전환 (텍스트 또는 음성)
function toggleInputType(type) {
  if (type === "text") {
    document.getElementById("text-input-toggle").classList.add("active");
    document.getElementById("voice-input-toggle").classList.remove("active");
    document.getElementById("text-input-area").style.display = "block";
    document.getElementById("voice-input-area").style.display = "none";
  } else {
    document.getElementById("text-input-toggle").classList.remove("active");
    document.getElementById("voice-input-toggle").classList.add("active");
    document.getElementById("text-input-area").style.display = "none";
    document.getElementById("voice-input-area").style.display = "block";
  }
}

// 페이지 로드 시 이벤트 리스너 설정
document.addEventListener("DOMContentLoaded", function () {
  // STT 녹음 시작
  document
    .getElementById("record-button")
    .addEventListener("click", startRecording);

  // STT 녹음 중지
  document
    .getElementById("stop-button")
    .addEventListener("click", stopRecording);

  // STT 파일 업로드
  document
    .getElementById("upload-button")
    .addEventListener("click", uploadAudioFile);

  // TTS 변환
  document
    .getElementById("convert-button")
    .addEventListener("click", convertToSpeech);

  // 텍스트 대화 시작
  document
    .getElementById("chat-button")
    .addEventListener("click", startTextChat);

  // 대화 응답 TTS 변환
  document
    .getElementById("chat-tts-button")
    .addEventListener("click", playChatResponse);

  // 음성 대화 녹음 시작
  document
    .getElementById("full-record-button")
    .addEventListener("click", startFullRecording);

  // 음성 대화 녹음 중지
  document
    .getElementById("full-stop-button")
    .addEventListener("click", stopFullRecording);

  // 음성 대화 파일 업로드
  document
    .getElementById("full-upload-button")
    .addEventListener("click", uploadFullAudioFile);

  // 음성 대화 응답 TTS 변환
  document
    .getElementById("full-tts-button")
    .addEventListener("click", playFullResponse);

  // 통합 채팅 텍스트 메시지 전송
  document
    .getElementById("integrated-chat-submit")
    .addEventListener("click", sendIntegratedChatMessage);

  // 통합 채팅 엔터 키로 메시지 전송
  document
    .getElementById("integrated-chat-input")
    .addEventListener("keypress", handleChatEnterKey);

  // 통합 채팅 녹음 시작
  document
    .getElementById("integrated-record-button")
    .addEventListener("click", startIntegratedRecording);

  // 통합 채팅 녹음 중지
  document
    .getElementById("integrated-stop-button")
    .addEventListener("click", stopIntegratedRecording);

  // 통합 채팅 응답 TTS 변환
  document
    .getElementById("integrated-tts-button")
    .addEventListener("click", playIntegratedResponse);
});
