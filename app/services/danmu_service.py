"""弹幕监听服务"""
import websocket
import threading
import time
import zlib
import json
import ssl
import re
import requests
import hashlib
from datetime import datetime
from app.services.signature_service import SignatureService
from app.services.message_processor import MessageProcessor
from app.repositories.room_repo import RoomRepository
from app.utils.logger import get_logger

# 导入protobuf
try:
    from app.services.douyin_pb2 import PushFrame, Message, Response, ChatMessage, LikeMessage, User
except ImportError:
    from douyin_pb2 import PushFrame, Message, Response, ChatMessage, LikeMessage, User

class DanmuService:
    """弹幕监听服务类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        # 使用独立的Session，避免与其他请求共享
        from app.config.database import DatabaseConfig
        self.db_session = DatabaseConfig.get_session()
        self.signature_service = SignatureService()
        self.message_processor = MessageProcessor(self.db_session)
        self.room_repo = RoomRepository(self.db_session)
        self.ws = None
        self.running = False
        self.short_room_id = None  # 用户输入的短ID
        self.room_id = None        # 实际的长ID
        self.sub_room_id = None
        self.user_unique_id = None
        self.ttwid = None
    
    def __del__(self):
        """析构函数：关闭Session"""
        if hasattr(self, 'db_session') and self.db_session:
            try:
                self.db_session.close()
            except:
                pass
    
    def _get_room_info(self, room_url_or_id):
        """
        获取房间信息
        :param room_url_or_id: 房间URL或房间ID
        :return: (short_id, room_id, sub_room_id, user_unique_id, ttwid)
        """
        if room_url_or_id.startswith('http'):
            url = room_url_or_id
            # 从URL提取短ID
            match = re.search(r'live\.douyin\.com/(\d+)', url)
            short_id = match.group(1) if match else room_url_or_id
        else:
            url = f"https://live.douyin.com/{room_url_or_id}"
            short_id = room_url_or_id
        
        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
            "sec-ch-ua": '"Microsoft Edge";v="147", "Not=A?Brand";v="8", "Chromium";v="147"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.douyin.com/"
        }
        cookies = {
            "__ac_nonce": "06723018d00888333ca1b"
        }
        
        try:
            res = requests.get(url, headers=headers, cookies=cookies)
            
            # 提取 room_id（长ID）
            match_list = re.findall(r'"roomId\\":\\"(\d+)\\",', res.text)
            if not match_list:
                match_list = re.findall(r'"room_id":(\d+)', res.text)
            room_id = match_list[0] if match_list else short_id
            
            # 提取 sub_room_id
            sub_room_match = re.findall(r'"sub_room_id":(\d+)', res.text)
            sub_room_id = sub_room_match[0] if sub_room_match else room_id
            
            # 提取 user_unique_id
            user_unique_match = re.findall(r'"user_unique_id":"?(\d+)"?', res.text)
            if not user_unique_match:
                user_unique_match = re.findall(r'"webcast_user_id":"?(\d+)"?', res.text)
            user_unique_id = user_unique_match[0] if user_unique_match else "7621938952584791552"
            
            # 提取 ttwid
            ttwid = res.cookies.get_dict().get('ttwid', '')
            if not ttwid:
                ttwid_match = re.findall(r'ttwid=([^;]+)', res.text)
                ttwid = ttwid_match[0] if ttwid_match else ''
            
            self.logger.info(f"获取房间信息成功: short_id={short_id}, room_id={room_id}, sub_room_id={sub_room_id}, user_unique_id={user_unique_id}")
            
            return short_id, room_id, sub_room_id, user_unique_id, ttwid
        except Exception as e:
            self.logger.error(f"获取房间信息失败: {e}")
            return room_url_or_id, room_url_or_id, room_url_or_id, "7621938952584791552", ""
    
    def start_listening(self, short_room_id: str):
        """
        开始监听弹幕
        :param short_room_id: 用户输入的短房间ID或完整URL
        """
        # 获取房间信息
        short_id, room_id, sub_room_id, user_unique_id, ttwid = self._get_room_info(short_room_id)
        
        self.short_room_id = short_id
        self.room_id = room_id
        self.sub_room_id = sub_room_id
        self.user_unique_id = user_unique_id
        self.ttwid = ttwid
        self.running = True
        
        # 确保房间存在（使用用户输入的短ID）
        if not self.room_repo.exists(short_id):
            self.room_repo.create(short_id, long_room_id=room_id, sub_room_id=sub_room_id, 
                                  user_unique_id=user_unique_id, ttwid=ttwid)
        else:
            # 更新房间信息（存储抖音返回的参数）
            self.room_repo.update_info(short_id, long_room_id=room_id, sub_room_id=sub_room_id, 
                                       user_unique_id=user_unique_id, ttwid=ttwid)
        
        # 更新房间状态为在线
        self.room_repo.update_status(short_id, 1)
        
        # 启动监听线程
        threading.Thread(target=self._listen, daemon=True).start()
        self.logger.info(f"开始监听房间: {short_id} (实际ID: {room_id})")
    
    def stop_listening(self):
        """停止监听"""
        self.running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                self.logger.warning(f"关闭WebSocket失败: {e}")
        
        # 更新房间状态为离线（使用用户输入的短ID）
        if self.short_room_id:
            self.room_repo.update_status(self.short_room_id, 0)
        
        self.logger.info(f"停止监听房间: {self.short_room_id}")
    
    def _listen(self):
        """WebSocket监听循环"""
        reconnect_count = 0
        max_reconnect = 20
        last_refresh_time = 0
        refresh_interval = 300  # 每5分钟刷新一次房间信息和签名
        
        while self.running and reconnect_count < max_reconnect:
            try:
                # 定期刷新房间信息和签名（防止过期）
                current_time = time.time()
                if current_time - last_refresh_time > refresh_interval:
                    self.logger.info("刷新房间信息和签名...")
                    short_id, room_id, sub_room_id, user_unique_id, ttwid = self._get_room_info(self.short_room_id)
                    self.room_id = room_id
                    self.sub_room_id = sub_room_id
                    self.user_unique_id = user_unique_id
                    self.ttwid = ttwid
                    last_refresh_time = current_time
                
                # 获取签名（使用实际的长ID）
                signature = self.signature_service.generate_signature(
                    self.room_id,
                    self.sub_room_id,
                    self.user_unique_id
                )
                
                # 构建WebSocket URL
                fetch_time = int(time.time() * 1000)
                wss_url = f'wss://webcast100-ws-web-hl.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.0.15&update_version_code=1.0.15&compress=gzip&device_platform=web&cookie_enabled=true&screen_width=1707&screen_height=960&browser_language=zh-CN&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/147.0.0.0%20Safari/537.36%20Edg/147.0.0.0&browser_online=true&tz_name=Etc/GMT-8&cursor=&internal_ext=internal_src:dim|wss_push_room_id:{self.room_id}|wss_push_did:{self.user_unique_id}|fetch_time:{fetch_time}|seq:1|wss_info:0-0-0-0&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1&user_unique_id={self.user_unique_id}&im_path=/webcast/im/fetch/&identity=audience&need_persist_msg_count=0&insert_task_id=&live_reason=&room_id={self.room_id}&sub_room_id={self.sub_room_id}&heartbeatDuration=0&signature={signature}'
                
                self.logger.debug(f"WebSocket URL: {wss_url[:100]}...")
                
                # 创建WebSocket连接
                self.ws = websocket.WebSocketApp(
                    wss_url,
                    header={
                        "Upgrade": "websocket",
                        "Origin": "https://live.douyin.com",
                        "Cache-Control": "no-cache",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Pragma": "no-cache",
                        "Connection": "Upgrade",
                        "Sec-WebSocket-Key": "uVxBjCAGqrBEcOx8mdtmeg==",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
                        "Sec-WebSocket-Version": "13",
                        "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
                    },
                    cookie=f"ttwid={self.ttwid}",
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                
                # 运行WebSocket（优化心跳参数）
                self.ws.run_forever(
                    sslopt={"cert_reqs": ssl.CERT_NONE},
                    ping_interval=30,      # 每30秒发送心跳
                    ping_timeout=10,       # 10秒无响应断开
                    ping_payload="ping"    # 添加心跳内容
                )
                
            except Exception as e:
                reconnect_count += 1
                # 指数退避，首次快速重试，之后逐渐增加间隔
                wait_time = min(2 ** (reconnect_count - 1), 60)
                self.logger.error(f"监听异常 ({reconnect_count}/{max_reconnect}): {e}")
                self.logger.info(f"等待 {wait_time} 秒后重连...")
                time.sleep(wait_time)
        
        if reconnect_count >= max_reconnect:
            self.logger.error("达到最大重连次数，停止监听")
            self.stop_listening()
    
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        self.logger.info(f"WebSocket连接成功: {self.short_room_id}")
    
    def _on_message(self, ws, message):
        """WebSocket消息回调"""
        try:
            # 先尝试解析protobuf
            frame = PushFrame()
            frame.ParseFromString(message)
            
            # 尝试解压数据（可能是gzip或原始数据）
            try:
                # 方法1: gzip解压
                result = zlib.decompress(frame.payload, 16 + zlib.MAX_WBITS)
            except Exception:
                try:
                    # 方法2: 普通解压
                    result = zlib.decompress(frame.payload)
                except Exception:
                    # 方法3: 不压缩
                    result = frame.payload
            
            # 解析响应
            res = Response()
            res.ParseFromString(result)
            
            # 需要ack的消息
            if res.need_ack:
                s = PushFrame()
                s.payload_type = 'ack'
                s.payload = res.internal_ext.encode('utf-8')
                s.LogID = frame.LogID
                ws.send(s.SerializeToString())
            
            # 处理消息
            for item in res.messages:
                if item.method == 'WebcastChatMessage':
                    # 解析弹幕信息
                    chat_message = ChatMessage()
                    chat_message.ParseFromString(item.payload)
                    info = f"【{chat_message.user.nickName}】发出弹幕：{chat_message.content}"
                    self.logger.info(info)
                    
                    # 保存到数据库（使用用户输入的短ID）
                    self.message_processor.save_danmu(
                        room_id=self.short_room_id,
                        user_id=str(chat_message.user.id),
                        user_name=chat_message.user.nickName,
                        content=chat_message.content,
                        timestamp=datetime.now()
                    )
                
                elif item.method == 'WebcastLikeMessage':
                    # 解析点赞信息
                    like_message = LikeMessage()
                    like_message.ParseFromString(item.payload)
                    self.logger.info(f"点赞: {like_message.user.nickName}给主播点了 {like_message.count} 次赞")

                    # 保存点赞到数据库
                    self.message_processor.save_like(
                        room_id=self.short_room_id,
                        user_id=str(like_message.user.id),
                        user_name=like_message.user.nickName,
                        count=like_message.count,
                        timestamp=datetime.now()
                    )
            
        except Exception as e:
            self.logger.error(f"消息处理失败: {e}", exc_info=True)
    
    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        self.logger.error(f"WebSocket错误: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭回调"""
        self.logger.info(f"WebSocket关闭: {close_status_code} - {close_msg}")
        if self.running:
            self.logger.info("尝试重新连接...")
