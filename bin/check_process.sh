#!/bin/bash

# 환경 변수 설정 파일 읽기
source ./env.sh

# ps 명령어로 프로세스 검색 및 개수 세기
PROCESS_COUNT=$(ps -ef | grep -v grep | grep -c "$PROCESS_NAME")

if [ $PROCESS_COUNT -gt 0 ]; then
    echo "Process '$PROCESS_NAME' is running ($PROCESS_COUNT instances):"
    
    # 각 프로세스의 PID 출력
    PIDS=$(ps -ef | grep -v grep | grep "$PROCESS_NAME" | awk '{print $2}')
    for PID in $PIDS; do
        echo "  - PID: $PID"
    done
else
    echo "Process '$PROCESS_NAME' is not running."
fi
