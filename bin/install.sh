#!/bin/bash

# SSH 서비스 시작
service ssh start

# requirements.txt에 있는 Python 의존성 설치
pip3 install --upgrade pip
pip3 install --no-cache-dir -r requirements.txt
