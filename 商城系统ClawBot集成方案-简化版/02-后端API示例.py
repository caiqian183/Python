"""
商城系统ClawBot集成后端API示例（简化版）
专注于微信消息接收功能，不需要AI功能
使用FastAPI框架
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import datetime
import asyncio
import httpx
import qrcode
import io
import base64
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import enum

# 数据库配置
DATABASE_URL = "sqlite:///./clawbot_integration.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI应用
app = FastAPI(title="商城系统ClawBot集成API（简化版）", version="1.0.0")

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
    messages = relationship("WechatMessage", back_populates="binding")

class WechatMessage(Base):
    __tablename__ = "wechat_messages"
    id = Column(Integer, primary_key=True, index=True)
    binding_id = Column(Integer, ForeignKey("clawbot_bindings.id"))
    message_id = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    sender_id = Column(String(255), nullable=True)
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
    
    def get_webhook_api_key(self) -> str:
        return self.get("webhook_api_key", "")

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
    db.commit()
    return {"success": True, "message": "解绑成功"}

@app.post("/api/clawbot/webhook")
async def clawbot_webhook(request: Request, db: Session = Depends(get_db)):
    """接收来自ClawBot网关的Webhook"""
    # 验证Webhook签名
    api_key = request.headers.get("X-API-Key")
    expected_api_key = GatewayConfig(db).get_webhook_api_key()
    
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # 处理消息
    data = await request.json()
    message_type = data.get("type")
    payload = data.get("data", {})
    
    if message_type == "message":
        # 处理收到的微信消息
        wechat_user_id = payload.get("from_user_id")
        message_content = payload.get("content")
        message_id = payload.get("message_id")
        
        # 查找对应的绑定
        binding = db.query(ClawBotBinding).filter(
            ClawBotBinding.wechat_user_id == wechat_user_id
        ).first()
        
        if binding:
            # 记录消息
            message = WechatMessage(
                binding_id=binding.id,
                message_id=message_id,
                content=message_content,
                sender_id=wechat_user_id
            )
            db.add(message)
            db.commit()
            
            # 这里可以添加业务逻辑，比如处理用户的消息
            # 例如：将消息存入数据库、触发业务流程等
            print(f"收到微信消息 from {wechat_user_id}: {message_content}")
    
    # 不需要回复，只需要记录
    return {"success": True}

@app.get("/api/clawbot/messages/{user_id}")
async def get_wechat_messages(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """获取用户的微信消息历史"""
    binding = db.query(ClawBotBinding).filter(
        ClawBotBinding.user_id == user_id
    ).first()
    
    if not binding:
        return {"messages": []}
    
    messages = db.query(WechatMessage).filter(
        WechatMessage.binding_id == binding.id
    ).order_by(WechatMessage.sent_at.desc()).limit(limit).all()
    
    return {
        "messages": [
            {
                "id": m.id,
                "content": m.content,
                "sender_id": m.sender_id,
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
