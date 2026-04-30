# 🎬 抖音弹幕监控系统

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![WebSocket](https://img.shields.io/badge/WebSocket-Support-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个功能强大的抖音直播弹幕监控系统，支持实时监听、数据统计和可视化展示。

---

## ✨ 功能特性

| 功能 | 描述 | 状态 |
|:---:|------|:---:|
| 📡 **实时弹幕监听** | 实时获取直播间弹幕消息 | ✅ |
| ❤️ **点赞统计** | 记录点赞消息并统计 | ✅ |
| 📊 **数据分析** | 弹幕时段分布、活跃用户排行 | ✅ |
| 🌐 **Web 界面** | 现代化的管理后台 | ✅ |
| 🔍 **弹幕搜索** | 支持关键词搜索弹幕 | ✅ |
| 🤖 **房间解析** | 自动获取房间信息 | ✅ |

---

## 🚀 快速开始

### 环境要求

- Python >= 3.8
- Node.js >= 14.0

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-username/douyin-danmu.git
cd douyin-danmu

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 启动服务

```bash
python run.py
```

访问地址: http://localhost:5000

---

## 📁 项目结构

```
douyin-danmu/
├── app/
│   ├── api/v1/           # REST API 接口
│   │   ├── room_api.py   # 房间管理
│   │   ├── danmu_api.py  # 弹幕数据
│   │   └── stats_api.py  # 统计分析
│   ├── services/         # 业务逻辑层
│   │   ├── danmu_service.py
│   │   ├── room_info_parser.py
│   │   └── signature_service.py
│   ├── repositories/     # 数据访问层
│   ├── web/templates/    # Web 前端模板
│   ├── config/           # 配置文件
│   └── utils/            # 工具函数
├── data/                 # 数据库文件
├── tests/                # 测试文件
├── requirements.txt      # 依赖清单
└── run.py                # 启动脚本
```

---

## 🛠️ 技术栈

| 分类 | 技术 | 说明 |
|:---:|------|------|
| 后端框架 | Flask | 轻量级 Python Web 框架 |
| 数据库 | SQLite | 嵌入式数据库 |
| WebSocket | websocket-client | WebSocket 客户端库 |
| 签名生成 | PyExecJS + Node.js | JavaScript 签名算法 |
| 页面解析 | Playwright | 动态页面渲染解析 |
| 协议解析 | Protocol Buffers | 抖音数据协议解析 |

---

## 🔧 API 接口

### 房间管理

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/rooms` | GET | 获取房间列表 |
| `/api/v1/rooms` | POST | 添加新房间 |
| `/api/v1/rooms/{id}` | GET | 获取房间详情 |
| `/api/v1/rooms/{id}` | PUT | 更新房间信息 |
| `/api/v1/rooms/{id}` | DELETE | 删除房间 |
| `/api/v1/rooms/{id}/start` | POST | 开始监听 |
| `/api/v1/rooms/{id}/stop` | POST | 停止监听 |
| `/api/v1/rooms/info/{room_id}` | GET | 获取抖音房间信息 |

### 弹幕数据

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/danmus/{room_id}` | GET | 获取弹幕列表 |

### 统计分析

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/stats/danmu/{room_id}` | GET | 弹幕统计 |
| `/api/v1/stats/like/{room_id}` | GET | 点赞统计 |

---

## 📝 使用示例

### 添加监控房间

```bash
curl -X POST http://localhost:5000/api/v1/rooms \
  -H "Content-Type: application/json" \
  -d '{"room_id": "966861199494", "room_name": "麦小兜的直播间", "host_name": "麦小兜"}'
```

### 开始监听弹幕

```bash
curl -X POST http://localhost:5000/api/v1/rooms/966861199494/start \
  -H "Content-Type: application/json"
```

### 获取弹幕列表

```bash
curl "http://localhost:5000/api/v1/danmus/966861199494?page=1&limit=50"
```

---

## 📊 数据统计

系统提供以下统计功能：

1. **弹幕活跃用户 TOP10** - 按弹幕数量排序
2. **点赞活跃用户 TOP10** - 按点赞数量排序
3. **弹幕时段分布** - 24小时弹幕分布柱状图

---

## ⚠️ 注意事项

1. **网络环境**：需要可以正常访问抖音服务器的网络
2. **Node.js**：必须安装 Node.js 才能生成签名
3. **直播间状态**：只能监听正在直播的房间
4. **合规使用**：请遵守抖音平台规则，合理使用本工具
5. **Playwright**：首次运行会自动下载浏览器

---

## 🐛 常见问题

**Q: 运行时提示 "ModuleNotFoundError"**

**A:** 请确保已激活虚拟环境并安装依赖

**Q: 签名生成失败**

**A:** 请确保已安装 Node.js，并且版本 ≥ 14.0

**Q: WebSocket 连接失败（400 Bad Request）**

**A:** 可能是直播间 ID 不正确或签名过期，请检查直播间 URL

**Q: 房间信息获取失败**

**A:** 请确保已安装 Playwright：`pip install playwright && playwright install chromium`

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交代码 (`git commit -m 'Add xxx'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License

---

⭐ 如果这个项目对你有帮助，请给个 Star！