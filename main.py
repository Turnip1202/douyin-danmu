import hashlib
import os
import re
import requests
from websocket import WebSocketApp
import ssl
import time
import sys
from douyin_pb2 import PushFrame, Message,Response,ChatMessage,LikeMessage,User
from loguru import logger
import gzip

# 设置 UTF-8 编码，解决 execjs 在 Windows 下的编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 如果是 Windows 系统，设置控制台编码
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 导入 execjs 前设置环境变量
import execjs


def get_room_info(url):
    import time
    import random
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
    res = requests.get(url, headers=headers, cookies=cookies)

    # 提取 room_id
    match_list = re.findall(r'"roomId\\":\\"(\d+)\\",', res.text)
    if not match_list:
        match_list = re.findall(r'"room_id":(\d+)', res.text)
    room_id = match_list[0]
    print(f"房间号：{room_id}")

    # 提取 sub_room_id
    sub_room_match = re.findall(r'"sub_room_id":(\d+)', res.text)
    sub_room_id = sub_room_match[0] if sub_room_match else room_id
    print(f"子房间号：{sub_room_id}")

    # 提取 user_unique_id（webcast 相关）
    user_unique_match = re.findall(r'"user_unique_id":"?(\d+)"?', res.text)
    if not user_unique_match:
        user_unique_match = re.findall(r'"webcast_user_id":"?(\d+)"?', res.text)
    user_unique_id = user_unique_match[0] if user_unique_match else "7621938952584791552"
    print(f"用户唯一ID：{user_unique_id}")

    ttwid = res.cookies.get_dict().get('ttwid', '')
    if not ttwid:
        # 从响应中提取 ttwid
        ttwid_match = re.findall(r'ttwid=([^;]+)', res.text)
        ttwid = ttwid_match[0] if ttwid_match else ''

    print(f"TTwid: {ttwid}")

    return room_id, sub_room_id, user_unique_id, ttwid


def on_open(ws):
    print("on_open", ws)



def on_message(ws, message):
    # 回调函数，直接接收到抖音的弹幕信息
    # print("on_message", message)
    frame = PushFrame()
    frame.ParseFromString(message)
    # print("frame:::", frame)

    result=gzip.decompress(frame.payload)
    res=Response()
    res.ParseFromString(result)
    # print("res:::", res)

    if res.need_ack:
        s = PushFrame()
        s.payload_type = 'ack'
        s.payload = res.internal_ext.encode('utf-8')
        s.LogID = frame.LogID
        ws.send(s.SerializeToString())

    for item in res.messages:
        # print(item.method)

        if item.method == 'WebcastChatMessage':
            # 解析弹幕信息
            message = ChatMessage()
            message.ParseFromString(item.payload)
            info = f"【{message.user.nickName}】发出弹幕：{message.content}"
            logger.info(info)
        # 如果你想要获取礼物、点赞
        if item.method == 'WebcastLikeMessage':
            like_message = LikeMessage()
            like_message.ParseFromString(item.payload)
            logger.info(f"点赞:{like_message.user.nickName}给主播点了 {like_message.count} 次赞")








def on_error(ws, message):
    print("on_error", ws, message)
    time.sleep(2)


def on_close(ws, *args, **kwargs):
    time.sleep(2)



url = "https://live.douyin.com/459565028332"
room_id, sub_room_id, user_unique_id, ttwid = get_room_info(url)

# 使用动态获取的参数生成签名
text = f"live_id=1,aid=6383,version_code=180800,webcast_sdk_version=1.0.15,room_id={room_id},sub_room_id={sub_room_id},sub_channel_id=,did_rule=3,user_unique_id={user_unique_id},device_platform=web,device_type=,ac=,identity=audience"
md5_obj = hashlib.md5()
md5_obj.update(text.encode('utf-8'))
sign = md5_obj.hexdigest()
print(f"MD5签名: {sign}")
print(f"TTwid: {ttwid[:30]}...")

