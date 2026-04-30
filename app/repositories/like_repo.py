"""点赞数据访问层"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Like
from datetime import datetime

class LikeRepository:
    """点赞数据访问类"""
    
    _model_class = Like
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, room_id: str, user_id: str, user_name: str, count: int = 1, timestamp: datetime = None):
        """创建点赞记录"""
        like = Like(
            room_id=room_id,
            user_id=user_id,
            user_name=user_name,
            count=count,
            timestamp=timestamp or datetime.now()
        )
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like
    
    def create_batch(self, likes: list):
        """批量创建点赞记录"""
        self.db.add_all(likes)
        self.db.commit()
    
    def get_by_room(self, room_id: str, limit: int = 100, offset: int = 0):
        """按房间ID查询点赞"""
        return self.db.query(Like)\
            .filter(Like.room_id == room_id)\
            .order_by(Like.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    def count_by_room(self, room_id: str) -> int:
        """统计房间点赞总数"""
        result = self.db.query(func.sum(Like.count))\
            .filter(Like.room_id == room_id)\
            .scalar()
        return result or 0
    
    def delete_by_room(self, room_id: str):
        """删除房间所有点赞"""
        self.db.query(Like)\
            .filter(Like.room_id == room_id)\
            .delete()
        self.db.commit()
    
    def get_hot_users(self, room_id: str, limit: int = 10):
        """获取房间点赞活跃用户TOP N"""
        return self.db.query(
            Like.user_id,
            Like.user_name,
            func.sum(Like.count).label('like_count')
        ).filter(Like.room_id == room_id)\
         .group_by(Like.user_id, Like.user_name)\
         .order_by(func.sum(Like.count).desc())\
         .limit(limit)\
         .all()