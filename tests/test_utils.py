"""工具函数测试"""
import pytest
from app.utils.crypto_helper import md5_hash, generate_random_string
from app.utils.validator import validate_room_id, validate_user_id

class TestCryptoHelper:
    """加密工具测试"""
    
    def test_md5_hash(self):
        """测试MD5哈希"""
        result = md5_hash('test')
        assert len(result) == 32
        assert result == '098f6bcd4621d373cade4e832627b4f6'
    
    def test_generate_random_string(self):
        """测试随机字符串生成"""
        result = generate_random_string(16)
        assert len(result) == 16
        assert result.isalnum()

class TestValidator:
    """验证工具测试"""
    
    def test_validate_room_id(self):
        """测试房间ID验证"""
        assert validate_room_id('123456789') is True
        assert validate_room_id('abc123') is True
        assert validate_room_id('') is False
        assert validate_room_id(None) is False
    
    def test_validate_user_id(self):
        """测试用户ID验证"""
        assert validate_user_id('user123') is True
        assert validate_user_id('u_abc_123') is True
        assert validate_user_id('') is False