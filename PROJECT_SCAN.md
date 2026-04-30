# 抖音弹幕监控系统 - 项目扫描文档

## 一、项目概述

### 1.1 项目名称
抖音弹幕监控系统

### 1.2 项目定位
基于 Python Flask 框架开发的抖音直播间弹幕监控系统，支持多房间同时监听、弹幕数据持久化存储、Web管理界面等功能。

### 1.3 技术栈
| 分类 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.12+ |
| 框架 | Flask | 2.0+ |
| 数据库 | SQLite | 内置 |
| 日志 | loguru | 0.7+ |
| WebSocket | websocket-client | 1.9+ |
| ORM | SQLAlchemy | 2.0+ |

---

## 二、目录结构

```
抖音弹幕/
├── app/                          # 应用核心目录
│   ├── __init__.py               # 应用初始化
│   ├── api/                      # API接口层
│   │   └── v1/                   # API版本1
│   │       ├── __init__.py       # API注册
│   │       ├── room_api.py       # 房间管理API
│   │       ├── danmu_api.py      # 弹幕数据API
│   │       └── stats_api.py      # 统计数据API
│   ├── config/                   # 配置层
│   │   ├── __init__.py
│   │   ├── database.py           # 数据库配置
│   │   └── settings.py           # 应用设置
│   ├── models/                   # 数据模型
│   │   └── __init__.py           # 数据库模型定义
│   ├── repositories/             # 数据访问层
│   │   ├── room_repo.py          # 房间数据操作
│   │   └── danmu_repo.py         # 弹幕数据操作
│   ├── services/                 # 业务服务层
│   │   ├── danmu_service.py      # 弹幕监听服务
│   │   └── signature_service.py  # 签名生成服务
│   ├── utils/                    # 工具函数
│   │   └── logger.py             # 日志配置
│   └── web/                      # Web界面层
│       ├── __init__.py           # Web注册
│       ├── views.py              # 页面路由
│       └── templates/            # HTML模板
│           ├── index.html        # 首页
│           ├── rooms.html        # 房间管理页
│           └── danmus.html       # 弹幕查看页
├── logs/                         # 日志目录
├── venv/                         # 虚拟环境
├── run.py                        # 启动入口
├── requirements.txt              # 依赖清单
└── README.md                     # 项目说明
```

---

## 三、核心功能模块

### 3.1 弹幕监听服务 (`DanmuService`)
- **功能**：与抖音直播服务器建立 WebSocket 连接，实时接收弹幕消息
- **特性**：
  - 支持多房间同时监听（多线程）
  - 自动重连机制
  - 消息解析和数据持久化

### 3.2 签名服务 (`SignatureService`)
- **功能**：生成抖音 API 请求所需的签名
- **核心方法**：`generate_signature()`

### 3.3 房间管理
- 添加/删除/编辑房间
- 启动/停止监听
- 房间状态管理

### 3.4 弹幕数据管理
- 弹幕存储与查询
- 按房间分类查看
- 关键词搜索

---

## 四、API 接口清单

### 4.1 房间管理接口

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/v1/rooms` | 获取房间列表 |
| GET | `/api/v1/rooms/<room_id>` | 获取房间详情 |
| GET | `/api/v1/rooms/info/<room_id>` | 获取抖音房间信息 |
| POST | `/api/v1/rooms` | 添加房间 |
| PUT | `/api/v1/rooms/<room_id>` | 更新房间信息 |
| DELETE | `/api/v1/rooms/<room_id>` | 删除房间 |
| POST | `/api/v1/rooms/<room_id>/start` | 开始监听 |
| POST | `/api/v1/rooms/<room_id>/stop` | 停止监听 |

### 4.2 弹幕数据接口

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/v1/danmus/<room_id>` | 获取房间弹幕列表 |
| DELETE | `/api/v1/danmus/<room_id>` | 清空房间弹幕 |

