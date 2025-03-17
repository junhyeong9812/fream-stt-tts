# 유틸리티 API 문서

## 개요

유틸리티 API는 애플리케이션의 보조 기능을 제공하는 RESTful 엔드포인트 모음입니다. 주로 임시 파일 관리, 오디오 파일 제공 등의 기능을 담당합니다.

## 엔드포인트

### 1. 오디오 파일 다운로드

- **URL**: `/audio/<filename>`
- **메서드**: `GET`
- **설명**: 서버에 저장된 임시 오디오 파일 다운로드

### 2. 개별 임시 파일 정리

- **URL**: `/cleanup`
- **메서드**: `POST`
- **설명**: 특정 임시 파일 삭제

### 3. 임시 디렉토리 파일 대량 정리

- **URL**: `/cleanup/temp`
- **메서드**: `POST`
- **설명**: 오래된 임시 파일 일괄 삭제

## 요청 및 응답 형식

### 1. 오디오 파일 다운로드

#### 요청

- URL 경로에 파일 이름 포함
- 예: `/audio/output_en_123456.wav`

#### 성공 응답

- WAV 형식의 오디오 파일 직접 다운로드
- HTTP 상태 코드 200

#### 오류 응답

```json
{
  "error": "파일을 찾을 수 없습니다"
}
```

### 2. 개별 임시 파일 정리

#### 요청

```json
{
  "filename": "경로/파일명"
}
```

#### 성공 응답

```json
{
  "success": true
}
```

#### 오류 응답

```json
{
  "success": false,
  "error": "오류 메시지"
}
```

### 3. 임시 디렉토리 파일 대량 정리

#### 요청

- 요청 본문 없음

#### 성공 응답

```json
{
  "success": true,
  "deleted_files": 10 // 삭제된 파일 수
}
```

## 요청 예시

### cURL 요청

```bash
# 오디오 파일 다운로드
curl http://localhost:5000/audio/output_en_123456.wav --output downloaded_audio.wav

# 개별 임시 파일 삭제
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"filename":"/path/to/temp/file.wav"}' \
  http://localhost:5000/cleanup

# 임시 디렉토리 파일 대량 정리
curl -X POST http://localhost:5000/cleanup/temp
```

### Python 요청

```python
import requests

# 오디오 파일 다운로드
response = requests.get("http://localhost:5000/audio/output_en_123456.wav")
if response.status_code == 200:
    with open("downloaded_audio.wav", "wb") as f:
        f.write(response.content)

# 개별 임시 파일 삭제
response = requests.post(
    "http://localhost:5000/cleanup",
    json={"filename": "/path/to/temp/file.wav"}
)
print(response.json())

# 임시 디렉토리 파일 대량 정리
response = requests.post("http://localhost:5000/cleanup/temp")
print(response.json())
```

## 주요 기능

### 1. 임시 파일 수명 관리

- 기본 임시 파일 수명: 1시간
- 설정 가능한 수명 시간
- 자동 파일 정리를 통한 디스크 공간 관리

### 2. 보안 고려사항

- 임시 파일은 안전한 디렉토리에 저장
- 접근 제한 및 권한 관리
- 민감한 데이터 보호

## 성능 고려사항

- 파일 삭제 작업은 비동기적으로 처리
- 대량 파일 정리 시 시스템 리소스 최적화
- 로깅을 통한 파일 관리 추적

## 오류 처리

1. 파일 미존재 오류
2. 파일 삭제 권한 오류
3. 디스크 공간 부족 오류
4. 네트워크 관련 오류

## 향후 개선 예정 기능

- 더 세밀한 파일 수명 관리
- 사용자 정의 임시 파일 정리 정책
- 로깅 및 모니터링 기능 강화
- 클라우드 스토리지 통합 지원

## 주의사항

- 임시 파일은 자동으로 삭제될 수 있음
- 중요한 파일은 영구 저장소에 별도 보관
- API 사용 시 적절한 예외 처리 필요
