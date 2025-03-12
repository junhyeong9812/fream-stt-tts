FROM continuumio/miniconda3:4.12.0

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

# Python 3.9 환경 생성 및 활성화
RUN conda create -n tts python=3.9 -y
SHELL ["conda", "run", "-n", "tts", "/bin/bash", "-c"]

# Conda 환경에 기본 패키지 설치
COPY requirements.txt .
RUN conda install -y -c conda-forge scikit-learn=1.0.2 numpy=1.22.0 && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install openai-whisper==20231117 && \
    pip install TTS==0.16.0

# 애플리케이션 파일 복사
COPY app.py .
COPY templates/ templates/

# 모델 및 임시 파일 저장 디렉토리 생성
RUN mkdir -p models temp
RUN chmod 777 temp  # 임시 디렉토리에 쓰기 권한 부여

# 포트 노출
EXPOSE 5000

# 애플리케이션 실행
CMD ["conda", "run", "--no-capture-output", "-n", "tts", "python", "app.py"]