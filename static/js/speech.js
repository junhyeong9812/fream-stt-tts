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
  const endpoint = `/stt-chat-extended/${language}`;

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
  const endpoint = `/tts/${language}`;

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
