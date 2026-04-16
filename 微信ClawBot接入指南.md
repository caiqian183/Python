# 微信ClawBot接入指南

## 目录

- [一、前置条件](#一前置条件)
- [二、接入方式](#二接入方式)
  - [2.1 使用官方SDK](#21-使用官方sdk)
  - [2.2 直接调用HTTP API](#22-直接调用http-api)
  - [2.3 使用第三方库](#23-使用第三方库)
- [三、完整接入流程](#三完整接入流程)
  - [3.1 启用ClawBot插件](#31-启用clawbot插件)
  - [3.2 配置OpenClaw](#32-配置openclaw)
  - [3.3 集成到自己的程序](#33-集成到自己的程序)
- [四、高级配置](#四高级配置)
  - [4.1 权限管理](#41-权限管理)
  - [4.2 多渠道集成](#42-多渠道集成)
  - [4.3 自定义技能开发](#43-自定义技能开发)
- [五、常见问题与解决方案](#五常见问题与解决方案)
- [六、注意事项](#六注意事项)

## 一、前置条件

1. **微信版本**：iOS 8.0.70及以上 / 安卓8.0.69及以上
2. **OpenClaw环境**：已安装并正常运行OpenClaw（本地或云端）
3. **API密钥**：已配置好可用的AI模型API Key（如DeepSeek、豆包等）
4. **网络环境**：确保网络连接正常，能够访问微信API

## 二、接入方式

### 2.1 使用官方SDK

#### 1. 安装OpenClaw SDK

```bash
npm install @clawdbot/sdk
```

#### 2. 初始化技能项目

```bash
npx clawdbot-skill init my-skill
```

#### 3. 实现技能逻辑

```typescript
// Edit skills/my-skill/index.ts
import { Skill } from '@clawdbot/sdk'

export default class MySkill extends Skill {
  async execute(params: any) {
    // Your skill logic here
    return { success: true }
  }
}
```

#### 4. 测试和安装

```bash
# Test locally
clawdbot skills test ./my-skill

# Install to OpenClaw
clawdbot skills install ./my-skill
```

### 2.2 直接调用HTTP API

ClawBot基于iLink协议，提供HTTP/JSON接口，无需SDK可直接调用。

#### 1. 认证机制

需要在请求头中包含认证信息：

```bash
curl -X GET https://ilinkai.weixin.qq.com/api/v1/status \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

#### 2. 核心API端点

- **获取状态**：`GET /api/v1/status`
- **发送消息**：`POST /api/v1/assistant/chat`
- **执行技能**：`POST /api/v1/skills/{skill}/execute`

#### 3. 消息结构示例

**发送消息请求**：
```json
{
  "message": "你好，ClawBot！",
  "user_id": "wx_user_id",
  "chat_id": "chat_session_id"
}
```

**接收消息响应**：
```json
{
  "response": "我是你的AI助手，有什么可以帮你的？",
  "model": "claude-3.5-sonnet",
  "tokens_used": 150,
  "timestamp": "2026-04-16T10:30:00Z"
}
```

### 2.3 使用第三方库

#### 1. Python实现

可以使用GitHub上的wechat-clawbot库：

```bash
pip install wechat-clawbot
```

**使用示例**：
```python
from wechat_clawbot import ClawBot

# 初始化
bot = ClawBot(api_key="YOUR_API_KEY")

# 发送消息
response = bot.send_message("你好，ClawBot！")
print(response)
```

## 三、完整接入流程

### 3.1 启用ClawBot插件

- 打开微信 → 我 → 设置 → 插件
- 找到「微信ClawBot」插件并启用
- 复制插件详情页中的安装命令

### 3.2 配置OpenClaw

- 在运行OpenClaw的服务器上执行安装命令
- 扫码绑定微信账号
- 确认绑定成功

### 3.3 集成到自己的程序

#### 示例：Web页面集成

```javascript
// 配置OpenClaw API信息
const OPENCLAW_API_URL = "http://你的服务器IP:8080/api/v1/chat";
const API_KEY = "你的OpenClaw API密钥";

// 发送消息函数
async function sendMessage(message) {
  try {
    const response = await fetch(OPENCLAW_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        message: message,
        user_id: 'web_user_123',
        chat_id: 'session_123'
      })
    });
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error sending message:', error);
    return '发送失败，请重试';
  }
}

// 使用示例
document.getElementById('send-btn').addEventListener('click', async () => {
  const message = document.getElementById('message-input').value;
  const response = await sendMessage(message);
  document.getElementById('chat-output').innerHTML += `<div>用户: ${message}</div><div>ClawBot: ${response}</div>`;
});
```

#### 示例：Python后端集成

```python
import requests
import json

def send_clawbot_message(message):
    url = "http://你的服务器IP:8080/api/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
    }
    data = {
        "message": message,
        "user_id": "user_123",
        "chat_id": "session_123"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Error: " + response.text

# 使用示例
response = send_clawbot_message("帮我写一个Python函数，实现斐波那契数列")
print(response)
```

## 四、高级配置

### 4.1 权限管理

- 进入ClawBot聊天窗口 → 点击右上角「⋯」→ 选择「权限管理」
- 按需开启权限：
  - 基础对话权限（必开）
  - 文件读写权限（推荐）
  - 日程管理
  - 信息检索

### 4.2 多渠道集成

除微信外，OpenClaw还支持以下渠道：
- 企业微信
- 钉钉
- 飞书
- Telegram
- Discord

### 4.3 自定义技能开发

可以开发自定义技能扩展ClawBot的功能：

```typescript
// skills/weather-alert/index.ts
import { Skill, SkillConfig } from '@clawdbot/sdk'

const config: SkillConfig = {
  name: 'weather-alert',
  version: '1.0.0',
  description: 'Weather monitoring and alerts',
  dependencies: ['weather-api'],
  permissions: ['location', 'notifications'],
}

export default class WeatherAlertSkill extends Skill {
  constructor() {
    super(config)
  }

  async onEnable() {
    // Set up weather monitoring
    this.schedule.every('1h', () => this.checkWeather())
  }

  async checkWeather() {
    const weather = await this.api.weather.getCurrent()
    if (weather.severity === 'severe') {
      await this.notifications.send({
        title: 'Severe Weather Alert',
        body: weather.description,
        urgency: 'high',
      })
    }
  }
}
```

## 五、常见问题与解决方案

| 问题 | 可能原因 | 解决方案 |
|------|---------|--------|
| API调用失败 | 认证信息错误 | 检查API密钥是否正确，权限是否开启 |
| 消息发送无响应 | 网络连接问题 | 检查网络连接，确保服务器可访问 |
| 插件安装失败 | 微信版本过低 | 升级微信至8.0.70+ |
| 响应延迟高 | 网络延迟 | 考虑使用云端部署的OpenClaw |
| 功能受限 | 权限未开启 | 在ClawBot权限管理中开启相应权限 |

## 六、注意事项

1. **合法性**：使用官方ClawBot插件，合法合规，无封号风险
2. **稳定性**：基于服务器端API，稳定可靠
3. **安全性**：妥善保管API密钥，避免泄露
4. **版本更新**：定期更新微信和OpenClaw到最新版本
5. **限流策略**：合理使用API，避免高频请求触发限流

---

通过以上步骤，你可以成功在自己的程序中接入ClawBot，实现与微信AI助手的集成，为用户提供更加智能的交互体验。