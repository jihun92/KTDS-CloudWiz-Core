#!/bin/bash

# 가상 환경 활성화 (venv 라는 이름의 가상 환경을 사용한다고 가정)
source venv/bin/activate

# IaCOpsCore 디렉토리로 이동
cd IaCOpsCore

# main.py 실행
python main.py &

# 프로세스 ID 저장
echo $! > main.pid
