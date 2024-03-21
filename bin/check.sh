#!/bin/bash

# ps 명령어로 프로세스 검색 및 개수 세기
PROCESS_COUNT=$(ps -ef | grep -v grep | grep -c "main.py")