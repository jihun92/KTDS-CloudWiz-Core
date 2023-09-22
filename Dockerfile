# 공식 Python 런타임을 부모 이미지로 사용합니다.
FROM python:3.10

# 컨테이너 내에서 /app 디렉토리를 작업 디렉토리로 설정합니다.
WORKDIR /app

# 현재 디렉토리의 내용을 컨테이너의 /app 디렉토리에 복사합니다.
COPY . /app

# 환경 변수를 설정합니다.
ENV PROJECT_ROOT /app
# ENV SRC_DIR /app/src
# ENV PROCESS_NAME main.py
ENV CONFIG_DIR /app/config
# ENV LOG_PATH /app/log

# requirements.txt에 있는 Python 의존성을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 필요하다면 사전 설정 스크립트를 실행합니다.
# RUN bash bin/setup.sh

# src/main.py를 실행합니다.
CMD ["python", "src/main.py"]
