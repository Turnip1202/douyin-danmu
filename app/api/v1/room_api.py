"""房间API接口"""
from flask import Blueprint, request, jsonify
from app.config.database import DatabaseConfig
from app.repositories.room_repo import RoomRepository
from app.services.danmu_service import DanmuService

# 多房间弹幕服务实例（支持同时监听多个房间）
danmu_services = {}

room_bp = Blueprint('room', __name__, url_prefix='/api/v1/rooms')

@room_bp.route('/', methods=['GET'])
def get_rooms():
    """查询房间列表"""
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        status = request.args.get('status', type=int)
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        rooms = repo.get_all(status=status, limit=limit, offset=offset)
        total = db.query(repo._model_class).count()
        
        result = [r.to_dict() for r in rooms]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': result,
                'total': total,
                'page': page,
                'limit': limit
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@room_bp.route('/<room_id>', methods=['GET'])
def get_room(room_id):
    """查询房间详情"""
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        room = repo.get_by_room_id(room_id)
        
        if room:
            return jsonify({'code': 200, 'message': 'success', 'data': room.to_dict()})
        else:
            return jsonify({'code': 404, 'message': '房间不存在', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@room_bp.route('/info/<room_id>', methods=['GET'])
def get_room_info(room_id):
    """获取抖音房间信息（不保存到数据库）"""
    try:
        from app.services.room_info_parser import get_room_parser
        
        parser = get_room_parser()
        room_info = parser.get_room_info(room_id)
        
        if room_info:
            return jsonify({
                'code': 200, 
                'message': 'success', 
                'data': {
                    'room_id': room_info.get('short_id'),
                    'long_room_id': room_info.get('room_id'),
                    'sub_room_id': None,
                    'user_unique_id': None,
                    'room_name': room_info.get('room_name'),
                    'host_name': room_info.get('host_name'),
                    'host_id': room_info.get('host_id')
                }
            })
        else:
            return jsonify({'code': 404, 'message': '获取房间信息失败', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})

@room_bp.route('/', methods=['POST'])
def create_room():
    """添加房间"""
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        data = request.get_json()
        room_id = data.get('room_id')
        room_name = data.get('room_name')
        host_name = data.get('host_name')
        host_id = data.get('host_id')
        
        if not room_id:
            return jsonify({'code': 400, 'message': '房间ID不能为空', 'data': None})
        
        if repo.exists(room_id):
            return jsonify({'code': 409, 'message': '房间已存在', 'data': None})
        
        room = repo.create(room_id, room_name, host_name, host_id)
        
        return jsonify({'code': 201, 'message': '创建成功', 'data': room.to_dict()})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@room_bp.route('/<room_id>', methods=['PUT'])
def update_room(room_id):
    """更新房间信息"""
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        data = request.get_json()
        room = repo.get_by_room_id(room_id)
        
        if not room:
            return jsonify({'code': 404, 'message': '房间不存在', 'data': None})
        
        # 更新允许的字段
        allowed_fields = ['room_name', 'host_name', 'host_id', 'status']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_data:
            room = repo.update_info(room_id, **update_data)
        
        return jsonify({'code': 200, 'message': '更新成功', 'data': room.to_dict()})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@room_bp.route('/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    """删除房间"""
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        if repo.delete(room_id):
            return jsonify({'code': 200, 'message': '删除成功', 'data': None})
        else:
            return jsonify({'code': 404, 'message': '房间不存在', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@room_bp.route('/<room_id>/start', methods=['POST'])
def start_listening(room_id):
    """开始监听房间弹幕（支持多房间同时监听）"""
    global danmu_services
    
    try:
        # 检查是否已经在监听该房间
        if room_id in danmu_services:
            return jsonify({'code': 409, 'message': '该房间已经在监听中', 'data': {'room_id': room_id}})
        
        # 创建新的弹幕服务实例（每个房间独立）
        danmu_service = DanmuService()
        danmu_service.start_listening(room_id)
        
        # 保存服务实例
        danmu_services[room_id] = danmu_service
        
        # 更新房间状态为在线
        db = DatabaseConfig.get_session()
        try:
            repo = RoomRepository(db)
            repo.update_status(room_id, 1)
        finally:
            db.close()
        
        return jsonify({'code': 200, 'message': '开始监听成功', 'data': {'room_id': room_id}})
    except Exception as e:
        # 清理可能创建的服务实例
        if room_id in danmu_services:
            del danmu_services[room_id]
        return jsonify({'code': 500, 'message': str(e), 'data': None})

@room_bp.route('/<room_id>/stop', methods=['POST'])
def stop_listening(room_id):
    """停止监听房间弹幕"""
    global danmu_services
    
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        # 更新房间状态为离线
        repo.update_status(room_id, 0)
        
        # 停止该房间的监听服务
        if room_id in danmu_services:
            danmu_services[room_id].stop_listening()
            del danmu_services[room_id]
        
        return jsonify({'code': 200, 'message': '停止监听成功', 'data': {'room_id': room_id}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()