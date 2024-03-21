#!/bin/bash

# 프로세스 이름
PROCESS_NAME="main.py"

# ps 명령어로 프로세스 검색
PS_RESULT=$(ps -ef | grep "$PROCESS_NAME" | grep -v grep)