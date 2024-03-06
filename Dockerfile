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
ENV APP_ENV=dev

# SSH 키 복사
COPY /keys/id_rsa /root/.ssh/id_rsa
COPY /keys/id_rsa.pub /root/.ssh/id_rsa.pub

# requirements.txt에 있는 Python 의존성을 설치합니다.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 두 번째 SSH 포트 열기
EXPOSE 22222

# src/main.py를 실행합니다.
CMD ["python3", "src/main.py"]




# 이미지 빌드
# docker build -t ansible-core-image .

# 네트워크 생성
# docker network create cloudwiz-network

# 컨테이너 실행
# docker run -d --name cloudwiz-mq -p 5672:5672 -p 15672:15672 --network cloudwiz-network rabbitmq
## docker run -d --name ansible-core-container -v /Users/kimjihun/Documents/git/KTDS-IaCOpsCore:/app --network cloudwiz-network ansible-core-image
# docker run -d --name ansible-core-container -p 22222:22222 -v /Users/kimjihun/Documents/git/KTDS-IaCOpsCore:/app --network cloudwiz-network ansible-core-image

 
# docker exec -it cloudwiz-mq /bin/bash
# rabbitmq-plugins enable rabbitmq_management
# rabbitmqctl list_queues
# rabbitmqctl list_queues name_of_your_queue


# ps aux | grep sshd
# /etc/init.d/ssh start


# docker exec -it ansible-core-container /bin/bash
# root@b55a1ffd3561:/app# ansible --version
# ansible [core 2.16.4]
#   config file = None
#   configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
#   ansible python module location = /usr/local/lib/python3.10/site-packages/ansible
#   ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
#   executable location = /usr/local/bin/ansible
#   python version = 3.10.13 (main, Feb 13 2024, 09:39:14) [GCC 12.2.0] (/usr/local/bin/python)
#   jinja version = 3.1.3
#   libyaml = True


