# ClawBot 网关配置和集成

## 概述

ClawBot Gateway 是一个多用户、多端点的路由网关，支持多个微信Bot账户（每个账户都1:1绑定到其创建者的微信账户）将消息路由到多个上游AI端点。

## 架构说明

```
商城系统 <---> ClawBot Gateway <---> 微信用户
     |              |
     |              └---> 多个AI端点
     |
     └---> 数据库
```

## 安装 ClawBot Gateway

### 1. 环境要求

- Python 3.10+
- uv (推荐) 或 pip

### 2. 安装

```bash
# 使用 uv 安装（推荐）
uv add "wechat-clawbot[gateway]"

# 或使用 pip
pip install "wechat-clawbot[gateway]"
```

## 配置网关

### 1. 初始化配置

```bash
clawbot-gateway init
```

这将在 `~/.clawbot-gateway/` 目录下创建配置文件。

### 2. 配置 gateway.yaml

编辑 `~/.clawbot-gateway/gateway.yaml`：

```yaml
gateway:
  host: 0.0.0.0
  port: 8765
  admin_port: 8766
  admin_token: "your-secret-admin-token-change-this"
  log_level: info

accounts:
  # 这里会在添加Bot账户时自动填充

endpoints:
  mall-system:
    name: "商城系统"
    type: http
    url: "https://your-domain.com/api/clawbot/webhook"
    api_key: "your-webhook-api-key"

routing:
  strategy: active-endpoint
  mention_prefix: "@"
  gateway_commands: ["/"]

authorization:
  mode: open
  default_endpoints: ["mall-system"]
  admins: []

archive:
  enabled: false
  path: ~/.clawbot-gateway/archive.db
  retention_days: 0
```

### 3. 配置说明

#### gateway 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| host | 网关监听地址 | 0.0.0.0 |
| port | 网关端口 | 8765 |
| admin_port | 管理API端口 | 8766 |
| admin_token | 管理API认证令牌 | - |
| log_level | 日志级别 | info |

#### endpoints 配置

商城系统作为HTTP Webhook端点：

```yaml
endpoints:
  mall-system:
    name: "商城系统"
    type: http
    url: "https://your-domain.com/api/clawbot/webhook"
    api_key: "your-webhook-api-key"
```

#### authorization 配置

| 模式 | 说明 |
|------|------|
| open | 开放模式，所有用户都可以使用 |
| allowlist | 白名单模式，只有允许的用户可以使用 |
| invite-code | 邀请码模式，需要邀请码才能使用 |

## 启动网关

### 1. 添加微信Bot账户

```bash
clawbot-gateway account add
```

扫描终端显示的二维码完成微信登录。

### 2. 查看账户列表

```bash
clawbot-gateway account list
```

### 3. 启动网关

```bash
clawbot-gateway start
```

### 4. 检查网关状态

```bash
clawbot-gateway status
```

## 管理API

网关在 `admin_port`（默认8766）提供管理API，需要使用 Bearer token 认证。

### API端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/status` | 网关状态概览 |
| GET | `/api/accounts` | 列出Bot账户 |
| GET | `/api/endpoints` | 列出端点及其状态 |
| POST | `/api/endpoints` | 添加端点 |
| DELETE | `/api/endpoints/{id}` | 删除端点 |
| GET | `/api/users` | 列出用户 |
| POST | `/api/users/{id}/bind` | 绑定用户到端点 |
| POST | `/api/users/{id}/unbind` | 解绑用户 |

### 使用示例

```python
import httpx

GATEWAY_ADMIN_URL = "http://localhost:8766"
ADMIN_TOKEN = "your-secret-admin-token"

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

# 获取网关状态
async def get_gateway_status():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GATEWAY_ADMIN_URL}/api/status",
            headers=headers
        )
        return response.json()

# 添加端点
async def add_endpoint(endpoint_id, name, url, api_key):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GATEWAY_ADMIN_URL}/api/endpoints",
            headers=headers,
            json={
                "id": endpoint_id,
                "name": name,
                "type": "http",
                "url": url,
                "api_key": api_key
            }
        )
        return response.json()
```

## Webhook 集成

### Webhook 接收端点

在商城系统中实现Webhook接收端点 `/api/clawbot/webhook`：

```python
@app.post("/api/clawbot/webhook")
async def clawbot_webhook(request: Request, db: Session = Depends(get_db)):
    """接收来自ClawBot网关的Webhook"""
    # 验证API密钥
    api_key = request.headers.get("X-API-Key")
    expected_api_key = get_config_value(db, "webhook_api_key")
    
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    data = await request.json()
    message_type = data.get("type")
    payload = data.get("data", {})
    
    if message_type == "message":
        return await handle_incoming_message(payload, db)
    elif message_type == "status":
        return await handle_status_update(payload, db)
    
    return {"success": True}

async def handle_incoming_message(data: dict, db: Session):
    """处理收到的微信消息"""
    wechat_user_id = data.get("from_user_id")
    message_content = data.get("content", "")
    message_id = data.get("message_id")
    
    # 查找对应的绑定
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.wechat_user_id == wechat_user_id,
        ClawBotBinding.binding_status == BindingStatus.BOUND
    ).first()
    
    if not binding:
        return {"reply": "未找到绑定的商城账户，请先在商城个人中心绑定ClawBot。"}
    
    # 记录消息
    record_message(db, binding.id, MessageDirection.INBOUND, message_content, message_id)
    
    # 处理消息（查询订单、商品等）
    reply = await process_user_message(binding.user_id, message_content, db)
    
    return {"reply": reply}

async def process_user_message(user_id: int, message: str, db: Session):
    """处理用户消息，返回回复"""
    message_lower = message.lower()
    
    # 查询订单
    if "订单" in message_lower or "order" in message_lower:
        return await get_user_orders_summary(user_id, db)
    
    # 查询商品
    elif "商品" in message_lower or "product" in message_lower:
        return "请访问商城查看最新商品：https://your-domain.com"
    
    # 其他功能
    elif "帮助" in message_lower or "help" in message_lower:
        return """
您可以问我：
- 查询我的订单
- 查询商品
- 联系客服
        """.strip()
    
    # 默认回复
    return "收到您的消息！如需帮助，请发送'帮助'。"
```

