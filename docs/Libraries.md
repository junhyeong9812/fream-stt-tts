# 라이브러리 가이드

이 문서는 STT-TTS-FLASK 프로젝트에서 사용된 주요 라이브러리와 기술에 대한 설명을 제공합니다.

## 목차

1. [웹 프레임워크](#웹-프레임워크)
2. [OpenAI API](#openai-api)
3. [오디오 처리](#오디오-처리)
4. [과학적 계산 및 데이터 처리](#과학적-계산-및-데이터-처리)
5. [TTS 및 의존성](#tts-및-의존성)
6. [유틸리티](#유틸리티)
7. [PyTorch](#pytorch)
8. [WSGI 서버](#wsgi-서버)
9. [FFmpeg 설치 가이드](#ffmpeg-설치-가이드)

## 웹 프레임워크

### Flask (2.2.5)

- **설명**: Flask는 가볍고 확장 가능한 Python 웹 프레임워크입니다. 마이크로 프레임워크로 분류되지만, 확장성을 통해 복잡한 애플리케이션도 구축할 수 있습니다.
- **주요 기능**: 라우팅, 요청 처리, 템플릿 렌더링, 쿠키 및 세션 관리
- **프로젝트 내 역할**: 웹 API 엔드포인트 정의, HTTP 요청 처리, 응답 생성

### Werkzeug (2.2.3)

- **설명**: Werkzeug는 WSGI 유틸리티 라이브러리로, Flask의 핵심 의존성입니다.
- **주요 기능**: HTTP 요청/응답 객체, URL 라우팅, 디버깅 기능
- **프로젝트 내 역할**: Flask의 기반 기능 제공, 요청 처리 지원

### Jinja2 (3.1.3)

- **설명**: Jinja2는 Python용 모던 템플릿 엔진입니다.
- **주요 기능**: HTML 템플릿 렌더링, 템플릿 상속, 필터 및 매크로
- **프로젝트 내 역할**: 웹 인터페이스 템플릿 렌더링

### itsdangerous (2.1.2) & click (8.1.7)

- **설명**: Flask의 의존성 라이브러리
- **주요 기능**:
  - itsdangerous: 데이터 서명 및 직렬화 지원
  - click: 명령줄 인터페이스 생성 지원
- **프로젝트 내 역할**: Flask의 기본 기능 지원

## OpenAI API

### openai (1.3.0)

- **설명**: OpenAI의 공식 Python 클라이언트 라이브러리입니다.
- **주요 기능**: GPT 모델 API 호출, 응답 처리, 토큰 관리
- **프로젝트 내 역할**: GPT를 활용한 대화 처리 및 번역 기능 구현

### python-dotenv (1.0.0)

- **설명**: 환경 변수를 `.env` 파일에서 로드하는 라이브러리입니다.
- **주요 기능**: 환경 변수 관리
- **프로젝트 내 역할**: API 키 등 민감한 설정 정보 관리

## 오디오 처리

### openai-whisper (20230918)

- **설명**: OpenAI의 Whisper는 음성 인식 모델로, 다양한 언어의 음성을 텍스트로 변환합니다.
- **주요 기능**: 다국어 음성 인식, 다양한 악센트 지원, 배경 소음에 강인함
- **프로젝트 내 역할**: 영어/일본어 음성을 텍스트로 변환하는 STT 기능
- **동작 방식**:
  1. 오디오 입력을 로그-멜 스펙트로그램으로 변환
  2. 인코더-디코더 Transformer 아키텍처로 처리
  3. 텍스트 출력 생성

### pydub (0.25.1)

- **설명**: 오디오 파일 처리를 위한 Python 라이브러리입니다.
- **주요 기능**: 오디오 파일 포맷 변환, 편집, 필터링
- **프로젝트 내 역할**: 업로드된 오디오 파일 처리 및 변환
- **동작 방식**: FFmpeg를 백엔드로 사용하여 다양한 오디오 형식 지원

### soundfile (0.12.1)

- **설명**: 오디오 파일 읽기/쓰기를 위한 라이브러리입니다.
- **주요 기능**: 다양한 오디오 포맷 지원, 낮은 수준의 오디오 데이터 접근
- **프로젝트 내 역할**: 오디오 데이터 처리 및 저장

## 과학적 계산 및 데이터 처리

### numpy (1.24.3)

- **설명**: 수치 계산을 위한 기본 Python 라이브러리입니다.
- **주요 기능**: 다차원 배열, 벡터화 연산, 선형 대수
- **프로젝트 내 역할**: 오디오 데이터 처리 및 분석을 위한 기반

### scipy (>=1.11.2)

- **설명**: 과학적 계산을 위한 고급 라이브러리입니다.
- **주요 기능**: 신호 처리, 통계, 최적화, 선형 대수
- **프로젝트 내 역할**: 오디오 신호 처리 지원

### pandas (1.5.3)

- **설명**: 데이터 분석 및 조작을 위한 라이브러리입니다.
- **주요 기능**: 데이터프레임, 시리즈, 데이터 정제 및 변환
- **프로젝트 내 역할**: 데이터 처리 및 분석

### scikit-learn (>=1.3.0)

- **설명**: 머신러닝 알고리즘 및 데이터 전처리를 위한 라이브러리입니다.
- **주요 기능**: 분류, 회귀, 군집화, 차원 축소
- **프로젝트 내 역할**: 모델 및 데이터 처리 기능 지원

## TTS 및 의존성

### TTS [all] (0.22.0)

- **설명**: Coqui TTS는 고품질 음성 합성을 위한 딥러닝 기반 라이브러리입니다.
- **주요 기능**: 다양한 TTS 모델 지원, 다국어 지원, 음성 커스터마이징
- **프로젝트 내 역할**: 텍스트를 자연스러운 음성으로 변환하는 TTS 기능
- **동작 방식**:
  1. 텍스트 정규화 및 전처리
  2. Tacotron2 등의 모델을 사용하여 음성 특성 생성
  3. 보코더를 통한 최종 오디오 생성

### Cython (0.29.36)

- **설명**: Python 코드를 C로 컴파일하여 성능을 개선하는 프로그래밍 언어입니다.
- **주요 기능**: Python 코드 최적화, C 확장 모듈 생성
- **프로젝트 내 역할**: TTS 및 오디오 처리 성능 최적화

### numba (0.57.1)

- **설명**: Just-In-Time 컴파일러로 Python 코드 속도를 향상시키는 라이브러리입니다.
- **주요 기능**: 넘파이 배열 연산 최적화, 병렬 처리 지원
- **프로젝트 내 역할**: 오디오 처리 및 신호 분석 성능 향상

## 유틸리티

### pyyaml (6.0.1)

- **설명**: YAML 파일 처리를 위한 라이브러리입니다.
- **주요 기능**: YAML 파싱 및 생성
- **프로젝트 내 역할**: 설정 파일 관리

### tqdm (4.66.1)

- **설명**: 진행 상태 표시를 위한 라이브러리입니다.
- **주요 기능**: 반복 작업의 진행률 시각화
- **프로젝트 내 역할**: 모델 로딩 및 처리 진행 상태 표시

### matplotlib (3.7.2)

- **설명**: 데이터 시각화를 위한 라이브러리입니다.
- **주요 기능**: 그래프, 차트, 시각화 도구
- **프로젝트 내 역할**: 디버깅 및 모델 분석용 시각화

### jamo (0.4.1)

- **설명**: 한글 자모 분리 및 결합을 위한 라이브러리입니다.
- **주요 기능**: 한글 음절 처리, 자모 분석
- **프로젝트 내 역할**: 한국어 텍스트 처리 지원

### multidict (6.0.4) & requests (2.31.0)

- **설명**: 유틸리티 라이브러리입니다.
- **주요 기능**:
  - multidict: 다중 값 딕셔너리 구현
  - requests: HTTP 요청 처리
- **프로젝트 내 역할**: 내부 데이터 구조 및 API 통신 지원

## PyTorch

### torch (>=2.1.0)

- **설명**: 딥러닝 프레임워크입니다.
- **주요 기능**: 신경망 모델 정의, 훈련, 추론
- **프로젝트 내 역할**: Whisper 및 TTS 모델의 기반 프레임워크
- **동작 방식**: 텐서 연산을 통한 신경망 계산, 자동 미분, GPU 가속

### torchaudio (>=2.1.0)

- **설명**: PyTorch의 오디오 처리 라이브러리입니다.
- **주요 기능**: 오디오 데이터 로딩, 변환, 특성 추출
- **프로젝트 내 역할**: 음성 데이터 전처리 및 모델 입력 준비

### torchvision (>=0.16.0)

- **설명**: PyTorch의 컴퓨터 비전 라이브러리입니다.
- **주요 기능**: 이미지 처리, 데이터셋, 모델
- **프로젝트 내 역할**: PyTorch 의존성 지원

## WSGI 서버

### gunicorn (21.2.0)

- **설명**: UNIX 시스템용 Python WSGI HTTP 서버입니다.
- **주요 기능**: 멀티 프로세스 아키텍처, 프로덕션 배포 지원
- **프로젝트 내 역할**: UNIX/Linux 환경에서의 프로덕션 서버
- **동작 방식**: 워커 프로세스 관리를 통한 요청 처리 및 로드 밸런싱

### waitress (2.1.2)

- **설명**: 크로스 플랫폼 WSGI 서버입니다.
- **주요 기능**: Windows 지원, 멀티스레드 아키텍처
- **프로젝트 내 역할**: Windows 환경에서의 프로덕션 서버
- **동작 방식**: 스레드 풀을 통한 요청 처리

## FFmpeg 설치 가이드

### FFmpeg이란?

FFmpeg은 오디오 및 비디오를 기록, 변환 및 스트리밍하기 위한 완전한 크로스 플랫폼 솔루션입니다. 본 프로젝트에서는 주로 오디오 파일 처리와 변환에 사용됩니다.

### FFmpeg이 필요한 이유

- **다양한 오디오 형식 지원**: WAV, MP3, OGG 등 다양한 오디오 포맷 변환
- **오디오 처리**: 표본화율 변경, 채널 수 조정, 볼륨 정규화 등
- **pydub 라이브러리의 백엔드**: pydub은 내부적으로 FFmpeg을 사용하여 오디오 처리

### 운영체제별 설치 방법

#### Windows

1. [FFmpeg 공식 다운로드 페이지](https://ffmpeg.org/download.html)에서 Windows 버전 다운로드
2. 다운로드한 zip 파일 압축 해제
3. 압축 해제된 폴더 내의 `bin` 디렉토리를 시스템 환경 변수 PATH에 추가
4. 명령 프롬프트에서 `ffmpeg -version`을 실행하여 설치 확인

#### macOS

Homebrew를 사용한 설치:

```bash
brew install ffmpeg
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

#### CentOS/RHEL

```bash
sudo yum install epel-release
sudo yum install ffmpeg ffmpeg-devel
```

### 설치 확인

터미널 또는 명령 프롬프트에서 다음 명령을 실행하여 FFmpeg이 올바르게 설치되었는지 확인:

```bash
ffmpeg -version
```

### FFmpeg와 프로젝트 통합

FFmpeg이 설치되면 Python 라이브러리(특히 pydub)가 자동으로 이를 감지하고 활용합니다. 별도의 Python 코드 변경 없이 오디오 처리 기능이 작동합니다.

## 추가 정보

### 의존성 설치

모든 프로젝트 의존성 설치:

```bash
pip install -r requirements.txt
```

### 가상 환경 사용 권장

독립적인 환경에서 프로젝트를 실행하기 위해 가상 환경 사용을 권장합니다:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
