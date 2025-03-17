// 텍스트 대화 기능 구현
function startTextChat() {
  const text = document.getElementById("chat-input").value;
  if (!text) {
    alert("대화할 내용을 입력해주세요.");
    return;
  }

  const language = document.getElementById("chat-language").value;
  const endpoint = `/chat-extended/${language}`;

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
      const audioPlayer = document.getElementById("chat-audio");
      audioPlayer.src = audioUrl;
      audioPlayer.style.display = "block";
    })
    .catch((error) => {
      alert(`오류: ${error.message}`);
    });
}
