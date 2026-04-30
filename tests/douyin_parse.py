from playwright.sync_api import sync_playwright
import re

def get_dynamic_html(url):
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 访问页面（不卡 networkidle，抖音永远不会 idle）
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        
        # 等待页面渲染完成
        page.wait_for_timeout(5000)

        # ✅ 关键：强制获取渲染后的完整 DOM HTML
        full_html = page.evaluate("document.documentElement.outerHTML")

        browser.close()
        return full_html

def parse_room_info(html):
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
        # 格式："麦小兜,麦小兜}直播,麦小兜抖音,麦小兜直播间..."
        first_keyword = keywords.split(',')[0]
        if 'host_name' not in room_info:
            room_info['host_name'] = first_keyword
    
    return room_info

if __name__ == "__main__":
    live_url = "https://live.douyin.com/966861199494"
    html = get_dynamic_html(live_url)

    # 保存HTML
    with open("douyin_live.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ 已保存正常 HTML：douyin_live.html")
    
    # 解析房间信息
    room_info = parse_room_info(html)
    print("\n📋 解析到的房间信息：")
    print(f"   主播名称: {room_info.get('host_name', '未找到')}")
    print(f"   房间名称: {room_info.get('room_name', '未找到')}")