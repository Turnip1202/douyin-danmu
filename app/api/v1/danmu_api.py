"""弹幕API接口"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.config.database import DatabaseConfig
from app.repositories.danmu_repo import DanmuRepository

danmu_bp = Blueprint('danmu', __name__, url_prefix='/api/v1/danmus')

@danmu_bp.route('/', methods=['GET'])
def get_danmus():
    """查询弹幕列表"""
    try:
        db = DatabaseConfig.get_session()
        repo = DanmuRepository(db)
        
        room_id = request.args.get('room_id')
        user_id = request.args.get('user_id')
        keyword = request.args.get('keyword')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        if room_id and keyword:
            # 按房间和关键词搜索
            danmus = repo.search_by_keyword(room_id, keyword)
            total = len(danmus)
        elif room_id:
            # 按房间查询
            danmus = repo.get_by_room(room_id, limit=limit, offset=offset)
            total = repo.count_by_room(room_id)
        elif user_id:
            # 按用户查询
            danmus = repo.get_by_user(user_id, limit=limit)
            total = len(danmus)
        else:
            return jsonify({'code': 400, 'message': '缺少必要参数', 'data': None})
        
        result = [d.to_dict() for d in danmus]
        
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

@danmu_bp.route('/<int:danmu_id>', methods=['GET'])
def get_danmu(danmu_id):
    """查询单条弹幕"""
    try:
        db = DatabaseConfig.get_session()
        repo = DanmuRepository(db)
        
        # 由于我们的Repository没有get_by_id方法，需要直接查询
        danmu = db.query(repo._model_class).filter_by(id=danmu_id).first()
        
        if danmu:
            return jsonify({'code': 200, 'message': 'success', 'data': danmu.to_dict()})
        else:
            return jsonify({'code': 404, 'message': '弹幕不存在', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@danmu_bp.route('/<int:danmu_id>', methods=['DELETE'])
def delete_danmu(danmu_id):
    """删除单条弹幕"""
    try:
        db = DatabaseConfig.get_session()
        
        danmu = db.query(DanmuRepository._model_class).filter_by(id=danmu_id).first()
        if danmu:
            db.delete(danmu)
            db.commit()
            return jsonify({'code': 200, 'message': '删除成功', 'data': None})
        else:
            return jsonify({'code': 404, 'message': '弹幕不存在', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@danmu_bp.route('/room/<room_id>', methods=['DELETE'])
def delete_danmus_by_room(room_id):
    """删除房间所有弹幕"""
    try:
        db = DatabaseConfig.get_session()
        repo = DanmuRepository(db)
        
        repo.delete_by_room(room_id)
        return jsonify({'code': 200, 'message': '删除成功', 'data': None})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()