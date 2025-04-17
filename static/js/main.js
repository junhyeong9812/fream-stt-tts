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

// STT & TTS 기능 변수
let mediaRecorder;
let audioChunks = [];

// 음성 대화 녹음 변수
let fullMediaRecorder;
let fullAudioChunks = [];

// 통합 채팅 변수
let chatHistory = [];
let integratedMediaRecorder;
let integratedAudioChunks = [];

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

// STT 기능 구현
async function startRecording() {
  audioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (e) => {
    audioChunks.push(e.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    sendAudioToServer(audioBlob);
  };

  mediaRecorder.start();
  document.getElementById("record-button").disabled = true;
  document.getElementById("stop-button").disabled = false;
}

function stopRecording() {
  mediaRecorder.stop();
  document.getElementById("record-button").disabled = false;
  document.getElementById("stop-button").disabled = true;
}

function uploadAudioFile() {
  const fileInput = document.getElementById("audio-file");
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    sendAudioToServer(file);
  } else {
    alert("파일을 선택해주세요.");
  }
}

// 오디오 서버로 전송 (STT)
function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob);

  const language = document.getElementById("stt-language").value;
  const endpoint = `/talk/stt/${language}`;

  document.getElementById("stt-result").value = "처리 중...";

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("stt-result").value = `오류: ${data.error}`;
      } else {
        document.getElementById("stt-result").value = data.text;
      }
    })
    .catch((error) => {
      document.getElementById("stt-result").value = `오류: ${error}`;
    });
}

// 텍스트 변환 (TTS)
function convertToSpeech() {
  const text = document.getElementById("tts-text").value;
  if (!text) {
    alert("텍스트를 입력해주세요.");
    return;
  }

  const language = document.getElementById("tts-language").value;
  const endpoint = `/talk/tts/${language}`;

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

// 텍스트 대화 기능 구현
function startTextChat() {
  const text = document.getElementById("chat-input").value;
  if (!text) {
    alert("대화할 내용을 입력해주세요.");
    return;
  }

  const language = document.getElementById("chat-language").value;
  const endpoint = `/talk/chat-extended/${language}`;

  document.getElementById("loading-chat").style.display = "block";
  document.getElementById("chat-response").innerHTML = "";
  document.getElementById("vocabulary").innerHTML = "";
  document.getElementById("example-responses").innerHTML = "";

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("loading-chat").style.display = "none";

      if (data.error) {
        document.getElementById(
          "chat-response"
        ).innerHTML = `<p class="error">오류: ${data.error}</p>`;
      } else {
        // 대화 응답 표시
        document.getElementById(
          "chat-response"
        ).innerHTML = `<p>${data.conversation.replace(/\n/g, "<br>")}</p>`;

        // 어휘 학습 표시
        if (data.vocabulary) {
          document.getElementById(
            "vocabulary"
          ).innerHTML = `<p>${data.vocabulary.replace(/\n/g, "<br>")}</p>`;
        } else {
          document.getElementById("vocabulary").innerHTML =
            "<p>어휘 정보가 없습니다.</p>";
        }

        // 예시 응답 표시
        if (data.example_responses) {
          document.getElementById(
            "example-responses"
          ).innerHTML = `<p>${data.example_responses.replace(
            /\n/g,
            "<br>"
          )}</p>`;
        } else {
          document.getElementById("example-responses").innerHTML =
            "<p>예시 응답이 없습니다.</p>";
        }
      }
    })
    .catch((error) => {
      document.getElementById("loading-chat").style.display = "none";
      document.getElementById(
        "chat-response"
      ).innerHTML = `<p class="error">오류: ${error.message}</p>`;
    });
}

// 대화 응답 TTS 변환
function playChatResponse() {
  const text = document.getElementById("chat-response").innerText.trim();

  if (!text || text.includes("오류:")) {
    alert("변환할 대화 응답이 없습니다.");
    return;
  }

  const language = document.getElementById("chat-language").value;
  const endpoint = `/talk/tts/${language}`;

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

// 음성 대화 기능 (STT → GPT → TTS)
async function startFullRecording() {
  fullAudioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  fullMediaRecorder = new MediaRecorder(stream);

  fullMediaRecorder.ondataavailable = (e) => {
    fullAudioChunks.push(e.data);
  };

  fullMediaRecorder.onstop = () => {
    const audioBlob = new Blob(fullAudioChunks, { type: "audio/wav" });
    sendFullConversation(audioBlob);
  };

  fullMediaRecorder.start();
  document.getElementById("full-record-button").disabled = true;
  document.getElementById("full-stop-button").disabled = false;
}

function stopFullRecording() {
  fullMediaRecorder.stop();
  document.getElementById("full-record-button").disabled = false;
  document.getElementById("full-stop-button").disabled = true;
}

function uploadFullAudioFile() {
  const fileInput = document.getElementById("full-audio-file");
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    sendFullConversation(file);
  } else {
    alert("파일을 선택해주세요.");
  }
}

