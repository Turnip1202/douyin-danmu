"""用户数据访问层"""
from sqlalchemy.orm import Session
from app.models import User
from datetime import datetime

class UserRepository:
    """用户数据访问类"""
    
    _model_class = User
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: str, user_name: str = None, avatar: str = None):
        """创建用户记录"""
        user = User(
            user_id=user_id,
            user_name=user_name,
            avatar=avatar
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_user_id(self, user_id: str):
        """按用户ID查询"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def update_last_seen(self, user_id: str):
        """更新用户最后活跃时间"""
        user = self.get_by_user_id(user_id)
        if user:
            user.last_seen = datetime.now()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update_info(self, user_id: str, **kwargs):
        """更新用户信息"""
        user = self.get_by_user_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.last_seen = datetime.now()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_all(self, limit: int = 100, offset: int = 0):
        """查询所有用户"""
        return self.db.query(User)\
            .order_by(User.last_seen.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    def exists(self, user_id: str) -> bool:
        """检查用户是否存在"""
        return self.db.query(User).filter(User.user_id == user_id).count() > 0