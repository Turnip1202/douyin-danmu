"""统计API接口"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.config.database import DatabaseConfig
from app.repositories.danmu_repo import DanmuRepository
from app.repositories.like_repo import LikeRepository

stats_bp = Blueprint('stats', __name__, url_prefix='/api/v1/stats')

@stats_bp.route('/danmu/<room_id>', methods=['GET'])
def get_danmu_stats(room_id):
    """获取弹幕统计"""
    try:
        db = DatabaseConfig.get_session()
        repo = DanmuRepository(db)
        
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            danmus = repo.get_by_time_range(room_id, start_dt, end_dt)
            count = len(danmus)
        else:
            count = repo.count_by_room(room_id)
        
        # 获取活跃用户
        hot_users = repo.get_hot_users(room_id, limit=10)
        hot_users_list = [{'user_id': h[0], 'user_name': h[1], 'danmu_count': h[2]} for h in hot_users]
        
        # 获取小时统计
        hourly_stats = repo.get_hourly_stats(room_id)
        hourly_list = [{'hour': h[0], 'count': h[1]} for h in hourly_stats]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total_danmus': count,
                'hot_users': hot_users_list,
                'hourly_stats': hourly_list
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@stats_bp.route('/like/<room_id>', methods=['GET'])
def get_like_stats(room_id):
    """获取点赞统计"""
    try:
        db = DatabaseConfig.get_session()
        repo = LikeRepository(db)
        
        total_likes = repo.count_by_room(room_id)
        
        # 获取活跃用户
        hot_users = repo.get_hot_users(room_id, limit=10)
        hot_users_list = [{'user_id': h[0], 'user_name': h[1], 'like_count': h[2]} for h in hot_users]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total_likes': total_likes,
                'hot_users': hot_users_list
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()

@stats_bp.route('/summary/<room_id>', methods=['GET'])
def get_summary(room_id):
    """获取房间汇总统计"""
    try:
        db = DatabaseConfig.get_session()
        danmu_repo = DanmuRepository(db)
        like_repo = LikeRepository(db)
        
        summary = {
            'room_id': room_id,
            'total_danmus': danmu_repo.count_by_room(room_id),
            'total_likes': like_repo.count_by_room(room_id),
            'hot_danmu_users': [],
            'hot_like_users': []
        }
        
        # 弹幕活跃用户
        danmu_users = danmu_repo.get_hot_users(room_id, limit=5)
        summary['hot_danmu_users'] = [{'user_name': h[1], 'count': h[2]} for h in danmu_users]
        
        # 点赞活跃用户
        like_users = like_repo.get_hot_users(room_id, limit=5)
        summary['hot_like_users'] = [{'user_name': h[1], 'count': h[2]} for h in like_users]
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': summary
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None})
    finally:
        db.close()