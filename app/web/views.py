"""Web视图函数"""
from flask import Blueprint, render_template, jsonify, request
from app.config.database import DatabaseConfig
from app.repositories.room_repo import RoomRepository
from app.repositories.danmu_repo import DanmuRepository
from app.services.danmu_service import DanmuService

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """首页仪表盘"""
    return render_template('index.html')

@web_bp.route('/rooms')
def rooms():
    """房间管理页面"""
    return render_template('rooms.html')

@web_bp.route('/danmus')
@web_bp.route('/danmus/<room_id>')
def danmus(room_id=None):
    """弹幕查看页面"""
    # 如果没有指定房间ID，获取第一个房间
    if not room_id:
        db = DatabaseConfig.get_session()
        try:
            repo = RoomRepository(db)
            rooms = repo.get_all()
            if rooms:
                room_id = rooms[0].room_id
            else:
                room_id = '0'
        finally:
            db.close()
    return render_template('danmus.html', room_id=room_id)

@web_bp.route('/stats')
@web_bp.route('/stats/<room_id>')
def stats(room_id=None):
    """统计分析页面"""
    # 如果没有指定房间ID，获取第一个房间
    if not room_id:
        db = DatabaseConfig.get_session()
        try:
            repo = RoomRepository(db)
            rooms = repo.get_all()
            if rooms:
                room_id = rooms[0].room_id
            else:
                room_id = '0'
        finally:
            db.close()
    return render_template('stats.html', room_id=room_id)

@web_bp.route('/api/rooms', methods=['GET'])
def api_rooms():
    """获取房间列表（供前端使用）"""
    try:
        db = DatabaseConfig.get_session()
        repo = RoomRepository(db)
        
        status = request.args.get('status', type=int)
        rooms = repo.get_all(status=status)
        result = [r.to_dict() for r in rooms]
        
        return jsonify({'code': 200, 'message': 'success', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@web_bp.route('/api/danmus/<room_id>', methods=['GET'])
def api_danmus(room_id):
    """获取房间弹幕（供前端使用）"""
    try:
        db = DatabaseConfig.get_session()
        repo = DanmuRepository(db)
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        keyword = request.args.get('keyword', '').strip()
        
        if keyword:
            # 按关键词搜索
            danmus = repo.search_by_keyword(room_id, keyword)
            total = len(danmus)
            # 手动分页
            danmus = danmus[offset:offset + limit]
        else:
            # 普通分页查询
            danmus = repo.get_by_room(room_id, limit=limit, offset=offset)
            total = repo.count_by_room(room_id)
        
        result = [d.to_dict() for d in danmus]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'items': result,
                'total': total
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()