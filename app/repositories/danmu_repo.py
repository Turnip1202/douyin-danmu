"""弹幕数据访问层"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Danmu, Room
from datetime import datetime

class DanmuRepository:
    """弹幕数据访问类"""
    
    _model_class = Danmu
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, room_id: str, user_id: str, user_name: str, content: str, timestamp: datetime):
        """创建弹幕记录"""
        danmu = Danmu(
            room_id=room_id,
            user_id=user_id,
            user_name=user_name,
            content=content,
            timestamp=timestamp
        )
        self.db.add(danmu)
        self.db.commit()
        self.db.refresh(danmu)
        return danmu
    
    def create_batch(self, danmus: list):
        """批量创建弹幕记录"""
        self.db.add_all(danmus)
        self.db.commit()
    
    def get_by_room(self, room_id: str, limit: int = 100, offset: int = 0):
        """按房间ID分页查询弹幕"""
        return self.db.query(Danmu)\
            .filter(Danmu.room_id == room_id)\
            .order_by(Danmu.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    def get_by_user(self, user_id: str, limit: int = 50):
        """按用户ID查询弹幕"""
        return self.db.query(Danmu)\
            .filter(Danmu.user_id == user_id)\
            .order_by(Danmu.timestamp.desc())\
            .limit(limit)\
            .all()
    
    def get_by_time_range(self, room_id: str, start_time: datetime, end_time: datetime):
        """按时间范围查询弹幕"""
        return self.db.query(Danmu)\
            .filter(Danmu.room_id == room_id)\
            .filter(Danmu.timestamp >= start_time)\
            .filter(Danmu.timestamp <= end_time)\
            .order_by(Danmu.timestamp.desc())\
            .all()
    
    def count_by_room(self, room_id: str) -> int:
        """统计房间弹幕数量"""
        return self.db.query(Danmu)\
            .filter(Danmu.room_id == room_id)\
            .count()
    
    def delete_by_room(self, room_id: str):
        """删除房间所有弹幕"""
        self.db.query(Danmu)\
            .filter(Danmu.room_id == room_id)\
            .delete()
        self.db.commit()
    
    def search_by_keyword(self, room_id: str, keyword: str):
        """按关键词搜索弹幕"""
        return self.db.query(Danmu)\
            .filter(Danmu.room_id == room_id)\
            .filter(Danmu.content.contains(keyword))\
            .order_by(Danmu.timestamp.desc())\
            .all()
    
    def get_hot_users(self, room_id: str, limit: int = 10):
        """获取房间活跃用户TOP N"""
        return self.db.query(
            Danmu.user_id,
            Danmu.user_name,
            func.count(Danmu.id).label('danmu_count')
        ).filter(Danmu.room_id == room_id)\
         .group_by(Danmu.user_id, Danmu.user_name)\
         .order_by(func.count(Danmu.id).desc())\
         .limit(limit)\
         .all()
    
    def get_hourly_stats(self, room_id: str):
        """获取每小时弹幕统计"""
        return self.db.query(
            func.strftime('%Y-%m-%d %H:00:00', Danmu.timestamp).label('hour'),
            func.count(Danmu.id).label('count')
        ).filter(Danmu.room_id == room_id)\
         .group_by('hour')\
         .order_by('hour')\
         .all()