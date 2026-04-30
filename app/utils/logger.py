"""日志工具"""
import os
import sys
from loguru import logger

# 全局标志，确保日志配置只执行一次
_logger_configured = False

def _setup_console_encoding():
    """设置控制台编码，解决Windows中文乱码问题"""
    if sys.platform.startswith('win'):
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8
            kernel32.SetConsoleCP(65001)  # UTF-8
        except Exception:
            pass

def get_logger(name: str = __name__):
    """
    获取日志记录器
    :param name: 日志名称
    :return: 日志记录器
    """
    global _logger_configured
    
    # 只配置一次
    if not _logger_configured:
        # 设置控制台编码
        _setup_console_encoding()
        
        # 确保日志目录存在
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置控制台输出
        logger.remove()  # 移除默认处理器
        logger.add(
            sys.stdout,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} - {message}"
        )
        
        # 配置文件输出
        logger.add(
            os.path.join(log_dir, 'app.log'),
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} - {message}",
            encoding="utf-8"
        )
        
        _logger_configured = True
    
    return logger