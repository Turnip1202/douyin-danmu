"""签名生成工具"""
import subprocess
import json
import os

def generate_signature(md5_value: str) -> str:
    """
    调用Node.js生成签名
    :param md5_value: MD5签名原文
    :return: 生成的签名
    """
    # 读取签名相关的JS文件
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 读取 env.js
    env_path = os.path.join(base_dir, '..', 'env.js')
    with open(env_path, 'r', encoding='utf-8') as f:
        env_js = f.read()
    
    # 读取 sign.js
    sign_path = os.path.join(base_dir, '..', 'sign.js')
    with open(sign_path, 'r', encoding='utf-8') as f:
        sign_js = f.read()
    
    # 读取 danmu.js
    danmu_path = os.path.join(base_dir, '..', 'danmu.js')
    with open(danmu_path, 'r', encoding='utf-8') as f:
        danmu_js = f.read()
    
    full_js = env_js + '\n' + sign_js + '\n' + danmu_js
    
    # 构建JS代码
    js_code = f"""
    {full_js}
    var result = get_sign('{md5_value}');
    console.log(JSON.stringify(result));
    """
    
    # 写入临时文件
    temp_file = "_temp_sign.js"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    try:
        result = subprocess.run(
            ['node', temp_file],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30,
            env={**os.environ, 'NODE_OPTIONS': '--no-warnings'}
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            lines = output.split('\n')
            signature = None
            
            # 从最后一行开始找有效的签名（过滤调试输出）
            for line in reversed(lines):
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith('✅') and not line.startswith('❌'):
                    signature = line
                    break
            
            if signature is None:
                signature = lines[-1].strip() if lines else output
            
            # 尝试解析JSON
            try:
                parsed = json.loads(signature)
                if isinstance(parsed, dict):
                    signature = parsed.get('X-Bogus') or parsed.get('signature') or signature
                else:
                    signature = parsed
            except json.JSONDecodeError:
                pass
            
            return str(signature)
        else:
            raise Exception(f"签名生成失败: {result.stderr}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)