# 베이스 이미지 선택
FROM python:3.12.4

# 필요한 파일 복사
COPY . .

# 필요 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Flask 서버 실행
ENTRYPOINT ["python3", "app.py"]
