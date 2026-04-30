"""生产环境配置"""
from app.config.base import BaseConfig

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARN"