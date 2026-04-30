"""应用启动入口"""
import os
import sys

# ========== Windows控制台编码修复 ==========
if sys.platform.startswith('win'):
    try:
        # 使用ctypes设置控制台编码为UTF-8
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # 标准输出编码
        kernel32.SetConsoleCP(65001)        # 标准输入编码
    except Exception as e:
        pass
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    try:
        # 重新配置stdout/stderr编码
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception as e:
        pass

# 提前初始化日志配置
from app.utils.logger import get_logger
logger = get_logger(__name__)

from app import create_app
from app.config.database import DatabaseConfig

def init_database():
    """初始化数据库"""
    db = DatabaseConfig.get_session()
    try:
        # 创建所有表
        from app.models import Base
        Base.metadata.create_all(bind=db.bind)
        print("✅ 数据库表创建成功")
        
        # 重置所有房间状态为离线（应用重启后所有连接都会断开）
        from app.models import Room
        db.query(Room).update({"status": 0})
        db.commit()
        print("✅ 房间状态已重置为离线")
    finally:
        db.close()

if __name__ == '__main__':
    print("🚀 启动抖音弹幕监控系统...")
    
    # 初始化数据库
    init_database()
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 服务运行在: http://{host}:{port}")
    print(f"📊 管理界面: http://{host}:{port}/")
    print("按 Ctrl+C 停止服务")
    
    app.run(host=host, port=port, debug=True)