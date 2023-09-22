# env.sh
export PROJECT_ROOT="$(dirname $PWD)"
export VENV_PATH="$PROJECT_ROOT/venv"
export PID_DIR="$PROJECT_ROOT/bin/pid"
export SRC_DIR="$PROJECT_ROOT/src"
export PROCESS_NAME="main.py"
export PID_FILE="$PID_DIR/main.pid"
export CONFIG_DIR="$PROJECT_ROOT/config" 
export LOG_DIR="$PROJECT_ROOT/logs" # 파이썬 실행 시 발생하는 오류 로그