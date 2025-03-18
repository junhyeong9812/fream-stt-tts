# 음성 변환 및 언어 학습 서비스

이 프로젝트는 음성 인식(STT), 음성 합성(TTS), 언어 학습, 그리고 번역 기능을 제공하는 종합 웹 서비스입니다. 영어, 일본어, 한국어를 지원하며, Flask를 기반으로 구조화된 아키텍처 패턴을 적용했습니다.

## 주요 기능

1. **음성 인식(STT)**

   - 영어 및 일본어 음성 파일을 텍스트로 변환

2. **음성 합성(TTS)**

   - 영어 및 일본어 텍스트를 음성으로 변환

3. **대화 학습**

   - 영어 및 일본어 대화 학습 지원
   - 핵심 단어 추출 및 예시 문장 제공
   - 대화 계속을 위한 예시 응답 제안

4. **번역 서비스**

   - 한국어 ↔ 영어, 한국어 ↔ 일본어, 영어 ↔ 일본어 번역

5. **통합 채팅 인터페이스**
   - 텍스트 및 음성 입력 지원
   - 대화 기록 유지 및 관리

## 기술 스택

- **백엔드**: Flask, Python 3.7+
- **음성 인식**: OpenAI Whisper
- **음성 합성**: Coqui TTS
- **자연어 처리**: OpenAI GPT API
- **프론트엔드**: HTML, CSS, JavaScript

## 프로젝트 아키택처

![image](https://github.com/user-attachments/assets/d70a5a70-4c92-46da-aae4-e1843fe54ab6)


## 프로젝트 구조

```
STT_TTS_FLASK/
│
├── app/                         # 애플리케이션 패키지
│   ├── __init__.py              # 앱 초기화 및 설정
│   ├── models/                  # 데이터 모델
│   ├── services/                # 서비스 계층
│   │   ├── gpt_service.py       # GPT API 서비스
│   │   ├── stt_service.py       # 음성 인식 서비스
│   │   ├── tts_service.py       # 음성 합성 서비스
│   │   └── translation_service.py # 번역 서비스
│   └── views/                   # 뷰 계층 (라우트 핸들러)
│       ├── chat_routes.py       # 대화 관련 라우트
│       ├── main_routes.py       # 메인 페이지 라우트
│       ├── stt_routes.py        # STT 관련 라우트
│       ├── tts_routes.py        # TTS 관련 라우트
│       ├── translation_routes.py # 번역 관련 라우트
│       └── utility_routes.py    # 유틸리티 라우트
├── config/                      # 설정 파일
│   └── settings.py              # 애플리케이션 설정
├── docs/                        # 문서화
│   ├── GPT_README.md            # GPT 서비스 문서
│   └── Spring&Python_README.md  # Spring과 Python 비교 문서
├── static/                      # 정적 파일
│   ├── css/                     # CSS 파일
│   └── js/                      # JavaScript 파일
├── templates/                   # HTML 템플릿
│   └── main.html                # 메인 템플릿
├── .env                         # 환경 변수 파일
├── app.py                       # 레거시 애플리케이션 파일
├── run.py                       # 애플리케이션 실행 스크립트
└── requirements.txt             # 의존성 목록
```

## 설치 및 실행 방법

### 필수 요구사항

- Python 3.7 이상
- FFmpeg (오디오 처리용)

### 설치 방법

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# FFmpeg 설치
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg
# macOS
brew install ffmpeg
# Windows: https://ffmpeg.org/download.html 에서 다운로드 후 PATH에 추가

# 필요 라이브러리 설치
pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일을 다음과 같이 구성합니다:

```
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# 앱 설정
SECRET_KEY=your_secret_key_here
FLASK_APP=run.py
FLASK_ENV=development
DEBUG=True

# 기타 설정
TEMP_FILES_LIFETIME=3600  # 임시 파일 보관 시간(초)
```

### 실행 방법

```bash
# 개발 환경 실행
python run.py

# 또는
flask run
```

서버는 기본적으로 http://localhost:5000 에서 실행됩니다.

## API 엔드포인트

자세한 API 문서는 다음 링크에서 확인할 수 있습니다:

- [STT(음성 인식) API 문서](docs/api/STT_API.md)
- [TTS(음성 합성) API 문서](docs/api/TTS_API.md)
- [대화 API 문서](docs/api/Chat_API.md)
- [번역 API 문서](docs/api/Translation_API.md)
- [유틸리티 API 문서](docs/api/Utility_API.md)

## 서비스별 상세 문서

- [음성 인식(STT) 서비스](docs/service/STT_Service.md)
- [음성 합성(TTS) 서비스](docs/service/TTS_Service.md)
- [GPT 서비스](docs/service/GPT_Service.md)
- [번역 서비스](docs/service/Translation_Service.md)

## 아키텍처 및 설계

이 프로젝트는 모듈화된 구조를 채택하여 유지보수성과 확장성을 높였습니다:

- **계층 분리**: 뷰(라우트), 서비스, 모델 계층 분리
- **서비스 계층**: 비즈니스 로직 캡슐화
- **지연 로딩**: 모델을 필요할 때만 로드하여 리소스 효율성 증대
- **공통 인터페이스**: 일관된 응답 형식으로 프론트엔드 통합 용이성 확보

[아키텍처 설계 상세 문서](docs/Architecture.md)

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 제출합니다.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 주의사항

1. **리소스 요구사항**: Whisper와 TTS 모델은 상당한 메모리를 사용합니다. 충분한 RAM이 필요합니다.
2. **초기 로딩 시간**: 모델 로딩 시 초기 지연이 발생할 수 있습니다.
3. **API 키 보안**: OpenAI API 키를 안전하게 관리하세요.
4. **FFmpeg 의존성**: 오디오 처리를 위해 FFmpeg가 필요합니다.
5. **프로덕션 배포**: 프로덕션 환경에서는 보안 설정과 에러 처리를 강화할 필요성이 있습니다.
