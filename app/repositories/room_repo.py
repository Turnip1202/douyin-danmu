"""房间数据访问层"""
from sqlalchemy.orm import Session
from app.models import Room
from datetime import datetime

class RoomRepository:
    """房间数据访问类"""
    
    _model_class = Room
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, room_id: str, room_name: str = None, host_name: str = None, host_id: str = None, 
                long_room_id: str = None, sub_room_id: str = None, user_unique_id: str = None, ttwid: str = None):
        """创建房间记录"""
        room = Room(
            room_id=room_id,
            room_name=room_name,
            host_name=host_name,
            host_id=host_id,
            long_room_id=long_room_id,
            sub_room_id=sub_room_id,
            user_unique_id=user_unique_id,
            ttwid=ttwid,
            status=0  # 默认离线，点击开始监听后变为在线
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room
    
    def get_by_room_id(self, room_id: str):
        """按房间ID查询"""
        return self.db.query(Room).filter(Room.room_id == room_id).first()
    
    def get_all(self, status: int = None, limit: int = 100, offset: int = 0):
        """查询所有房间"""
        query = self.db.query(Room)
        if status is not None:
            query = query.filter(Room.status == status)
        return query.order_by(Room.created_at.desc()).offset(offset).limit(limit).all()
    
    def update_status(self, room_id: str, status: int):
        """更新房间状态"""
        room = self.get_by_room_id(room_id)
        if room:
            room.status = status
            room.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(room)
        return room
    
    def update_info(self, room_id: str, **kwargs):
        """更新房间信息"""
        room = self.get_by_room_id(room_id)
        if room:
            for key, value in kwargs.items():
                if hasattr(room, key):
                    setattr(room, key, value)
            room.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(room)
        return room
    
    def delete(self, room_id: str):
        """删除房间（同时删除关联的弹幕和点赞记录）"""
        room = self.get_by_room_id(room_id)
        if room:
            # 先删除关联的弹幕记录
            from app.models import Danmu, Like
            self.db.query(Danmu).filter(Danmu.room_id == room_id).delete()
            self.db.query(Like).filter(Like.room_id == room_id).delete()
            # 再删除房间
            self.db.delete(room)
            self.db.commit()
            return True
        return False
    
    def exists(self, room_id: str) -> bool:
        """检查房间是否存在"""
        return self.db.query(Room).filter(Room.room_id == room_id).count() > 0