### 发送消息到微信

通过网关发送消息到微信：

```python
async def send_message_to_wechat(binding: ClawBotBinding, message: str, db: Session):
    """通过ClawBot网关发送消息到微信"""
    gateway_url = get_config_value(db, "gateway_url")
    admin_token = get_config_value(db, "admin_token")
    
    async with httpx.AsyncClient() as client:
        try:
            # 这里需要根据网关API实现发送逻辑
            # 实际项目中应该调用网关的发送消息API
            # 这里简化处理
            result = {
                "success": True,
                "message_id": f"msg_{datetime.datetime.utcnow().timestamp()}"
            }
            
            if result.get("success"):
                # 记录消息
                record_message(
                    db, 
                    binding.id, 
                    MessageDirection.OUTBOUND, 
                    message,
                    result.get("message_id")
                )
            
            return result
        except Exception as e:
            print(f"发送消息失败: {e}")
            return {"success": False, "error": str(e)}

def record_message(db: Session, binding_id: int, direction: MessageDirection, 
                  content: str, message_id: str = None):
    """记录消息到数据库"""
    message = ClawBotMessage(
        binding_id=binding_id,
        message_id=message_id,
        direction=direction,
        message_type=MessageType.TEXT,
        content=content,
        sent_at=datetime.datetime.utcnow()
    )
    db.add(message)
    db.commit()
```

## 商城业务集成

### 1. 订单状态变更通知

```python
async def notify_order_status_change(user_id: int, order_id: int, 
                                    status: str, db: Session):
    """订单状态变更时发送通知"""
    # 检查用户是否绑定了ClawBot
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == user_id,
        ClawBotBinding.binding_status == BindingStatus.BOUND
    ).first()
    
    if not binding:
        return
    
    # 构建通知消息
    status_messages = {
        "created": f"您的订单 #{order_id} 已创建！",
        "paid": f"您的订单 #{order_id} 已支付成功！",
        "shipped": f"您的订单 #{order_id} 已发货，预计2-3天送达！",
        "delivered": f"您的订单 #{order_id} 已送达，请查收！",
        "cancelled": f"您的订单 #{order_id} 已取消。"
    }
    
    message = status_messages.get(status, f"订单 #{order_id} 状态已更新")
    
    # 发送通知
    await send_message_to_wechat(binding, message, db)
    
    # 记录通知
    notification = OrderNotification(
        user_id=user_id,
        order_id=order_id,
        notification_type=NotificationType(status),
        message=message
    )
    db.add(notification)
    db.commit()
```

### 2. 用户查询订单

```python
async def get_user_orders_summary(user_id: int, db: Session) -> str:
    """获取用户订单摘要"""
    # 这里应该查询真实的订单数据
    # 示例数据
    recent_orders = [
        {"id": 12345, "status": "shipped", "total": 299.00},
        {"id": 12340, "status": "delivered", "total": 159.00}
    ]
    
    if not recent_orders:
        return "您暂无订单记录。"
    
    lines = ["您的最近订单："]
    for order in recent_orders:
        status_text = {
            "created": "待支付",
            "paid": "待发货",
            "shipped": "配送中",
            "delivered": "已收货",
            "cancelled": "已取消"
        }.get(order["status"], order["status"])
        
        lines.append(f"• 订单 #{order['id']} - {status_text} - ¥{order['total']:.2f}")
    
    lines.append("\n点击查看详情：https://your-domain.com/orders")
    return "\n".join(lines)
```

## 监控和维护

### 查看日志

```bash
# 查看网关日志
clawbot-gateway logs -n 100

# 查看特定用户的消息
clawbot-gateway logs --user user-id

# 查看特定端点的消息
clawbot-gateway logs --endpoint mall-system
```

### 健康检查

```bash
clawbot-gateway status
```

### 备份和恢复

网关配置和数据存储在 `~/.clawbot-gateway/` 目录下，定期备份该目录即可。

## 安全建议

1. **修改默认令牌**：立即修改 `admin_token` 和 `webhook_api_key`
2. **使用HTTPS**：在生产环境中使用HTTPS
3. **限制访问**：使用防火墙限制管理API端口的访问
4. **定期更新**：保持 `wechat-clawbot` 库为最新版本
5. **日志监控**：定期检查网关日志，发现异常及时处理

## 故障排查

### 问题：用户无法绑定

- 检查网关是否正常运行：`clawbot-gateway status`
- 查看账户状态：`clawbot-gateway account list`
- 检查网络连接和防火墙设置

### 问题：消息无法发送

- 检查端点配置是否正确
- 验证Webhook URL是否可访问
- 查看网关日志：`clawbot-gateway logs`

### 问题：Webhook接收失败

- 验证API密钥是否正确
- 检查Webhook端点是否返回200状态码
- 查看应用日志
