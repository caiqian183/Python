# ClawBot网关配置指南

## 网关简介

ClawBot网关是连接商城系统与微信ClawBot的桥梁，负责处理微信消息的接收和转发。本指南将帮助您正确配置ClawBot网关，确保系统能够正常接收用户在微信发送的消息。

## 网关安装

### 1. 下载ClawBot网关

请从ClawBot官方网站下载最新版本的网关软件。

### 2. 安装依赖

```bash
# 进入网关目录
cd clawbot-gateway

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置网关

编辑 `gateway.yaml` 文件，根据您的实际情况进行配置：

```yaml
# 服务器配置
server:
  host: 0.0.0.0
  port: 8765
  debug: false

# 认证配置
auth:
  admin_token: your-secret-admin-token  # 替换为安全的管理员令牌
  webhook_api_key: your-webhook-api-key  # 替换为安全的API密钥

# 回调配置
webhook:
  url: https://your-domain.com/api/clawbot/webhook  # 替换为你的实际域名
  timeout: 10
  retry: 3
```

### 4. 启动网关

```bash
# 启动网关
python main.py

# 或使用后台运行
nohup python main.py > gateway.log 2>&1 &
```

## 关键配置项说明

### 1. 认证配置

- **admin_token**：用于调用网关API的管理员令牌，必须与商城系统中的配置一致
- **webhook_api_key**：用于验证Webhook回调的API密钥，必须与商城系统中的配置一致

### 2. 回调配置

- **url**：商城系统接收微信消息的Webhook地址，格式为 `https://your-domain.com/api/clawbot/webhook`
- **timeout**：回调超时时间，建议设置为10秒
- **retry**：失败重试次数，建议设置为3次

### 3. 多用户配置

```yaml
multi_user:
  enabled: true
  routing:
    by_wechat_id: true
    by_content: false
```

- **enabled**：启用多用户模式
- **by_wechat_id**：基于微信用户ID进行路由，确保消息发送到正确的用户

### 4. 插件配置

本方案不使用AI功能，所以插件配置为空：

```yaml
plugins:
  enabled: []
```

## 网关API

### 1. 生成微信登录二维码

```bash
POST /api/v1/auth/qr-code
Headers: Authorization: Bearer {admin_token}
```

**响应示例**：

```json
{
  "qr_code_data": "wechat_login_123456",
  "qr_code_base64": "base64编码的二维码图片",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

### 2. 检查绑定状态

```bash
GET /api/v1/auth/status/{qr_code_data}
Headers: Authorization: Bearer {admin_token}
```

**响应示例**：

```json
{
  "status": "bound",
  "wechat_user_id": "wx_user_123456",
  "wechat_nickname": "微信用户",
  "bot_token": "bot_token_123456"
}
```

## Webhook回调

当用户在微信发送消息时，ClawBot网关会通过Webhook回调将消息推送到商城系统。

### 回调格式

```json
{
  "type": "message",
  "data": {
    "message_id": "msg_123456",
    "from_user_id": "wx_user_123456",
    "content": "你好，这是一条测试消息",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 回调验证

网关会在请求头中添加 `X-API-Key` 字段，值为配置的 `webhook_api_key`，商城系统需要验证此值以确保回调的安全性。

## 故障排查

### 1. 网关启动失败

- 检查端口是否被占用
- 检查配置文件格式是否正确
- 检查依赖是否安装完整

### 2. 二维码生成失败

- 检查 `admin_token` 是否正确
- 检查网关与微信的连接是否正常

### 3. 消息接收失败

- 检查Webhook URL是否可访问
- 检查 `webhook_api_key` 是否正确
- 检查商城系统的Webhook端点是否正常运行

### 4. 绑定状态更新失败

- 检查网络连接是否正常
- 检查网关与商城系统的通信是否正常
- 检查微信用户是否已扫码确认

## 安全建议

1. **使用HTTPS**：Webhook回调必须使用HTTPS协议，确保数据传输安全
2. **强密码**：使用强随机的 `admin_token` 和 `webhook_api_key`
3. **IP限制**：在生产环境中，限制网关API的访问IP
4. **日志监控**：启用网关日志，监控异常情况
5. **定期更新**：定期更新ClawBot网关到最新版本

## 常见问题

### Q: 网关可以部署在本地吗？

A: 开发测试阶段可以部署在本地，但生产环境必须部署在公网可访问的服务器上，因为微信需要访问网关进行消息推送。

### Q: 如何查看网关日志？

A: 网关日志默认保存在 `logs/clawbot-gateway.log` 文件中，可以使用 `tail -f` 命令实时查看。

### Q: 网关支持多用户吗？

A: 是的，本配置已启用多用户模式，支持基于微信用户ID的路由。

### Q: 网关需要微信开发者账号吗？

A: ClawBot网关通常已经集成了微信机器人功能，具体是否需要微信开发者账号请参考ClawBot官方文档。

## 配置示例

以下是一个完整的生产环境配置示例：

```yaml
server:
  host: 0.0.0.0
  port: 8765
  debug: false

auth:
  admin_token: 5f4dcc3b5aa765d61d8327deb882cf99  # 示例MD5哈希
  webhook_api_key: 098f6bcd4621d373cade4e832627b4f6  # 示例MD5哈希

webhook:
  url: https://mall.example.com/api/clawbot/webhook
  timeout: 10
  retry: 3

wechat:
  bot_config:
    pass

logging:
  level: info
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/clawbot-gateway.log

multi_user:
  enabled: true
  routing:
    by_wechat_id: true
    by_content: false

plugins:
  enabled: []
```

## 总结

正确配置ClawBot网关是确保商城系统能够接收微信消息的关键。请按照本指南的步骤进行配置，并根据实际情况调整参数。如果遇到问题，请参考故障排查部分或咨询ClawBot官方支持。