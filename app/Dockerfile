# Python 3.12 슬림 버전 사용 (가볍고 빠름)
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
# PYTHONDONTWRITEBYTECODE 1: .pyc 파일 생성 방지 (컨테이너 깔끔하게 유지)
# PYTHONUNBUFFERED 1: 로그가 버퍼링 없이 즉시 출력되게 함
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 의존성 파일 복사 및 설치
COPY /requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 현재 app 디렉토리의 모든 파일을 컨테이너의 /app으로 복사
COPY . .

# 8888 포트 열기
EXPOSE 8888

# 서버 실행 명령어 (0.0.0.0으로 바인딩하여 외부 접속 허용)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]
