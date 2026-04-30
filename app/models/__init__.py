"""数据模型定义"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Room(Base):
    """房间信息模型"""
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), unique=True, nullable=False, index=True)  # 用户输入的短ID或URL中的ID
    long_room_id = Column(String(64))  # 抖音返回的长ID
    sub_room_id = Column(String(64))  # 子房间ID
    user_unique_id = Column(String(64))  # 用户唯一ID
    ttwid = Column(String(512))  # Cookie
    room_name = Column(String(256))
    host_name = Column(String(128))
    host_id = Column(String(64))
    status = Column(Integer, default=0)  # 0-离线, 1-在线
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义
    danmus = relationship("Danmu", back_populates="room")
    likes = relationship("Like", back_populates="room")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'long_room_id': self.long_room_id,
            'sub_room_id': self.sub_room_id,
            'user_unique_id': self.user_unique_id,
            'ttwid': self.ttwid,
            'room_name': self.room_name,
            'host_name': self.host_name,
            'host_id': self.host_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Danmu(Base):
    """弹幕数据模型"""
    __tablename__ = 'danmus'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), ForeignKey('rooms.room_id'), nullable=False, index=True)
    user_id = Column(String(64), index=True)
    user_name = Column(String(128))
    content = Column(Text)
    timestamp = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系定义
    room = relationship("Room", back_populates="danmus")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Like(Base):
    """点赞数据模型"""
    __tablename__ = 'likes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(64), ForeignKey('rooms.room_id'), nullable=False, index=True)
    user_id = Column(String(64), index=True)
    user_name = Column(String(128))
    count = Column(Integer, default=1)
    timestamp = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系定义
    room = relationship("Room", back_populates="likes")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'count': self.count,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(Base):
    """用户信息模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), unique=True, nullable=False, index=True)
    user_name = Column(String(128))
    avatar = Column(String(512))
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'avatar': self.avatar,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }