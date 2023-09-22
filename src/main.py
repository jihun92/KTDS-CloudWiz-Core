# main.py
import os
import yaml
from datetime import datetime
from config.logger_setup import setup_logger
from modules.rabbitmq_handler import RabbitMQHandler

# 환경 변수로 환경 설정 (기본값은 'dev')
config_dir = os.environ.get('CONFIG_DIR')

env = os.environ.get('APP_ENV', 'dev')
config_filename = os.path.join(config_dir, f"config_{env}.yaml")

with open(config_filename, 'r') as config_file:
    config = yaml.safe_load(config_file)

# logger를 설정합니다.
log_file_path = config['log']['path']
logger = setup_logger(__name__, log_file_path)

if __name__ == "__main__":
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 시작 로그를 남깁니다.
    logger.info(f"Program started at {current_time}")
    logger.info(f"Environment: {env}")
    logger.info(f"Configuration file: {config_filename}")

    rabbitmq_handler = RabbitMQHandler(config['mq_server'],logger)
    rabbitmq_handler.start()

