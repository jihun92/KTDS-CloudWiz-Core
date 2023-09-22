#!/bin/bash

# 환경 변수 설정 파일 읽기
source ./env.sh

# 환경 변수 사용
source "${VENV_PATH}/bin/activate"

# PID 디렉토리 생성 (존재하지 않는 경우)
if [ ! -d "$PID_DIR" ]; then
    mkdir "$PID_DIR"
fi

# 오류 로그 디렉토리 생성 (존재하지 않는 경우)
if [ ! -d "$LOG_DIR" ]; then
    mkdir "$LOG_DIR"
fi

# src 디렉토리로 이동
cd "$SRC_DIR"

# 이미 실행 중인 프로세스 검색
PS_RESULT=$(ps -ef | grep "$PROCESS_NAME" | grep -v grep)

# 이미 실행 중인 경우에는 추가로 실행하지 않음
if [ -n "$PS_RESULT" ]; then
    echo "Process '$PROCESS_NAME' is already running."
else
    # main.py 실행 (백그라운드에서 실행, 오류 로그 저장)
    nohup python "$PROCESS_NAME" > /dev/null 2>"$LOG_DIR/error.log" & 
    
    # 프로세스 ID 저장
    echo $! > "$PID_FILE"
    echo "Process '$PROCESS_NAME' started in the background (PID: $!)."
    echo "Error logs can be found in $LOG_DIR/error.log"
fi
