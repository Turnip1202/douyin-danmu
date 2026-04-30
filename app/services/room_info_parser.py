"""房间信息解析器 - 从抖音直播页面提取房间信息"""
from playwright.sync_api import sync_playwright
import re
import json
from typing import Dict, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RoomInfoParser:
    """抖音房间信息解析器"""
    
    def __init__(self):
        pass
    
    def fetch_html(self, room_id: str) -> Optional[str]:
        """使用Playwright获取抖音直播间动态渲染的HTML页面"""
        url = f"https://live.douyin.com/{room_id}"
        
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 访问页面（不等待networkidle，抖音永远不会idle）
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            # 等待页面渲染完成
            page.wait_for_timeout(5000)

            # ✅ 关键：强制获取渲染后的完整DOM HTML
            full_html = page.evaluate("document.documentElement.outerHTML")

            browser.close()
            return full_html
    
    def parse_room_info(self, html):
        """从HTML中解析房间名称和主播名称"""
        room_info = {}
        
        # 1. 从title标签提取房间信息
        title_match = re.search(r'<title>(.*?)</title>', html)
        if title_match:
            title = title_match.group(1)
            # 格式："麦小兜的抖音直播间 - 抖音直播"
            if '的抖音直播间' in title:
                host_name = title.split('的抖音直播间')[0]
                room_name = title.replace(' - 抖音直播', '')
                room_info['host_name'] = host_name
                room_info['room_name'] = room_name
        
        # 2. 从meta description提取
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
        if desc_match:
            desc = desc_match.group(1)
            # 格式："欢迎来到麦小兜的抖音直播间，麦小兜与大家一起记录美好生活 - 抖音直播"
            if '欢迎来到' in desc and '的抖音直播间' in desc:
                start_idx = desc.find('欢迎来到') + 4
                end_idx = desc.find('的抖音直播间')
                host_name_from_desc = desc[start_idx:end_idx]
                room_info['host_name'] = host_name_from_desc
        
        # 3. 从meta keywords提取
        keywords_match = re.search(r'<meta name="keywords" content="([^"]+)"', html)
        if keywords_match:
            keywords = keywords_match.group(1)
            # 格式："麦小兜,麦小兜直播,麦小兜抖音,麦小兜直播间..."
            first_keyword = keywords.split(',')[0]
            if 'host_name' not in room_info:
                room_info['host_name'] = first_keyword
        
        # 4. 从JSON数据提取更多信息
        self._parse_json_data(html, room_info)
        
        return room_info
    
    def _parse_json_data(self, html: str, result: Dict):
        """从页面的JSON数据中提取更多信息"""
        # 模式1: window.__initialState__
        state_match = re.search(r'window\.__initialState__\s*=\s*({.*?});', html, re.DOTALL)
        if state_match:
            try:
                data = json.loads(state_match.group(1))
                self._extract_from_json_data(data, result)
            except Exception as e:
                logger.debug(f"解析initialState失败: {str(e)}")
        
        # 模式2: window.__pageData__
        page_data_match = re.search(r'window\.__pageData__\s*=\s*({.*?});', html, re.DOTALL)
        if page_data_match:
            try:
                data = json.loads(page_data_match.group(1))
                self._extract_from_json_data(data, result)
            except Exception as e:
                logger.debug(f"解析pageData失败: {str(e)}")
    
    def _extract_from_json_data(self, data: Dict, result: Dict):
        """从JSON数据中提取房间信息"""
        paths = [
            data,
            data.get('room'),
            data.get('store', {}).get('room'),
            data.get('store', {}).get('roomInfo'),
            data.get('roomInfo'),
        ]
        
        for room_data in paths:
            if not isinstance(room_data, dict):
                continue
                
            if 'room_name' in room_data:
                result['room_name'] = room_data['room_name']
            elif 'title' in room_data:
                result['room_name'] = room_data['title']
            
            if 'anchor_name' in room_data:
                result['host_name'] = room_data['anchor_name']
            elif 'host_name' in room_data:
                result['host_name'] = room_data['host_name']
            elif 'nickname' in room_data:
                result['host_name'] = room_data['nickname']
            
            if 'room_id' in room_data:
                result['room_id'] = str(room_data['room_id'])
            if 'short_id' in room_data:
                result['short_id'] = str(room_data['short_id'])
            if 'anchor_id' in room_data:
                result['host_id'] = str(room_data['anchor_id'])
            elif 'host_id' in room_data:
                result['host_id'] = str(room_data['host_id'])
    
    def get_room_info(self, room_id: str) -> Optional[Dict]:
        """获取房间信息主方法"""
        try:
            html = self.fetch_html(room_id)
            if not html:
                logger.error(f"获取HTML失败: {room_id}")
                return None
            
            result = self.parse_room_info(html)
            result['short_id'] = result.get('short_id', room_id)
            
            if result.get('host_name') or result.get('room_name'):
                logger.info(f"解析房间信息成功: room_id={room_id}, host_name={result['host_name']}, room_name={result['room_name']}")
                return result
            else:
                logger.warning(f"未能解析到房间信息: {room_id}")
                return None
        except Exception as e:
            logger.error(f"获取房间信息异常: {str(e)}")
            return None

# 单例模式
_room_parser = None

def get_room_parser() -> RoomInfoParser:
    """获取房间解析器实例"""
    global _room_parser
    if _room_parser is None:
        _room_parser = RoomInfoParser()
    return _room_parser