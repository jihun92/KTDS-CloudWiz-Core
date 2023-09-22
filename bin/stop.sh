#!/bin/bash

# 환경 변수 설정 파일 읽기
source ./env.sh

# 저장된 프로세스 ID를 읽어와서 종료
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # 프로세스를 종료하고 PID 파일 삭제
    kill -9 "$PID" && rm "$PID_FILE"
    
    echo "main.py process (PID: $PID) has been stopped."
else
    echo "No main.py process running."
fi
