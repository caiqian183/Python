# 商城系统ClawBot集成方案（简化版）

## 项目概述

本方案专注于商城系统与微信ClawBot的集成，主要功能是接收用户在微信发送的消息，不包含AI回复功能。

## 核心功能

- ✅ 微信ClawBot绑定（生成二维码、扫码绑定）
- ✅ 接收用户在微信发送的消息
- ✅ 消息历史记录查看
- ✅ 解绑ClawBot功能

## 技术栈

- **后端**：FastAPI (Python)
- **前端**：HTML5 + CSS3 + JavaScript
- **数据库**：SQLite (可扩展为MySQL/PostgreSQL)
- **ClawBot**：微信ClawBot网关

## 目录结构

```
商城系统ClawBot集成方案-简化版/
├── 01-数据库设计.md           # 数据库表结构设计
├── 02-后端API示例.py          # FastAPI后端API实现
├── 03-前端绑定界面.html       # 前端绑定管理界面
├── README.md                  # 项目概述和快速开始
├── requirements.txt           # Python依赖项
├── gateway.yaml               # ClawBot网关配置
├── 04-ClawBot网关配置.md      # 网关配置指南
└── 05-完整集成文档.md         # 完整集成文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python 02-后端API示例.py
```

服务将在 http://localhost:8000 启动

### 3. 配置ClawBot网关

1. 编辑 `gateway.yaml` 文件，配置网关参数
2. 启动ClawBot网关（请参考ClawBot官方文档）

### 4. 访问前端界面

打开 `03-前端绑定界面.html` 文件，即可访问绑定管理界面。

## 主要API端点

- `POST /api/clawbot/bind/init/{user_id}` - 生成绑定二维码
- `GET /api/clawbot/bind/status/{user_id}` - 检查绑定状态
- `POST /api/clawbot/unbind/{user_id}` - 解绑ClawBot
- `POST /api/clawbot/webhook` - 接收微信消息Webhook
- `GET /api/clawbot/messages/{user_id}` - 获取消息历史

## 注意事项

1. 本方案为简化版，专注于消息接收功能
2. 实际部署时需要：
   - 替换数据库为生产环境数据库（如MySQL）
   - 配置真实的ClawBot网关URL和令牌
   - 部署到公网可访问的服务器
   - 配置HTTPS（Webhook回调需要）

## 系统流程图

1. 用户在商城系统个人中心点击"生成二维码"
2. 系统调用ClawBot网关生成微信登录二维码
3. 用户使用微信扫描二维码并确认绑定
4. ClawBot网关通过Webhook通知系统绑定成功
5. 系统更新绑定状态，建立用户与微信的关联
6. 用户在微信发送消息，ClawBot网关通过Webhook推送给系统
7. 系统接收并存储消息，用户可在系统中查看消息历史

## 故障排查

- **二维码生成失败**：检查ClawBot网关配置是否正确
- **绑定状态更新失败**：检查网络连接和网关响应
- **消息接收失败**：检查Webhook URL是否可访问，API密钥是否正确
- **数据库错误**：检查数据库连接和表结构是否正确

## 安全建议

- 生产环境中使用强随机的API密钥
- 限制Webhook端点的访问IP
- 对敏感数据进行加密存储
- 定期备份数据库

## 许可证

本方案仅供参考，可根据实际需求进行修改和扩展。