"""
商城系统ClawBot集成后端API示例
使用FastAPI框架
"""
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import datetime
import asyncio
import httpx
import qrcode
import io
import base64
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import enum

# 数据库配置
DATABASE_URL = "sqlite:///./clawbot_integration.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI应用
app = FastAPI(title="商城系统ClawBot集成API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 枚举定义
class BindingStatus(str, enum.Enum):
    PENDING = "pending"
    BOUND = "bound"
    UNBOUND = "unbound"
    ERROR = "error"

class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"

class NotificationType(str, enum.Enum):
    ORDER_CREATED = "order_created"
    ORDER_PAID = "order_paid"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"

# 数据库模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    clawbot_bindings = relationship("ClawBotBinding", back_populates="user")

class ClawBotBinding(Base):
    __tablename__ = "clawbot_bindings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wechat_bot_token = Column(String(255), nullable=True)
    wechat_user_id = Column(String(255), nullable=True)
    wechat_nickname = Column(String(100), nullable=True)
    binding_status = Column(Enum(BindingStatus), default=BindingStatus.PENDING)
    qr_code_data = Column(Text, nullable=True)
    qr_code_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = relationship("User", back_populates="clawbot_bindings")
    sessions = relationship("ClawBotSession", back_populates="binding")
    messages = relationship("ClawBotMessage", back_populates="binding")

class ClawBotSession(Base):
    __tablename__ = "clawbot_sessions"
    id = Column(Integer, primary_key=True, index=True)
    binding_id = Column(Integer, ForeignKey("clawbot_bindings.id"))
    context_token = Column(String(255), nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    binding = relationship("ClawBotBinding", back_populates="sessions")

class ClawBotMessage(Base):
    __tablename__ = "clawbot_messages"
    id = Column(Integer, primary_key=True, index=True)
    binding_id = Column(Integer, ForeignKey("clawbot_bindings.id"))
    message_id = Column(String(255), nullable=True)
    direction = Column(Enum(MessageDirection))
    message_type = Column(Enum(MessageType))
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    sender_id = Column(String(255), nullable=True)
    receiver_id = Column(String(255), nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    binding = relationship("ClawBotBinding", back_populates="messages")

class ClawBotGatewayConfig(Base):
    __tablename__ = "clawbot_gateway_config"
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True)
    config_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class OrderNotification(Base):
    __tablename__ = "order_notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer)
    notification_type = Column(Enum(NotificationType))
    message = Column(Text)
    sent_to_wechat = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# Pydantic模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class QRCodeResponse(BaseModel):
    qr_code_base64: str
    expires_at: datetime.datetime

class BindingStatusResponse(BaseModel):
    binding_id: int
    status: BindingStatus
    wechat_nickname: Optional[str] = None

class SendMessageRequest(BaseModel):
    user_id: int
    message: str
    message_type: MessageType = MessageType.TEXT

class OrderNotificationRequest(BaseModel):
    user_id: int
    order_id: int
    notification_type: NotificationType
    message: str

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 网关配置管理
class GatewayConfig:
    def __init__(self, db: Session):
        self.db = db
        self._load_config()
    
    def _load_config(self):
        configs = self.db.query(ClawBotGatewayConfig).all()
        self.config = {c.config_key: c.config_value for c in configs}
    
    def get(self, key: str, default: str = "") -> str:
        return self.config.get(key, default)
    
    def get_gateway_url(self) -> str:
        return self.get("gateway_url", "http://localhost:8765")
    
    def get_admin_token(self) -> str:
        return self.get("admin_token", "")
    
    def get_webhook_url(self) -> str:
        return self.get("webhook_url", "")

# ClawBot网关客户端
class ClawBotGatewayClient:
    def __init__(self, gateway_url: str, admin_token: str):
        self.gateway_url = gateway_url
        self.admin_token = admin_token
        self.headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    async def generate_qr_code(self) -> Dict[str, Any]:
        """生成微信登录二维码"""
        # 这里模拟网关API调用
        # 实际项目中应该调用真实的网关API
        qr_data = f"wechat_clawbot_login_{datetime.datetime.utcnow().timestamp()}"
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        
        # 生成二维码
        qr_img = qrcode.make(qr_data)
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "qr_code_data": qr_data,
            "qr_code_base64": qr_base64,
            "expires_at": expires_at
        }
    
    async def check_binding_status(self, qr_code_data: str) -> Dict[str, Any]:
        """检查绑定状态"""
        # 这里模拟网关API调用
        # 实际项目中应该调用真实的网关API
        # 模拟：假设用户已扫码
        return {
            "status": "bound",
            "wechat_user_id": f"wx_user_{qr_code_data[-8:]}",
            "wechat_nickname": "微信用户",
            "bot_token": f"bot_token_{datetime.datetime.utcnow().timestamp()}"
        }
    
    async def send_message(self, bot_token: str, to_user_id: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """发送消息到微信"""
        # 这里模拟网关API调用
        # 实际项目中应该调用真实的网关API
        async with httpx.AsyncClient() as client:
            try:
                # 实际调用应该是这样的：
                # response = await client.post(
                #     f"{self.gateway_url}/api/messages/send",
                #     headers=self.headers,
                #     json={
                #         "bot_token": bot_token,
                #         "to_user_id": to_user_id,
                #         "message": message,
                #         "type": message_type
                #     }
                # )
                # return response.json()
                return {
                    "success": True,
                    "message_id": f"msg_{datetime.datetime.utcnow().timestamp()}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

# API路由
@app.post("/api/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户（示例）"""
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=user.password  # 实际项目中应该使用hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"user_id": db_user.id, "username": db_user.username}

@app.post("/api/clawbot/bind/init/{user_id}", response_model=QRCodeResponse)
async def init_clawbot_binding(user_id: int, db: Session = Depends(get_db)):
    """初始化ClawBot绑定，生成二维码"""
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否已有未完成的绑定
    existing_binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == user_id,
        ClawBotBinding.binding_status == BindingStatus.PENDING
    ).first()
    
    if existing_binding:
        # 检查二维码是否过期
        if existing_binding.qr_code_expires_at > datetime.datetime.utcnow():
            return QRCodeResponse(
                qr_code_base64=existing_binding.qr_code_data,
                expires_at=existing_binding.qr_code_expires_at
            )
        else:
            # 标记为错误，创建新的
            existing_binding.binding_status = BindingStatus.ERROR
    
    # 获取网关配置
    config = GatewayConfig(db)
    gateway_client = ClawBotGatewayClient(
        config.get_gateway_url(),
        config.get_admin_token()
    )
    
    # 生成二维码
    qr_result = await gateway_client.generate_qr_code()
    
    # 创建绑定记录
    binding = ClawBotBinding(
        user_id=user_id,
        qr_code_data=qr_result["qr_code_base64"],
        qr_code_expires_at=qr_result["expires_at"],
        binding_status=BindingStatus.PENDING
    )
    db.add(binding)
    db.commit()
    
    return QRCodeResponse(
        qr_code_base64=qr_result["qr_code_base64"],
        expires_at=qr_result["expires_at"]
    )

@app.get("/api/clawbot/bind/status/{user_id}", response_model=BindingStatusResponse)
async def check_binding_status(user_id: int, db: Session = Depends(get_db)):
    """检查绑定状态"""
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == user_id
    ).order_by(ClawBotBinding.created_at.desc()).first()
    
    if not binding:
        raise HTTPException(status_code=404, detail="未找到绑定记录")
    
    # 如果是pending状态，检查网关
    if binding.binding_status == BindingStatus.PENDING:
        config = GatewayConfig(db)
        gateway_client = ClawBotGatewayClient(
            config.get_gateway_url(),
            config.get_admin_token()
        )
        
        # 从qr_code_base64中提取数据（实际项目中应该有更好的方式）
        # 这里简化处理
        status_result = await gateway_client.check_binding_status("mock_qr_data")
        
        if status_result["status"] == "bound":
            # 更新绑定状态
            binding.binding_status = BindingStatus.BOUND
            binding.wechat_user_id = status_result["wechat_user_id"]
            binding.wechat_nickname = status_result["wechat_nickname"]
            binding.wechat_bot_token = status_result["bot_token"]
            
            # 创建会话
            session = ClawBotSession(
                binding_id=binding.id,
                is_active=True
            )
            db.add(session)
            db.commit()
    
    return BindingStatusResponse(
        binding_id=binding.id,
        status=binding.binding_status,
        wechat_nickname=binding.wechat_nickname
    )

@app.post("/api/clawbot/unbind/{user_id}")
async def unbind_clawbot(user_id: int, db: Session = Depends(get_db)):
    """解绑ClawBot"""
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == user_id,
        ClawBotBinding.binding_status == BindingStatus.BOUND
    ).first()
    
    if not binding:
        raise HTTPException(status_code=404, detail="未找到活跃的绑定")
    
    # 更新状态
    binding.binding_status = BindingStatus.UNBOUND
    
    # 停用会话
    sessions = db.query(ClawBotSession).filter(
        ClawBotSession.binding_id == binding.id
    ).all()
    for session in sessions:
        session.is_active = False
    
    db.commit()
    return {"success": True, "message": "解绑成功"}

@app.post("/api/clawbot/message/send")
async def send_clawbot_message(request: SendMessageRequest, db: Session = Depends(get_db)):
    """发送消息到微信"""
    # 获取用户的绑定
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == request.user_id,
        ClawBotBinding.binding_status == BindingStatus.BOUND
    ).first()
    
    if not binding:
        raise HTTPException(status_code=400, detail="用户未绑定ClawBot")
    
    # 发送消息
    config = GatewayConfig(db)
    gateway_client = ClawBotGatewayClient(
        config.get_gateway_url(),
        config.get_admin_token()
    )
    
    result = await gateway_client.send_message(
        binding.wechat_bot_token,
        binding.wechat_user_id,
        request.message,
        request.message_type
    )
    
    # 记录消息
    message = ClawBotMessage(
        binding_id=binding.id,
        message_id=result.get("message_id"),
        direction=MessageDirection.OUTBOUND,
        message_type=request.message_type,
        content=request.message,
        sender_id="system",
        receiver_id=binding.wechat_user_id
    )
    db.add(message)
    db.commit()
    
    return result

