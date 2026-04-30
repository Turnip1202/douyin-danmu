"""Web模块初始化"""
from .views import web_bp

def register_web(app):
    """注册Web视图"""
    app.register_blueprint(web_bp)