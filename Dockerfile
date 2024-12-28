# 1. Python 베이스 이미지 사용 (필요한 버전에 따라 변경 가능)
FROM python:3.9-slim
# 2. 작업 디렉토리 설정
WORKDIR /
# 3. 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt
# 4. Flask 앱 소스 복사
COPY . .
# 5. Gunicorn으로 Flask 애플리케이션 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]