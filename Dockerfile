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
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Miniconda 설치
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh

# PATH에 conda 추가
ENV PATH="/opt/conda/bin:${PATH}"

# pip 업그레이드 및 requirements.txt 설치 (기본 Python 환경용)
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Conda 환경 생성 및 TTS 설치
RUN conda create -n tts python=3.9 -y
SHELL ["conda", "run", "-n", "tts", "/bin/bash", "-c"]

# conda 환경에 필요한 패키지 설치
RUN conda install -y -c conda-forge scikit-learn=1.0.2 && \
    pip install openai-whisper==20231117 && \
    pip install "TTS==0.17.0"

# 기본 쉘로 복귀
SHELL ["/bin/bash", "-c"]

# Conda 환경 활성화 스크립트 추가
RUN echo 'source /opt/conda/etc/profile.d/conda.sh && conda activate tts' > /root/.bashrc

# 애플리케이션 파일 복사
COPY app.py .
COPY templates/ templates/

# 모델 및 임시 파일 저장 디렉토리 생성
RUN mkdir -p models temp
RUN chmod 777 temp  # 임시 디렉토리에 쓰기 권한 부여

# 포트 노출
EXPOSE 5000

# conda 환경에서 애플리케이션 실행
CMD ["/bin/bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate tts && python app.py"]