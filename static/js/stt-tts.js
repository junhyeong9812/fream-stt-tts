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
  const endpoint = `/stt/${language}`;

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
      const audioPlayer = document.getElementById("tts-audio");
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = "block";
    })
    .catch((error) => {
      alert(`오류: ${error.message}`);
    });
}
