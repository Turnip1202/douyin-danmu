"""测试房间信息解析器"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.room_info_parser import get_room_parser
import re

def test_parser():
    parser = get_room_parser()
    html = parser.fetch_html('459565028332')
    
    if html:
        print(f"HTML长度: {len(html)}")
        
        # 查找title标签
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        print('\nTitle:', title_match.group(1).strip() if title_match else 'Not found')
        
        # 查找meta描述
        desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        print('Description:', desc_match.group(1)[:200] if desc_match else 'Not found')
        
        # 查找meta keywords
        keywords_match = re.search(r'<meta[^>]+name=["\']keywords["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        print('Keywords:', keywords_match.group(1)[:200] if keywords_match else 'Not found')
        
        # 保存HTML供分析
        with open('test_room.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('\n已保存测试HTML到 test_room.html')
    else:
        print('获取HTML失败')

if __name__ == '__main__':
    test_parser()