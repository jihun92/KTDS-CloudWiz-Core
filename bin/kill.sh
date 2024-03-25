#!/bin/bash

# main.py 프로세스를 찾아서 PID 가져오기
main_py_pids=$(pgrep -f "python3 /app/src/main.py")

# main.py 프로세스가 실행 중인지 확인
if [ -z "$main_py_pids" ]; then
    echo "main.py 프로세스가 실행 중이지 않습니다."
else
    # 각 PID에 대해 프로세스 종료
    for pid in $main_py_pids; do
        echo "main.py 프로세스를 종료합니다. PID: $pid"
        kill -9 "$pid"
    done
fi

