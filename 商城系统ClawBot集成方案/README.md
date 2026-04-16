# 商城系统 ClawBot 集成方案

## 📋 概述

本方案帮助您在商城系统中集成微信 ClawBot，实现用户在个人后台绑定微信、接收订单通知、通过微信查询订单等功能。

## ✨ 功能特性

- ✅ 用户在个人后台绑定微信 ClawBot
- ✅ 订单状态变更实时通知到微信
- ✅ 用户通过微信查询订单和商品信息
- ✅ 智能客服对话
- ✅ 多用户独立会话管理
- ✅ 消息历史记录

## 📁 文件结构

```
商城系统ClawBot集成方案/
├── README.md                          # 本文件，方案说明
├── 01-数据库设计.md                   # 数据库表结构设计
├── 02-后端API示例.py                  # FastAPI 后端API完整示例
├── 03-前端绑定界面.html               # 用户个人中心绑定页面
├── 04-ClawBot网关配置.md             # ClawBot Gateway 配置指南
├── 05-完整集成文档.md                 # 完整的集成文档
├── requirements.txt                    # Python 依赖包
└── gateway.yaml                        # ClawBot Gateway 配置文件示例
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或下载本方案
cd 商城系统ClawBot集成方案

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
# 运行后端 API 示例
python 02-后端API示例.py
```

### 3. 配置 ClawBot Gateway

```bash
# 初始化网关配置
clawbot-gateway init

# 复制配置文件
cp gateway.yaml ~/.clawbot-gateway/gateway.yaml

# 编辑配置，修改相关参数
# gateway.yaml 中的 your-domain.com 等需要替换为实际值

# 添加微信 Bot 账户
clawbot-gateway account add

# 启动网关
clawbot-gateway start
```

### 4. 打开前端页面

在浏览器中打开 [03-前端绑定界面.html](file:///workspace/商城系统ClawBot集成方案/03-前端绑定界面.html)

## 📖 详细文档

请按顺序阅读以下文档：

1. **[01-数据库设计.md](file:///workspace/商城系统ClawBot集成方案/01-数据库设计.md)** - 了解数据库表结构
2. **[02-后端API示例.py](file:///workspace/商城系统ClawBot集成方案/02-后端API示例.py)** - 查看后端API实现
3. **[03-前端绑定界面.html](file:///workspace/商城系统ClawBot集成方案/03-前端绑定界面.html)** - 集成前端绑定页面
4. **[04-ClawBot网关配置.md](file:///workspace/商城系统ClawBot集成方案/04-ClawBot网关配置.md)** - 配置ClawBot Gateway
5. **[05-完整集成文档.md](file:///workspace/商城系统ClawBot集成方案/05-完整集成文档.md)** - 完整的集成指南和API文档

## 🏗️ 系统架构

```
┌─────────────┐
│   微信用户   │
└──────┬──────┘
       │
       │ 微信消息
       │
┌──────▼──────────────────┐
│   微信 ClawBot 插件     │
└──────┬──────────────────┘
       │
       │ iLink 协议
       │
┌──────▼──────────────────┐
│  ClawBot Gateway       │
│  (多用户路由网关)       │
└──────┬──────────────────┘
       │
       │ HTTP Webhook
       │
┌──────▼──────────────────┐
│   商城系统后端           │
│  (FastAPI/Node.js等)    │
└──────┬──────────────────┘
       │
       ├────────────┬────────────┐
       │            │            │
┌──────▼──┐  ┌───▼──────┐ ┌──▼───────┐
│  数据库   │  │  订单服务  │ │  用户服务  │
└─────────┘  └──────────┘ └──────────┘
       │
       │
┌──────▼──────────────────┐
│   商城系统前端           │
│  (用户个人中心)          │
└─────────────────────────┘
```

## 🔧 核心API

| API 端点 | 方法 | 说明 |
|---------|------|------|
| `/api/clawbot/bind/init/{user_id}` | POST | 初始化绑定，生成二维码 |
| `/api/clawbot/bind/status/{user_id}` | GET | 检查绑定状态 |
| `/api/clawbot/unbind/{user_id}` | POST | 解绑 ClawBot |
| `/api/clawbot/message/send` | POST | 发送消息到微信 |
| `/api/clawbot/webhook` | POST | 接收网关 Webhook |
| `/api/clawbot/messages/{user_id}` | GET | 获取消息历史 |
| `/api/orders/notification` | POST | 创建订单通知 |

## 📚 相关资源

- [wechat-clawbot GitHub](https://github.com/nightsailer/wechat-clawbot)
- [OpenClaw 官方文档](https://getclawdbot.org/docs)
- [微信 ClawBot 插件说明](https://www1.scnet.cn/help/docs/mainsite/sclaw/channels/wechat/)

## ⚠️ 注意事项

1. **安全性**：生产环境请务必修改默认的 `admin_token` 和 `webhook_api_key`
2. **HTTPS**：生产环境请使用 HTTPS 加密所有传输
3. **微信版本**：确保用户微信版本为 8.0.70+
4. **数据备份**：定期备份数据库和网关配置

## 🆘 故障排查

如遇到问题，请参考：

- [05-完整集成文档.md](file:///workspace/商城系统ClawBot集成方案/05-完整集成文档.md) 中的故障排查章节
- [04-ClawBot网关配置.md](file:///workspace/商城系统ClawBot集成方案/04-ClawBot网关配置.md) 中的故障排查章节

## 📄 许可证

本方案仅供学习和参考使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**祝您集成顺利！** 🎉
