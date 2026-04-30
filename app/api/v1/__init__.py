"""API v1 版本初始化"""
from .danmu_api import danmu_bp
from .room_api import room_bp
from .stats_api import stats_bp

def register_apis(app):
    """注册所有API蓝图"""
    app.register_blueprint(danmu_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(stats_bp)