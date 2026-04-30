# 抖音弹幕监听工具

一个基于 Python 的抖音直播弹幕监听工具，可以实时获取直播间的弹幕、点赞等消息。

## ✨ 功能特性

- ✅ 实时监听抖音直播弹幕
- ✅ 支持获取点赞消息
- ✅ 自动处理签名生成
- ✅ 支持 Windows/Linux 系统

## 📦 环境要求

| 软件 | 版本 | 说明 |
|-----|-----|-----|
| Python | ≥ 3.8 | 项目开发语言 |
| Node.js | ≥ 14.0 | 执行 JavaScript 签名 |

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行项目

```bash
# 修改直播间 URL（在 main.py 中）
# url = "https://live.douyin.com/你的直播间ID"

# 运行主程序
python main.py
```

### 3. 配置说明

在 `main.py` 中修改直播间地址：

```python
url = "https://live.douyin.com/858408884422"
```

## 📁 项目结构

```
├── main.py           # 主程序入口
├── douyin_pb2.py     # Protocol Buffers 数据结构
├── douyin.proto      # Proto 定义文件
├── sign.js           # 签名算法（混淆代码）
├── danmu.js          # 签名接口封装
├── env.js            # 浏览器环境模拟
├── requirements.txt  # 依赖清单
├── README.md         # 项目说明
└── venv/             # Python 虚拟环境（自动生成）
```

## 📝 核心功能

### 弹幕监听

监听直播间实时弹幕消息，包括：
- 用户弹幕内容
- 点赞消息
- 其他互动消息

### 签名生成

自动生成抖音 API 请求所需的签名，无需手动配置。

## ⚠️ 注意事项

1. **网络环境**：需要可以访问抖音服务器的网络环境
2. **Node.js**：必须安装 Node.js 才能生成签名
3. **直播间状态**：只能监听正在直播的房间
4. **合规使用**：请遵守抖音平台规则，合理使用本工具

## 🐛 常见问题

### Q: 运行时提示 "ModuleNotFoundError: google"
**A:** 缺少 protobuf 库，执行 `pip install protobuf`

### Q: 签名生成失败
**A:** 请确保已安装 Node.js，并且版本 ≥ 14.0

### Q: WebSocket 连接失败（400 Bad Request）
**A:** 可能是直播间 ID 不正确或签名过期，请检查直播间 URL

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请提交 Issue 或 PR。