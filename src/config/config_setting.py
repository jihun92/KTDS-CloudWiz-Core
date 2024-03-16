import os
import yaml

class ConfigSetting:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigSetting, cls).__new__(cls)
        return cls._instance

    def __init__(self):

        self.env = None
        self.config_filename = None
        self.config_value = None

        # 환경 변수로 환경 설정 (기본값은 'dev')
        config_dir = os.environ.get('CONFIG_DIR')
        self.env = os.environ.get('APP_ENV', 'dev')
        self.config_filename = os.path.join(config_dir, f"config_{self.env}.yaml")

        with open(self.config_filename, 'r') as config_file:
            self.config_value = yaml.safe_load(config_file)

    def get_config_config_value(self):
        return self.config_value
    
    def get_log_path(self):
        return self.config_value['log']['path']
    
    def get_os_env(self):
        return self.env
    
    def get_config_filename(self):
        return self.config_filename
    
    def get_mq_server_info(self):
        return self.config_value['mq_server']