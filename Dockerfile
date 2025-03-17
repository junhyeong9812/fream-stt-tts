# 의존성 빌드 단계
FROM continuumio/miniconda3:4.12.0 AS conda-builder

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 환경 생성
RUN conda create -n tts python=3.9 -y
SHELL ["conda", "run", "-n", "tts", "/bin/bash", "-c"]

# 과학/ML 패키지는 conda로 설치
RUN conda install -y -c conda-forge \
    numpy=1.22.0 \
    scipy=1.10.1 \
    pandas=1.5.3 \
    matplotlib=3.7.2 \
    pyyaml=6.0.1 \
    tqdm=4.66.1 \
    cython=0.29.34 \
    scikit-learn=1.0.2 \
    pytorch=2.0.1 \
    cpuonly \
    && conda clean -afy

# pip 패키지 설치
RUN pip install --no-cache-dir \
    flask==2.2.5 \
    pydub==0.25.1 \
    soundfile==0.12.1 \
    openai-whisper==20231117 \
    TTS==0.22.0 \
    openai==1.3.0 \
    python-dotenv==1.0.0 \
    waitress

# 최종 이미지
FROM python:3.11-slim

# 환경변수 설정
ARG OPENAI_API_KEY
ARG OPENAI_MODEL=gpt-3.5-turbo
ARG FLASK_APP=app.py
ARG FLASK_ENV=development
ARG DEBUG=true
ARG TEMP_FILES_LIFETIME=3600

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV OPENAI_MODEL=$OPENAI_MODEL
ENV FLASK_APP=$FLASK_APP
ENV FLASK_ENV=$FLASK_ENV
ENV DEBUG=$DEBUG
ENV TEMP_FILES_LIFETIME=$TEMP_FILES_LIFETIME

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Conda 환경에서 설치된 패키지 복사
COPY --from=conda-builder /opt/conda/envs/tts/lib/python3.9/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=conda-builder /opt/conda/envs/tts/bin /usr/local/bin

# 추가 pip 패키지 설치 (필요한 경우)
RUN pip install --no-cache-dir \
    flask==2.2.5 \
    openai==1.3.0 \
    python-dotenv==1.0.0 \
    waitress

# 애플리케이션 파일 복사
COPY . .

# 모델 및 임시 파일 저장 디렉토리 생성
RUN mkdir -p models temp
RUN chmod 777 temp

# 포트 노출
EXPOSE 5000

# 실행 (waitress 서버 사용)
CMD ["python", "run.py"]


# FROM continuumio/miniconda3:4.12.0

# WORKDIR /app

# # 컴파일러 및 필요한 라이브러리 설치
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     build-essential \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Python 3.9 환경 생성 및 활성화
# RUN conda create -n tts python=3.9 -y
# SHELL ["conda", "run", "-n", "tts", "/bin/bash", "-c"]

# # 기존 가상환경 전체 복사 (venv 디렉토리를 그대로 복사)
# COPY venv /opt/conda/envs/tts

# # 모델 및 임시 파일 저장 디렉토리 생성
# RUN mkdir -p models temp
# RUN chmod 777 temp  # 임시 디렉토리에 쓰기 권한 부여

# # 애플리케이션 파일 복사
# COPY app.py .
# COPY templates/ templates/

# # 포트 노출
# EXPOSE 5000

# # 애플리케이션 실행
# CMD ["conda", "run", "--no-capture-output", "-n", "tts", "python", "app.py"]