@app.post("/api/orders/notification")
async def create_order_notification(
    request: OrderNotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建订单通知并发送到微信"""
    # 创建通知记录
    notification = OrderNotification(
        user_id=request.user_id,
        order_id=request.order_id,
        notification_type=request.notification_type,
        message=request.message
    )
    db.add(notification)
    db.commit()
    
    # 后台任务：发送到微信
    async def send_notification():
        await asyncio.sleep(1)  # 模拟延迟
        try:
            # 检查用户是否绑定了ClawBot
            binding = db.query(ClawBotBinding).filter(
                ClawBotBinding.user_id == request.user_id,
                ClawBotBinding.binding_status == BindingStatus.BOUND
            ).first()
            
            if binding:
                # 发送消息
                config = GatewayConfig(db)
                gateway_client = ClawBotGatewayClient(
                    config.get_gateway_url(),
                    config.get_admin_token()
                )
                
                result = await gateway_client.send_message(
                    binding.wechat_bot_token,
                    binding.wechat_user_id,
                    request.message
                )
                
                if result.get("success"):
                    notification.sent_to_wechat = True
                    notification.sent_at = datetime.datetime.utcnow()
                    db.commit()
        except Exception as e:
            print(f"发送通知失败: {e}")
    
    background_tasks.add_task(send_notification)
    
    return {"success": True, "notification_id": notification.id}

@app.post("/api/clawbot/webhook")
async def clawbot_webhook(request: Dict[str, Any], db: Session = Depends(get_db)):
    """接收来自ClawBot网关的Webhook"""
    # 验证Webhook签名（实际项目中应该实现）
    # 处理消息
    message_type = request.get("type")
    data = request.get("data", {})
    
    if message_type == "message":
        # 处理收到的消息
        wechat_user_id = data.get("from_user_id")
        message_content = data.get("content")
        
        # 查找对应的绑定
        binding = db.query(ClawBotBinding).filter(
            ClawBotBinding.wechat_user_id == wechat_user_id
        ).first()
        
        if binding:
            # 记录消息
            message = ClawBotMessage(
                binding_id=binding.id,
                direction=MessageDirection.INBOUND,
                message_type=MessageType.TEXT,
                content=message_content,
                sender_id=wechat_user_id
            )
            db.add(message)
            db.commit()
            
            # 这里可以添加业务逻辑，比如处理用户的查询
            # 例如：查询订单状态、查询商品信息等
            pass
    
    return {"success": True}

@app.get("/api/clawbot/messages/{user_id}")
async def get_clawbot_messages(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """获取用户的ClawBot消息历史"""
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == user_id
    ).first()
    
    if not binding:
        return {"messages": []}
    
    messages = db.query(ClawBotMessage).filter(
        ClawBotMessage.binding_id == binding.id
    ).order_by(ClawBotMessage.sent_at.desc()).limit(limit).all()
    
    return {
        "messages": [
            {
                "id": m.id,
                "direction": m.direction,
                "type": m.message_type,
                "content": m.content,
                "sent_at": m.sent_at
            }
            for m in messages
        ]
    }

# 初始化配置数据
def init_config_data(db: Session):
    """初始化网关配置数据"""
    default_configs = [
        ("gateway_url", "http://localhost:8765", "ClawBot网关URL"),
        ("admin_token", "your-secret-admin-token", "网关管理令牌"),
        ("endpoint_type", "http", "端点类型: mcp, sdk, http"),
        ("webhook_url", "https://your-domain.com/api/clawbot/webhook", "Webhook回调URL"),
        ("webhook_api_key", "your-webhook-api-key", "Webhook API密钥"),
    ]
    
    for key, value, desc in default_configs:
        existing = db.query(ClawBotGatewayConfig).filter(
            ClawBotGatewayConfig.config_key == key
        ).first()
        if not existing:
            config = ClawBotGatewayConfig(
                config_key=key,
                config_value=value,
                description=desc
            )
            db.add(config)
    db.commit()

# 应用启动时初始化
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        init_config_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
