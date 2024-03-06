#!/bin/bash

# SSH 서버 시작
/usr/sbin/sshd -D &

# 파이썬 프로그램 실행
python3 src/main.py
