#!/bin/bash

# 가상 환경 활성화 (venv 라는 이름의 가상 환경을 사용한다고 가정)
source ../venv/bin/activate

# PID 디렉토리 경로
PID_DIR="pid"

# PID 디렉토리 생성 (존재하지 않는 경우)
if [ ! -d "$PID_DIR" ]; then
    mkdir "$PID_DIR"
fi

# IaCOpsCore 디렉토리로 이동
cd ../IaCOpsCore

# 프로세스 이름
PROCESS_NAME="IaCOpsCore.py"

# 이미 실행 중인 프로세스 검색
PS_RESULT=$(ps -ef | grep "$PROCESS_NAME" | grep -v grep)

# 이미 실행 중인 경우에는 추가로 실행하지 않음
if [ -n "$PS_RESULT" ]; then
    echo "Process '$PROCESS_NAME' is already running."
else
    # IaCOpsCore.py 실행 (백그라운드에서 실행)
    nohup python ../IaCOpsCore/IaCOpsCore.py > /dev/null 2>&1 &
    
    # 프로세스 ID 저장
    echo $! > "../bin/$PID_DIR/IaCOpsCore.pid"
    echo "Process '$PROCESS_NAME' started in the background (PID: $!)."
fi