# 加载 env.js 模拟浏览器环境 + sign.js + danmu.js
print("\n正在加载浏览器环境 (env.js)...")
with open('env.js', 'r', encoding='utf-8') as f:
    env_js = f.read()
    
with open('sign.js', 'r', encoding='utf-8') as f:
    sign_js = f.read()
    
with open('danmu.js', 'r', encoding='utf-8') as f:
    danmu_js = f.read()

# 合并所有 JS 代码：env.js -> sign.js -> danmu.js
full_js = env_js + '\n' + sign_js + '\n' + danmu_js

# 使用 subprocess 调用 Node.js 来避免编码问题
import subprocess
import json

# 编写临时 JS 文件
js_code = f"""
{full_js}
var result = get_sign('{sign}');
console.log(JSON.stringify(result));
"""

# 写入临时文件
with open('_temp_sign.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

# 使用 Node.js 执行
print("✅ 浏览器环境加载完成")
print("⚙️  正在生成签名...")
try:
    result = subprocess.run(
        ['node', '_temp_sign.js'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env={**os.environ, 'NODE_OPTIONS': '--no-warnings'}
    )
    
    if result.returncode == 0:
        output = result.stdout.strip()
        # 签名可能在最后一行（因为前面可能有调试输出）
        lines = output.split('\n')
        # 从最后一行开始找有效的签名
        signature = None
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('✅') and not line.startswith('❌'):
                signature = line
                break
        
        if signature is None:
            signature = lines[-1].strip() if lines else output
        
        try:
            # 尝试解析为 JSON
            parsed = json.loads(signature)
            # 如果是对象，提取 X-Bogus 或 signature 字段
            if isinstance(parsed, dict):
                signature = parsed.get('X-Bogus') or parsed.get('signature') or signature
            else:
                signature = parsed
        except json.JSONDecodeError:
            # 如果不是 JSON，保持原样
            pass
        
        print(f"✅ 签名生成成功: {str(signature)[:60]}..." if len(str(signature)) > 60 else f"✅ 签名生成成功: {signature}")
    else:
        print(f"❌ 签名生成失败: {result.stderr}")
        raise Exception(f"签名生成失败: {result.stderr}")
finally:
    # 清理临时文件
    if os.path.exists('_temp_sign.js'):
        os.remove('_temp_sign.js')

# 构建 WebSocket URL
fetch_time = int(time.time() * 1000)
wss_url = f'wss://webcast100-ws-web-hl.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.0.15&update_version_code=1.0.15&compress=gzip&device_platform=web&cookie_enabled=true&screen_width=1707&screen_height=960&browser_language=zh-CN&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/147.0.0.0%20Safari/537.36%20Edg/147.0.0.0&browser_online=true&tz_name=Etc/GMT-8&cursor=&internal_ext=internal_src:dim|wss_push_room_id:{room_id}|wss_push_did:{user_unique_id}|fetch_time:{fetch_time}|seq:1|wss_info:0-0-0-0&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1&user_unique_id={user_unique_id}&im_path=/webcast/im/fetch/&identity=audience&need_persist_msg_count=0&insert_task_id=&live_reason=&room_id={room_id}&sub_room_id={sub_room_id}&heartbeatDuration=0&signature={signature}'

# 打印调试信息
print(f"\n📋 调试信息:")
print(f"  room_id: {room_id}")
print(f"  sub_room_id: {sub_room_id}")
print(f"  user_unique_id: {user_unique_id}")
print(f"  ttwid: {ttwid[:50]}..." if len(ttwid) > 50 else f"  ttwid: {ttwid}")
print(f"  signature: {str(signature)[:60]}..." if len(str(signature)) > 60 else f"  signature: {signature}")
print(f"  fetch_time: {fetch_time}")
print(f"  MD5原文: {text}")
ws = WebSocketApp(
    wss_url,
    header=
    {
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
    cookie=f"ttwid={ttwid}",  # 只需要 ttwid
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.run_forever(
    sslopt={"cert_reqs": ssl.CERT_NONE},
    ping_interval=20,  # 每20秒发送ping
    ping_timeout=10  # ping超时10秒
)


