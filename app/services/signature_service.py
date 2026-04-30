"""签名服务"""
import time
from app.utils.sign_helper import generate_signature
from app.utils.crypto_helper import md5_hash
from app.utils.logger import get_logger

class SignatureService:
    """签名服务类"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.signature_cache = {}
    
    def generate_signature(self, room_id: str, sub_room_id: str, user_unique_id: str) -> str:
        """
        生成弹幕签名
        :param room_id: 房间ID
        :param sub_room_id: 子房间ID
        :param user_unique_id: 用户唯一ID
        :return: 签名字符串
        """
        try:
            # 构建签名原文
            text = f"live_id=1,aid=6383,version_code=180800,webcast_sdk_version=1.0.15,room_id={room_id},sub_room_id={sub_room_id},sub_channel_id=,did_rule=3,user_unique_id={user_unique_id},device_platform=web,device_type=,ac=,identity=audience"
            
            # 计算MD5
            md5_sign = md5_hash(text)
            self.logger.debug(f"MD5签名原文: {text}")
            self.logger.debug(f"MD5签名结果: {md5_sign}")
            
            # 生成签名
            signature = generate_signature(md5_sign)
            self.logger.info(f"签名生成成功: {signature[:30]}...")
            
            # 缓存签名
            cache_key = f"{room_id}_{user_unique_id}"
            self.signature_cache[cache_key] = {
                'signature': signature,
                'timestamp': time.time()
            }
            
            return signature
        except Exception as e:
            self.logger.error(f"签名生成失败: {e}", exc_info=True)
            raise
    
    def get_cached_signature(self, room_id: str, user_unique_id: str, timeout: int = 300) -> str:
        """
        获取缓存的签名
        :param room_id: 房间ID
        :param user_unique_id: 用户唯一ID
        :param timeout: 超时时间（秒）
        :return: 签名字符串，如果超时返回None
        """
        cache_key = f"{room_id}_{user_unique_id}"
        cached = self.signature_cache.get(cache_key)
        
        if cached:
            if time.time() - cached['timestamp'] < timeout:
                return cached['signature']
            else:
                # 超时，删除缓存
                del self.signature_cache[cache_key]
        
        return None