### 4.3 统计接口

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/v1/stats/danmus` | 获取弹幕统计 |
| GET | `/api/v1/stats/rooms` | 获取房间统计 |

---

## 五、数据库设计

### 5.1 房间表 (`rooms`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 自增ID |
| room_id | VARCHAR(64) | UNIQUE, NOT NULL | 短房间ID（用户输入） |
| long_room_id | VARCHAR(64) | | 长房间ID（抖音返回） |
| sub_room_id | VARCHAR(64) | | 子房间ID |
| user_unique_id | VARCHAR(64) | | 用户唯一ID |
| ttwid | VARCHAR(256) | | 抖音会话标识 |
| room_name | VARCHAR(128) | | 房间名称 |
| host_name | VARCHAR(128) | | 主播名称 |
| host_id | VARCHAR(64) | | 主播ID |
| status | INTEGER | DEFAULT 0 | 状态（0离线/1在线） |
| created_at | DATETIME | | 创建时间 |
| updated_at | DATETIME | | 更新时间 |

### 5.2 弹幕表 (`danmus`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| room_id | VARCHAR(64) | FOREIGN KEY, NOT NULL | 关联房间ID |
| user_id | VARCHAR(64) | | 发送者ID |
| user_name | VARCHAR(128) | | 发送者名称 |
| content | TEXT | | 弹幕内容 |
| timestamp | DATETIME | | 发送时间 |
| created_at | DATETIME | | 存储时间 |

### 5.3 点赞表 (`likes`)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增ID |
| room_id | VARCHAR(64) | FOREIGN KEY, NOT NULL | 关联房间ID |
| user_id | VARCHAR(64) | | 用户ID |
| user_name | VARCHAR(128) | | 用户名称 |
| count | INTEGER | DEFAULT 1 | 点赞次数 |
| timestamp | DATETIME | | 时间 |
| created_at | DATETIME | | 存储时间 |

---

## 六、已完成工作

### 6.1 功能实现
- ✅ 多房间弹幕监听（多线程支持）
- ✅ 弹幕数据持久化存储
- ✅ Web管理界面（房间管理、弹幕查看）
- ✅ 房间CRUD操作
- ✅ 房间编辑功能
- ✅ 自动获取房间信息（房间名称、主播名称）

### 6.2 问题修复
- ✅ 控制台日志无输出
- ✅ 中文日志乱码（Windows UTF-8编码设置）
- ✅ 日志重复记录（单例模式）
- ✅ 数据库外键约束错误
- ✅ 房间状态显示错误（重启后重置）
- ✅ 弹幕按房间分类查看

---

## 七、待解决问题

| 序号 | 问题描述 | 状态 | 优先级 |
|------|----------|------|--------|
| 1 | WebSocket消息解压失败（Error -3） | 待排查 | 高 |
| 2 | 弹幕监听不稳定，偶尔断开 | 待优化 | 高 |
| 3 | 多房间监听资源占用监控 | 待实现 | 中 |
| 4 | 弹幕消息去重机制 | 待实现 | 中 |
| 5 | 用户管理模块 | 待扩展 | 低 |

---

## 八、后续开发建议

### 8.1 功能扩展
1. **用户管理**：添加用户认证、权限管理
2. **数据导出**：支持弹幕数据导出为Excel/CSV
3. **实时推送**：使用 WebSocket 向前端推送实时弹幕
4. **告警功能**：特定关键词弹幕告警

### 8.2 性能优化
1. 数据库索引优化
2. 弹幕批量插入
3. 缓存策略（Redis）

### 8.3 部署建议
1. 使用 Gunicorn + Nginx 部署
2. 配置 Supervisor 进程管理
3. 添加日志轮转配置

---

## 九、启动方式

```bash
# 1. 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python run.py

# 4. 访问管理界面
# http://127.0.0.1:5000/
```

---

**文档版本**：v1.0  
**生成时间**：2026-04-30  
**项目状态**：开发中