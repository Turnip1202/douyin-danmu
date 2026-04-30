"""数据验证工具"""

def validate_room_id(room_id: str) -> bool:
    """
    验证房间ID是否有效
    :param room_id: 房间ID
    :return: 是否有效
    """
    if not room_id:
        return False
    # 房间ID可以是数字或字母数字组合
    return room_id.replace('-', '').replace('_', '').isalnum()

def validate_signature(signature: str) -> bool:
    """
    验证签名是否有效
    :param signature: 签名
    :return: 是否有效
    """
    if not signature:
        return False
    if signature.startswith("ERROR"):
        return False
    return len(signature) > 0

def validate_url(url: str) -> bool:
    """
    验证URL是否有效
    :param url: URL字符串
    :return: 是否有效
    """
    if not url:
        return False
    return url.startswith("http://") or url.startswith("https://")

def validate_user_id(user_id: str) -> bool:
    """
    验证用户ID是否有效
    :param user_id: 用户ID
    :return: 是否有效
    """
    if not user_id:
        return False
    # 用户ID可以是数字或字母数字组合
    return user_id.replace('-', '').replace('_', '').isalnum()