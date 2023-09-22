# rabbitmq_handler.py
import pika
import json

from modules.ansible_handler import AnsibleHandler
from modules.terraform_handler import TerraformHandler

class RabbitMQHandler:
    def __init__(self, mq_config, logger):
        self.logger = logger
        self.init_config(mq_config)
        self.init_handlers()
        self.connect_to_rabbitmq()
        self.queue_declare()
        
    def init_config(self, mq_config):
        self.mq_server_host = mq_config['host']
        self.mq_server_port = mq_config['port']
        self.mq_username = mq_config['username']
        self.mq_password = mq_config['password']
        self.req_queue_name = mq_config['req_queue_name']
        self.res_queue_name = mq_config['res_queue_name']
        
    def init_handlers(self):
        self.handlers = {
            'ansible': AnsibleHandler(),
            'terraform': TerraformHandler(),
        }
        
    def queue_declare(self):
        self.channel.queue_declare(queue=self.req_queue_name, durable=True)
        
    def connect_to_rabbitmq(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.mq_server_host,
                    port=self.mq_server_port,
                    credentials=pika.PlainCredentials(self.mq_username, self.mq_password)
                )
            )
            self.channel = self.connection.channel()
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish_message(self, routing_key, message_body):
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        self.logger.info(f"Sent '{message_body}' to {routing_key}")
        
    def handle_message(self, message_data):
        target = "terraform" # ansible core 추가 개발 시 조건문 필요
        handler = self.handlers.get(target)
        if handler:
            result = handler.process(message_data)
        else:
            self.logger.warning(f"Unknown target: {target}")

        return result
        
    def process_message(self, ch, method, properties, body):
        message = body.decode('utf-8')
        self.logger.info(f"Received message: {message}")
        
        message_data = json.loads(message)
        result = self.handle_message(message_data)
        
        self.publish_message(self.res_queue_name, result)
        
    def start(self):
        self.channel.basic_consume(
            queue=self.req_queue_name,
            on_message_callback=self.process_message,
            auto_ack=True
        )
        self.logger.info("Waiting for messages...")
        self.channel.start_consuming()
