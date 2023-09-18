import pika
import yaml
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Logger 생성
logger = logging.getLogger(__name__)

class IaCOpsCore:
    def __init__(self):
        # 환경 변수로 환경 설정 (기본값은 'dev')
        env = os.environ.get('APP_ENV', 'dev')

        # 환경에 따른 설정 파일 경로 결정
        config_filename = f"config/config_{env}.yaml"

        # 설정 파일 로드 및 초기화
        self.load_config(config_filename)

        # Logger 설정 초기화
        self.setup_logger()

        # RabbitMQ에 연결
        self.connect_to_rabbitmq()

        # 메시지 수신 큐 선언
        self.channel.queue_declare(queue=self.req_queue_name, durable=True)

        logger.info("IaCOpsCore initialized.")

    def load_config(self, config_filename):
        # YAML 설정 파일 로드
        with open(config_filename, 'r') as config_file:
            self.config = yaml.safe_load(config_file)
            self.mq_server_host = self.config['mq_server']['host']
            self.mq_server_port = self.config['mq_server']['port']
            self.mq_username = self.config['mq_server']['username']
            self.mq_password = self.config['mq_server']['password']
            self.req_queue_name = self.config['mq_server']['req_queue_name']
            self.res_queue_name = self.config['mq_server']['res_queue_name']

    def setup_logger(self):
        # Logger 레벨 설정
        logger.setLevel(logging.INFO)

        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # 로그 파일 경로 설정 및 TimedRotatingFileHandler로 일일 로그 파일 생성
        log_path = self.config['log']['path']
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        file_handler.suffix = "%Y-%m-%d"

        # Logger에 핸들러 추가
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    def connect_to_rabbitmq(self):
        # RabbitMQ에 연결
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.mq_server_host, port=self.mq_server_port,
                                      credentials=pika.PlainCredentials(self.mq_username, self.mq_password))
        )
        self.channel = self.connection.channel()

    def publish_message(self, routing_key, message_body):
        # 메시지를 RabbitMQ에 발송
        self.channel.basic_publish(exchange='',
                                   routing_key=routing_key,
                                   body=message_body,
                                   properties=pika.BasicProperties(delivery_mode=2))
        logger.info(f"Sent '{message_body}' to {routing_key}")

    # 실제 비즈니스 로직이 수행되는 함수 --- 여기에 코딩하세요
    def handle_message(self, message_data):
        transaction_id = message_data['transaction_id']
        transmission_id = message_data['transmission_id']
        target = message_data['target']
        publish_type = message_data['publish_type']
        source = message_data['source']

        logger.info(f"transaction_id: {transaction_id}")
        logger.info(f"transmission_id: {transmission_id}")
        logger.info(f"target: {target}")
        logger.info(f"publish_type: {publish_type}")
        logger.info(f"source: {source}")

    def process_message(self, ch, method, properties, body):
        message = body.decode('utf-8')
        logger.info(f"Received message: {message}")

        message_data = json.loads(message)
        
        # 비즈니스 로직 수행
        self.handle_message(message_data)
        
        # 결과를 반환하기 위해 RabbitMQ에 메시지 발송
        self.publish_message(self.res_queue_name, f"RETURN!!! {datetime.now()}")

    def start(self):
        # 메시지 수신 대기 및 처리
        self.channel.basic_consume(queue=self.req_queue_name, on_message_callback=self.process_message, auto_ack=True)
        logger.info("Waiting for messages...")
        self.channel.start_consuming()

if __name__ == "__main__":
    # IaCOpsCore 인스턴스 생성 및 시작
    IaCOpsCore = IaCOpsCore()
    IaCOpsCore.start()
