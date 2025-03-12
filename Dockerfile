FROM continuumio/miniconda3:4.12.0

WORKDIR /app

# 컴파일러 및 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 3.9 환경 생성 및 활성화
RUN conda create -n tts python=3.9 -y
SHELL ["conda", "run", "-n", "tts", "/bin/bash", "-c"]

# 과학/데이터 관련 패키지는 conda로 설치 - 그룹으로 나누어 설치
RUN conda install -y -c conda-forge numpy=1.22.0 && conda clean -afy
RUN conda install -y -c conda-forge scipy=1.10.1 && conda clean -afy
RUN conda install -y -c conda-forge pandas=1.5.3 && conda clean -afy
RUN conda install -y -c conda-forge matplotlib=3.7.2 && conda clean -afy
RUN conda install -y -c conda-forge pyyaml=6.0.1 tqdm=4.66.1 && conda clean -afy
RUN conda install -y -c conda-forge cython=0.29.34 && conda clean -afy
RUN conda install -y -c conda-forge scikit-learn=1.0.2 && conda clean -afy

# PyTorch 설치
RUN conda install -y -c pytorch pytorch=2.0.1 cpuonly && conda clean -afy

# 나머지 패키지는 pip로 설치 - 그룹으로 나누어 설치
RUN pip install --upgrade pip
RUN pip install flask==2.0.1 pydub==0.25.1 soundfile==0.12.1
RUN pip install gruut==2.2.3 nltk==3.8.1
RUN pip install jamo==0.4.1 bangla==0.0.2 g2pkk==0.1.2 trainer==0.0.36

# Whisper와 TTS 설치
RUN pip install openai-whisper==20231117
RUN pip install TTS==0.16.0

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