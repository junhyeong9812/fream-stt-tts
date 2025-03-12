FROM python:3.9-slim

WORKDIR /app

# ffmpeg 설치
RUN apt-get update && apt-get install -y ffmpeg cron && apt-get clean

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app.py .
COPY templates/ templates/

# 모델 및 임시 파일 저장 디렉토리 생성
RUN mkdir -p models temp
RUN chmod 777 temp  # 임시 디렉토리에 쓰기 권한 부여

# 크론 작업 설정 - 매시간 임시 파일 정리
COPY cleanup_cron /etc/cron.d/cleanup_cron
RUN chmod 0644 /etc/cron.d/cleanup_cron
RUN crontab /etc/cron.d/cleanup_cron

# 포트 노출
EXPOSE 5000

# 애플리케이션 실행 (+ cron 실행)
COPY start.sh .
RUN chmod +x start.sh
CMD ["./start.sh"]