// 음성 대화 처리
function sendFullConversation(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob);

  const language = document.getElementById("full-language").value;
  const endpoint = `/talk/stt-chat-extended/${language}`;

  document.getElementById("loading-full").style.display = "block";
  document.getElementById("full-input-text").innerHTML = "";
  document.getElementById("full-response").innerHTML = "";
  document.getElementById("full-vocabulary").innerHTML = "";
  document.getElementById("full-example-responses").innerHTML = "";

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("loading-full").style.display = "none";

      if (data.error) {
        document.getElementById(
          "full-input-text"
        ).innerHTML = `<p class="error">오류: ${data.error}</p>`;
      } else {
        // 인식된 텍스트 표시
        document.getElementById(
          "full-input-text"
        ).innerHTML = `<p>${data.input_text}</p>`;

        // 대화 응답 표시
        document.getElementById(
          "full-response"
        ).innerHTML = `<p>${data.conversation.replace(/\n/g, "<br>")}</p>`;

        // 어휘 학습 표시
        if (data.vocabulary) {
          document.getElementById(
            "full-vocabulary"
          ).innerHTML = `<p>${data.vocabulary.replace(/\n/g, "<br>")}</p>`;
        } else {
          document.getElementById("full-vocabulary").innerHTML =
            "<p>어휘 정보가 없습니다.</p>";
        }

        // 예시 응답 표시
        if (data.example_responses) {
          document.getElementById(
            "full-example-responses"
          ).innerHTML = `<p>${data.example_responses.replace(
            /\n/g,
            "<br>"
          )}</p>`;
        } else {
          document.getElementById("full-example-responses").innerHTML =
            "<p>예시 응답이 없습니다.</p>";
        }

        // TTS 응답 듣기 버튼 활성화
        document.getElementById("full-tts-button").disabled = false;
      }
    })
    .catch((error) => {
      document.getElementById("loading-full").style.display = "none";
      document.getElementById(
        "full-input-text"
      ).innerHTML = `<p class="error">오류: ${error.message}</p>`;
    });
}

// 음성 대화 응답 TTS 변환
function playFullResponse() {
  const text = document.getElementById("full-response").innerText.trim();

  if (!text || text.includes("오류:")) {
    alert("변환할 대화 응답이 없습니다.");
    return;
  }

  const language = document.getElementById("full-language").value;
  const endpoint = `/talk/tts/${language}`;

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
      const audioPlayer = document.getElementById("full-audio");
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = "block";
    })
    .catch((error) => {
      alert(`오류: ${error.message}`);
    });
}

// 통합 채팅 기능 구현
function sendIntegratedChatMessage() {
  const input = document.getElementById("integrated-chat-input");
  const text = input.value.trim();

  if (!text) {
    alert("메시지를 입력해주세요.");
    return;
  }

  // 사용자 메시지를 채팅창에 추가
  addMessageToChat("user", text);

  // 입력창 비우기
  input.value = "";

  // 대화 요청 전송
  sendChatRequest(text);
}

// 엔터 키로 메시지 전송
function handleChatEnterKey(e) {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("integrated-chat-submit").click();
  }
}

// 통합 채팅 녹음 시작
async function startIntegratedRecording() {
  integratedAudioChunks = [];
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });
  integratedMediaRecorder = new MediaRecorder(stream);

  integratedMediaRecorder.ondataavailable = (e) => {
    integratedAudioChunks.push(e.data);
  };

  integratedMediaRecorder.onstop = () => {
    const audioBlob = new Blob(integratedAudioChunks, {
      type: "audio/wav",
    });
    sendVoiceChatRequest(audioBlob);
  };

  integratedMediaRecorder.start();
  document.getElementById("integrated-record-button").disabled = true;
  document.getElementById("integrated-stop-button").disabled = false;
  document.getElementById("recording-status").textContent = "녹음 중...";
}

