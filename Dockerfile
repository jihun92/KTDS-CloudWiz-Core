FROM python:3.10

# SSH 서버 설치
RUN apt-get update && \
    apt-get install -y openssh-server && \
    apt-get clean

# # SSH 서버 설정
# RUN mkdir /var/run/sshd
# RUN echo 'root:new1234' | chpasswd
# RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# # 두 번째 SSH 포트 추가
# RUN echo 'Port 22222' >> /etc/ssh/sshd_config

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 내용을 컨테이너의 /app 디렉토리에 복사합니다.
COPY . /app

# 환경 변수를 설정합니다.
ENV PROJECT_ROOT=/app
ENV CONFIG_DIR=/app/config
ENV APP_ENV=local

# /app/logs 디렉토리를 만듭니다.
RUN mkdir /app/logs

# SSH 키 복사
# COPY /keys/id_rsa /root/.ssh/id_rsa
# COPY /keys/id_rsa.pub /root/.ssh/id_rsa.pub
# COPY /keys/id_rsa.pub /etc/ssh/ssh_host_rsa_key.pub

# requirements.txt에 있는 Python 의존성을 설치합니다.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 두 번째 SSH 포트 열기
EXPOSE 22

# src/main.py를 실행합니다.
# CMD ["python3", "src/main.py"]

COPY start_ssh_service.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start_ssh_service.sh

# CMD를 사용하여 파이썬 코드 실행 및 SSH 서비스 시작 스크립트를 백그라운드에서 실행
CMD ["sh", "-c", "start_ssh_service.sh & python src/main.py"]


# 이미지 빌드
# docker build -t ansible-core-image .

# 네트워크 생성
# docker network create cloudwiz-network

# 컨테이너 실행
# docker run -d --name cloudwiz-mq -p 5672:5672 -p 15672:15672 --network cloudwiz-network rabbitmq
## docker run -d --name ansible-core-container -v /Users/kimjihun/Documents/git/KTDS-IaCOpsCore:/app --network cloudwiz-network ansible-core-image
# docker run -d --name ansible-core-container -p 22:22 -v /Users/kimjihun/Documents/git/KTDS-IaCOpsCore:/app --network cloudwiz-network ansible-core-image

 
# docker exec -it cloudwiz-mq /bin/bash
# rabbitmq-plugins enable rabbitmq_management
# rabbitmqctl list_queues
# rabbitmqctl list_queues name_of_your_queue




## 도커 허브
# docker build -t jihun92/cloudwiz-ansible-core:test .
# docker push jihun92/cloudwiz-ansible-core:test

# docker pull jihun92/cloudwiz-ansible-core:test
# sudo docker run -d jihun92/cloudwiz-ansible-core:test
# docker run -d --name ansible-core-container -v /home/ubuntu/KTDS-CloudWiz-Core:/app ansible-core-image
