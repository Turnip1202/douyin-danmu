"""API测试"""
import pytest
from app import create_app
from app.config.database import DatabaseConfig
from app.models import Base

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db = DatabaseConfig.get_session()
        Base.metadata.drop_all(bind=db.bind)
        Base.metadata.create_all(bind=db.bind)
        yield app
        db.close()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

class TestRoomAPI:
    """房间API测试"""
    
    def test_get_rooms(self, client):
        """测试获取房间列表"""
        response = client.get('/api/v1/rooms/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
    
    def test_create_room(self, client):
        """测试创建房间"""
        response = client.post(
            '/api/v1/rooms/',
            json={'room_id': 'test_api_room', 'room_name': 'API测试房间'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 201
        assert data['data']['room_id'] == 'test_api_room'
    
    def test_create_duplicate_room(self, client):
        """测试创建重复房间"""
        client.post(
            '/api/v1/rooms/',
            json={'room_id': 'duplicate_room', 'room_name': '重复房间'}
        )
        response = client.post(
            '/api/v1/rooms/',
            json={'room_id': 'duplicate_room', 'room_name': '重复房间'}
        )
        data = response.get_json()
        assert data['code'] == 409

class TestDanmuAPI:
    """弹幕API测试"""
    
    def test_get_danmus(self, client):
        """测试获取弹幕列表"""
        response = client.get('/api/v1/danmus/?room_id=test')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200