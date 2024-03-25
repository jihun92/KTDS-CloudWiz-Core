#!/bin/bash

# 환경 변수 설정
export PROJECT_ROOT=/app
export CONFIG_DIR=/app/config
export APP_ENV=dev

mkdir -p /app/logs

# stdout과 stderr 출력을 /dev/null로 리디렉션하여 nohup.out 파일 생성 방지
nohup python3 /app/src/main.py > /dev/null 2>&1 &