// 통합 채팅 녹음 중지
function stopIntegratedRecording() {
  integratedMediaRecorder.stop();
  document.getElementById("integrated-record-button").disabled = false;
  document.getElementById("integrated-stop-button").disabled = true;
  document.getElementById("recording-status").textContent = "녹음 완료";
}

// 채팅창에 메시지 추가
function addMessageToChat(sender, text) {
  const chatMessages = document.getElementById("integrated-chat-messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message message-${
    sender === "user" ? "user" : "assistant"
  }`;

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";
  contentDiv.innerText = text;

  const metaDiv = document.createElement("div");
  metaDiv.className = "message-meta";

  // 현재 시간 포맷팅
  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, "0")}:${String(
    now.getMinutes()
  ).padStart(2, "0")}`;
  metaDiv.innerText = timeStr;

  messageDiv.appendChild(contentDiv);
  messageDiv.appendChild(metaDiv);

  chatMessages.appendChild(messageDiv);

  // 스크롤을 최하단으로 이동
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // 채팅 기록에 메시지 추가
  if (sender === "user") {
    chatHistory.push({
      role: "user",
      content: text,
    });
  } else {
    chatHistory.push({
      role: "assistant",
      content: text,
    });
  }
}

// 텍스트 대화 요청 전송
function sendChatRequest(text) {
  const language = document.getElementById("integrated-chat-language").value;
  const endpoint = `/talk/chat-conversation/${language}`;

  document.getElementById("integrated-loading").style.display = "block";

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: text,
      history: chatHistory,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("integrated-loading").style.display = "none";

      if (data.error) {
        alert(`오류: ${data.error}`);
      } else {
        // 대화 응답을 채팅창에 추가
        addMessageToChat("assistant", data.conversation);

        // 어휘 학습 표시
        if (data.vocabulary) {
          document.getElementById(
            "integrated-vocabulary"
          ).innerHTML = `<p>${data.vocabulary.replace(/\n/g, "<br>")}</p>`;
        } else {
          document.getElementById("integrated-vocabulary").innerHTML =
            "<p>어휘 정보가 없습니다.</p>";
        }

        // 예시 응답 표시
        if (data.example_responses) {
          document.getElementById(
            "integrated-examples"
          ).innerHTML = `<p>${data.example_responses.replace(
            /\n/g,
            "<br>"
          )}</p>`;
        } else {
          document.getElementById("integrated-examples").innerHTML =
            "<p>예시 응답이 없습니다.</p>";
        }

        // TTS 버튼 활성화
        document.getElementById("integrated-tts-button").disabled = false;
      }
    })
    .catch((error) => {
      document.getElementById("integrated-loading").style.display = "none";
      alert(`오류: ${error.message}`);
    });
}

// 음성 대화 요청 전송
function sendVoiceChatRequest(audioBlob) {
  const language = document.getElementById("integrated-chat-language").value;
  const endpoint = `/talk/stt-chat-conversation/${language}`;

  document.getElementById("integrated-loading").style.display = "block";

  const formData = new FormData();
  formData.append("file", audioBlob);
  formData.append("history", JSON.stringify(chatHistory));

  fetch(endpoint, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("integrated-loading").style.display = "none";

      if (data.error) {
        alert(`오류: ${data.error}`);
      } else {
        // 인식된 사용자 텍스트를 채팅창에 추가
        addMessageToChat("user", data.input_text);

        // 대화 응답을 채팅창에 추가
        addMessageToChat("assistant", data.conversation);

        // 어휘 학습 표시
        if (data.vocabulary) {
          document.getElementById(
            "integrated-vocabulary"
          ).innerHTML = `<p>${data.vocabulary.replace(/\n/g, "<br>")}</p>`;
        } else {
          document.getElementById("integrated-vocabulary").innerHTML =
            "<p>어휘 정보가 없습니다.</p>";
        }

        // 예시 응답 표시
        if (data.example_responses) {
          document.getElementById(
            "integrated-examples"
          ).innerHTML = `<p>${data.example_responses.replace(
            /\n/g,
            "<br>"
          )}</p>`;
        } else {
          document.getElementById("integrated-examples").innerHTML =
            "<p>예시 응답이 없습니다.</p>";
        }

        // TTS 버튼 활성화
        document.getElementById("integrated-tts-button").disabled = false;
      }
    })
    .catch((error) => {
      document.getElementById("integrated-loading").style.display = "none";
      alert(`오류: ${error.message}`);
    });
}

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
  const endpoint = `/talk/tts/${language}`;

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
