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
