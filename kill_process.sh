#!/bin/bash

# 프로세스 이름
PROCESS_NAME="IaCOpsCore.py"

# ps 명령어로 프로세스 검색
PS_RESULT=$(ps -ef | grep "$PROCESS_NAME" | grep -v grep)

# 검색 결과가 비어있지 않으면 해당 프로세스를 강제로 종료
if [ -n "$PS_RESULT" ]; then
    # 해당 프로세스 ID를 추출하여 종료
    PIDS=($(echo "$PS_RESULT" | awk '{print $2}'))
    echo "Killing process '$PROCESS_NAME'..."

    for PID in "${PIDS[@]}"; do
        echo "  - PID: $PID"
        kill -9 $PID
        echo "    Process '$PROCESS_NAME' (PID: $PID) killed."
    done
else
    echo "Process '$PROCESS_NAME' is not running."
fi
