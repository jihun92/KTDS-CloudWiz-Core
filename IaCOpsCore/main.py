import pika
import yaml
import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

logger = logging.getLogger(__name__)

class RabbitMQHandler:
    def __init__(self):
        env = os.environ.get('APP_ENV', 'dev')  # 환경 변수를 가져오며, 기본값은 'dev'
        config_filename = f"config/config_{env}.yaml"

        self.load_config(config_filename)

        self.load_config(config_filename)
        self.setup_logger()
        self.connect_to_rabbitmq()
        self.channel.queue_declare(queue=self.req_queue_name, durable=True)

        logger.info("RabbitMQHandler initialized.")

    def load_config(self, config_filename):
        with open(config_filename, 'r') as config_file:
            self.config = yaml.safe_load(config_file)
            self.mq_server_host = self.config['mq_server']['host']
            self.mq_server_port = self.config['mq_server']['port']
            self.mq_username = self.config['mq_server']['username']
            self.mq_password = self.config['mq_server']['password']
            self.req_queue_name = self.config['mq_server']['req_queue_name']
            self.res_queue_name = self.config['mq_server']['res_queue_name']

    def setup_logger(self):
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        log_path = self.config['log']['path']
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        file_handler.suffix = "%Y-%m-%d"

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    def connect_to_rabbitmq(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.mq_server_host, port=self.mq_server_port,
                                      credentials=pika.PlainCredentials(self.mq_username, self.mq_password))
        )
        self.channel = self.connection.channel()

    def publish_message(self, routing_key, message_body):
        self.channel.basic_publish(exchange='',
                                   routing_key=routing_key,
                                   body=message_body,
                                   properties=pika.BasicProperties(delivery_mode=2))
        logger.info(f"Sent '{message_body}' to {routing_key}")

    # 실제 비지니스 로직이 수행되는 함수 --- 여기에 코딩하세요
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
        # 비지니스 로직 수행
        self.handle_message(message_data)
        
        self.publish_message(self.res_queue_name, f"RETURN!!! {datetime.now()}")

    def start(self):
        self.channel.basic_consume(queue=self.req_queue_name, on_message_callback=self.process_message, auto_ack=True)
        logger.info("Waiting for messages...")
        self.channel.start_consuming()

if __name__ == "__main__":
    rabbitmq_handler = RabbitMQHandler()
    rabbitmq_handler.start()
