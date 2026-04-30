"""配置模块测试"""
import pytest
from app.config.settings import config, DevelopmentConfig, ProductionConfig, TestingConfig

class TestConfig:
    """配置测试类"""
    
    def test_development_config(self):
        """测试开发环境配置"""
        dev_config = DevelopmentConfig()
        assert dev_config.DEBUG is True
        assert dev_config.DATABASE_URI == 'sqlite:///dev.db'
    
    def test_production_config(self):
        """测试生产环境配置"""
        prod_config = ProductionConfig()
        assert prod_config.DEBUG is False
        assert prod_config.TESTING is False
    
    def test_testing_config(self):
        """测试测试环境配置"""
        test_config = TestingConfig()
        assert test_config.TESTING is True
        assert test_config.DATABASE_URI == 'sqlite:///:memory:'
    
    def test_current_config(self):
        """测试当前配置"""
        assert config is not None