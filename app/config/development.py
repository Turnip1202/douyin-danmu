"""开发环境配置"""
from app.config.base import BaseConfig

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    LOG_LEVEL = "DEBUG"