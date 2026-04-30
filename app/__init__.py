"""应用初始化"""
from flask import Flask
from app.config.settings import config
from app.api.v1 import register_apis
from app.web import register_web

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
    
    # 加载配置
    app.config.from_object(config)
    
    # 注册API
    register_apis(app)
    
    # 注册Web视图
    register_web(app)
    
    return app