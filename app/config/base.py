"""基础配置类"""
import os

class BaseConfig:
    # 应用配置
    APP_NAME = "douyin-danmu"
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    DB_TYPE = "sqlite"
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'danmu.db')
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'app.log')
    
    # 抖音API配置
    DOUBYIN_BASE_URL = "https://live.douyin.com"
    DOUBYIN_WSS_URL = "wss://webcast100-ws-web-hl.douyin.com"
    
    # 签名配置
    SIGN_JS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'js', 'sign.js')
    
    # 缓存配置
    CACHE_TIMEOUT = 3600
    
    # Web服务器配置
    HOST = "0.0.0.0"
    PORT = 5000