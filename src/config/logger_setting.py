# logger_setting.py
import logging
from logging.handlers import TimedRotatingFileHandler
from config.config_setting import ConfigSetting

class Logger:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._logger = logging.getLogger(__name__)

           # logger를 설정합니다.
            configSetting = ConfigSetting()
            cls._instance._logger.setLevel(logging.INFO)
            log_file_path = configSetting.get_log_path()
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            file_handler.suffix = "%Y-%m-%d"

            cls._instance._logger.addHandler(console_handler)
            cls._instance._logger.addHandler(file_handler)

        return cls._instance._logger
        # return cls._instance

    # def get_logger(self):
        # return self._logger