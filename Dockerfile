FROM python:3.9-slim

WORKDIR /app

# 컴파일러 및 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libopenblas-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 기본 종속성 먼저 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Whisper 및 TTS 별도 설치
RUN pip install --no-cache-dir openai-whisper==20231117
RUN pip install --no-cache-dir TTS[all]==0.17.0

# 애플리케이션 파일 복사
COPY app.py .
COPY templates/ templates/

# 모델 및 임시 파일 저장 디렉토리 생성
RUN mkdir -p models temp
RUN chmod 777 temp  # 임시 디렉토리에 쓰기 권한 부여

# 포트 노출
EXPOSE 5000

# 애플리케이션 실행
CMD ["python", "app.py"]