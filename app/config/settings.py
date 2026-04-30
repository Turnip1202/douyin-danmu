"""应用设置配置"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-2024')
    
    # 数据库配置
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # 签名配置
    SIGNATURE_CACHE_TIMEOUT = 300  # 签名缓存超时时间（秒）

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'

# 根据环境变量选择配置
env = os.environ.get('FLASK_ENV', 'development')

if env == 'production':
    config = ProductionConfig()
elif env == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()