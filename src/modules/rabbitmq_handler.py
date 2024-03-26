# rabbitmq_handler.py
import pika
import json

from modules.ansible_handler import AnsibleHandler
from config.logger_setting import Logger

class RabbitMQHandler:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RabbitMQHandler, cls).__new__(cls)
        return cls._instance
    
    def init(self, mq_config):
        
        # RabbitMQ
        self.init_config(mq_config)
        self.init_handlers()
        self.connect_to_rabbitmq()
        self.queue_declare()

        # log
        self.logger = Logger()
        
    def init_config(self, mq_config):
        self.mq_server_host = mq_config['host']
        self.mq_server_port = mq_config['port']
        self.mq_username = mq_config['username']
        self.mq_password = mq_config['password']
        self.req_queue_name = mq_config['req_queue_name']
        
    def init_handlers(self):
        self.handlers = {
            'ansible': AnsibleHandler(self)
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

    def publish_message(self, routing_key, header_dict, body_dict):
        properties = pika.BasicProperties(delivery_mode=2)
        if header_dict:
            properties.headers = header_dict

        body_str = json.dumps(body_dict, indent=4)
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=body_str,
            properties=properties
        )

        self.logger.info(f"Send Message to {routing_key} !!!\nSend Message's Header : {properties.headers},\nReceived Message's body : {body_str}")

        
    def handle_message(self, header_dict, body_dict):
        target = "ansible" # ansible core 추가 개발 시 조건문 필요
        handler = self.handlers.get(target)
        if handler:
            result = handler.process(header_dict, body_dict)
        else:
            self.logger.warning(f"Unknown target: {target}")

        return result
    
    # 큐에 메세지가 들어오면 처리되는 메서드
    def process_message(self, ch, method, properties, body):

        header_dict = properties.headers
        body_str = body.decode('utf-8')

        self.logger.info(f"Received Message !!!\nReceived Message's Header : {header_dict},\nHeader type: {type(header_dict)}\nReceived Message's body : {body_str},\nbody type: {type(body_str)}")

        # 핸들러에게 메시지 전달
        body_dict = json.loads(body_str)
        # header_dict = json.loads(header_json)
        result = self.handle_message(header_dict, body_dict)

        
    def start(self):
        self.channel.basic_consume(
            queue=self.req_queue_name,
            on_message_callback=self.process_message,
            auto_ack=True
        )
        self.logger.info("Waiting for messages...")
        self.channel.start_consuming()
