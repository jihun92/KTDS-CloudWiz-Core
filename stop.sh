#!/bin/bash

# 저장된 프로세스 ID를 읽어와서 종료
if [ -f main.pid ]; then
    kill -9 $(cat main.pid)
    rm main.pid
else
    echo "No main.py process running."
fi
