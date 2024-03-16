# main.py
import os
import yaml
from datetime import datetime
from config.logger_setting import Logger
from config.config_setting import ConfigSetting
from modules.rabbitmq_handler import RabbitMQHandler


if __name__ == "__main__":

    logger = Logger()
    configSetting = ConfigSetting()

    # 시작 로그를 남깁니다.
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Ansible Core App started at {current_time}")
    logger.info(f"OS Environment: {configSetting.get_os_env()}")
    logger.info(f"Configuration file: {configSetting.get_config_filename()}")

    rabbitmq_handler = RabbitMQHandler()
    rabbitmq_handler.init(configSetting.get_mq_server_info())
    rabbitmq_handler.start()