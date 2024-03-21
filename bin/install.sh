#!/bin/bash

# 환경 변수 설정
export PROJECT_ROOT=/app
export CONFIG_DIR=/app/config
export APP_ENV=dev

# SSH 서비스 시작
service ssh start

# requirements.txt에 있는 Python 의존성 설치
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
