"""加密解密工具"""
import hashlib
import base64

def md5_hash(text: str) -> str:
    """
    计算MD5哈希值
    :param text: 输入字符串
    :return: MD5哈希值
    """
    md5_obj = hashlib.md5()
    md5_obj.update(text.encode('utf-8'))
    return md5_obj.hexdigest()

def base64_encode(text: str) -> str:
    """
    Base64编码
    :param text: 输入字符串
    :return: Base64编码结果
    """
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def base64_decode(encoded_text: str) -> str:
    """
    Base64解码
    :param encoded_text: Base64编码字符串
    :return: 解码结果
    """
    return base64.b64decode(encoded_text).decode('utf-8')

def generate_random_string(length: int = 16) -> str:
    """
    生成随机字符串
    :param length: 字符串长度
    :return: 随机字符串
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))