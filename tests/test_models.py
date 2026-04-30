"""数据模型测试"""
import pytest
from datetime import datetime
from app.models import Room, Danmu, Like, User
from app.config.database import DatabaseConfig

class TestRoomModel:
    """房间模型测试"""
    
    def test_create_room(self):
        """测试创建房间"""
        db = DatabaseConfig.get_session()
        try:
            room = Room(room_id='test_room_1', room_name='测试房间', host_name='测试主播')
            db.add(room)
            db.commit()
            
            retrieved = db.query(Room).filter_by(room_id='test_room_1').first()
            assert retrieved is not None
            assert retrieved.room_name == '测试房间'
            assert retrieved.host_name == '测试主播'
            assert retrieved.status == 0
        finally:
            db.query(Room).filter_by(room_id='test_room_1').delete()
            db.commit()
            db.close()
    
    def test_room_to_dict(self):
        """测试房间转字典"""
        room = Room(
            room_id='test_room_2',
            room_name='测试房间',
            host_name='测试主播',
            status=1
        )
        result = room.to_dict()
        assert 'room_id' in result
        assert 'room_name' in result
        assert 'status' in result
        assert result['room_id'] == 'test_room_2'

class TestDanmuModel:
    """弹幕模型测试"""
    
    def test_create_danmu(self):
        """测试创建弹幕"""
        db = DatabaseConfig.get_session()
        try:
            danmu = Danmu(
                room_id='test_room',
                user_id='user1',
                user_name='测试用户',
                content='测试弹幕内容'
            )
            db.add(danmu)
            db.commit()
            
            retrieved = db.query(Danmu).filter_by(user_id='user1').first()
            assert retrieved is not None
            assert retrieved.content == '测试弹幕内容'
        finally:
            db.query(Danmu).filter_by(user_id='user1').delete()
            db.commit()
            db.close()

class TestUserModel:
    """用户模型测试"""
    
    def test_create_user(self):
        """测试创建用户"""
        db = DatabaseConfig.get_session()
        try:
            user = User(user_id='test_user', user_name='测试用户')
            db.add(user)
            db.commit()
            
            retrieved = db.query(User).filter_by(user_id='test_user').first()
            assert retrieved is not None
            assert retrieved.user_name == '测试用户'
        finally:
            db.query(User).filter_by(user_id='test_user').delete()
            db.commit()
            db.close()