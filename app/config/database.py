"""数据库配置"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseConfig:
    """数据库配置类"""
    
    # SQLite数据库路径
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'danmu.db')
    
    @classmethod
    def get_engine(cls):
        """获取数据库引擎"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)
        # 创建SQLite引擎
        return create_engine(f'sqlite:///{cls.DB_PATH}', connect_args={'check_same_thread': False})
    
    @classmethod
    def get_session(cls):
        """获取数据库会话"""
        engine = cls.get_engine()
        Session = sessionmaker(bind=engine)
        return Session()
    
    @classmethod
    def init_db(cls):
        """初始化数据库表"""
        from app.models import Base
        # 确保数据目录存在
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)
        # 创建所有表
        engine = cls.get_engine()
        Base.metadata.create_all(engine)
        print(f"✅ 数据库初始化完成: {cls.DB_PATH}")