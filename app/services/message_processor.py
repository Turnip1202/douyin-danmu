"""消息处理服务"""
import json
from datetime import datetime
from app.models import Danmu, Like
from app.repositories.danmu_repo import DanmuRepository
from app.repositories.like_repo import LikeRepository
from app.repositories.user_repo import UserRepository
from app.utils.logger import get_logger

class MessageProcessor:
    """消息处理服务类"""

    def __init__(self, db_session):
        self.logger = get_logger(__name__)
        self.danmu_repo = DanmuRepository(db_session)
        self.like_repo = LikeRepository(db_session)
        self.user_repo = UserRepository(db_session)

    def process_message(self, message_data):
        """
        处理收到的消息
        :param message_data: 消息数据（字节或字符串）
        """
        try:
            # 解析消息
            if isinstance(message_data, bytes):
                message_data = message_data.decode('utf-8')

            # 尝试解析为JSON
            try:
                message = json.loads(message_data)
            except json.JSONDecodeError:
                self.logger.debug(f"非JSON消息: {message_data[:100]}")
                return

            # 根据消息类型处理
            if 'type' in message:
                message_type = message['type']

                if message_type == 'danmu':
                    self.process_danmu(message)
                elif message_type == 'like':
                    self.process_like(message)
                else:
                    self.logger.debug(f"未知消息类型: {message_type}")
            else:
                # 尝试其他消息格式
                self._process_raw_message(message)

        except Exception as e:
            self.logger.error(f"消息处理失败: {e}", exc_info=True)

    def process_danmu(self, message):
        """
        处理弹幕消息
        :param message: 弹幕消息字典
        """
        try:
            room_id = message.get('room_id')
            user_id = message.get('user_id')
            user_name = message.get('user_name')
            content = message.get('content')
            timestamp = message.get('timestamp') or datetime.now()

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            # 保存弹幕
            self.danmu_repo.create(
                room_id=room_id,
                user_id=user_id,
                user_name=user_name,
                content=content,
                timestamp=timestamp
            )

            # 更新用户信息
            self._update_user(user_id, user_name)

            self.logger.info(f"【{user_name}】发出弹幕：{content}")

        except Exception as e:
            self.logger.error(f"弹幕处理失败: {e}", exc_info=True)

    def process_like(self, message):
        """
        处理点赞消息
        :param message: 点赞消息字典
        """
        try:
            room_id = message.get('room_id')
            user_id = message.get('user_id')
            user_name = message.get('user_name')
            count = message.get('count', 1)
            timestamp = message.get('timestamp') or datetime.now()

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            # 保存点赞
            self.like_repo.create(
                room_id=room_id,
                user_id=user_id,
                user_name=user_name,
                count=count,
                timestamp=timestamp
            )

            # 更新用户信息
            self._update_user(user_id, user_name)

            self.logger.info(f"点赞: {user_name}给主播点了 {count} 次赞")

        except Exception as e:
            self.logger.error(f"点赞处理失败: {e}", exc_info=True)

    def _process_raw_message(self, message):
        """
        处理原始消息格式
        :param message: 原始消息数据
        """
        # 这里可以扩展处理抖音原始协议格式
        self.logger.debug(f"原始消息: {json.dumps(message)[:200]}")

    def save_danmu(self, room_id, user_id, user_name, content, timestamp=None):
        """
        保存弹幕到数据库
        :param room_id: 房间ID
        :param user_id: 用户ID
        :param user_name: 用户昵称
        :param content: 弹幕内容
        :param timestamp: 时间戳
        """
        try:
            if not timestamp:
                timestamp = datetime.now()

            # 保存弹幕
            self.danmu_repo.create(
                room_id=room_id,
                user_id=user_id,
                user_name=user_name,
                content=content,
                timestamp=timestamp
            )

            # 更新用户信息
            self._update_user(user_id, user_name)

        except Exception as e:
            self.logger.error(f"弹幕保存失败: {e}", exc_info=True)

    def save_like(self, room_id, user_id, user_name, count=1, timestamp=None):
        """
        保存点赞到数据库
        :param room_id: 房间ID
        :param user_id: 用户ID
        :param user_name: 用户昵称
        :param count: 点赞次数
        :param timestamp: 时间戳
        """
        try:
            if not timestamp:
                timestamp = datetime.now()

            # 保存点赞
            self.like_repo.create(
                room_id=room_id,
                user_id=user_id,
                user_name=user_name,
                count=count,
                timestamp=timestamp
            )

            # 更新用户信息
            self._update_user(user_id, user_name)

        except Exception as e:
            self.logger.error(f"点赞保存失败: {e}", exc_info=True)

    def _update_user(self, user_id, user_name):
        """
        更新用户信息（使用 get_or_create 模式避免并发冲突）
        :param user_id: 用户ID
        :param user_name: 用户昵称
        """
        try:
            if not user_id:
                return

            existing_user = self.user_repo.get_by_user_id(user_id)
            if existing_user:
                self.user_repo.update_info(user_id, user_name=user_name)
            else:
                try:
                    self.user_repo.create(user_id, user_name)
                except Exception:
                    self.user_repo.update_info(user_id, user_name=user_name)

        except Exception as e:
            self.logger.warning(f"用户更新失败: {e}")