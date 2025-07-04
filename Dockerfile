FROM python:3.11-slim

WORKDIR /app

# 컴파일러 및 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt로 새로 설치 (이게 가장 안전함)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 애플리케이션 파일 복사
COPY run.py .
COPY app/ app/  
COPY config/ config/  
COPY templates/ templates/
COPY static/ static/

# 모델 및 임시 파일 저장 디렉토리 생성
RUN mkdir -p models temp logs
RUN chmod 777 temp logs

# 포트 노출
EXPOSE 5000

# 애플리케이션 실행
CMD ["python", "run.py"]