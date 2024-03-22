#!/bin/bash

# 환경 변수 설정
export PROJECT_ROOT=/app
export CONFIG_DIR=/app/config
export APP_ENV=dev

mkdir -p /app/logs

nohup python /app/src/main.py &