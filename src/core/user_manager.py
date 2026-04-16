"""用户认证和管理"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..models.schemas import User, UserCreate, UserInDB, TokenData
from config.settings import settings


class UserManager:
    """用户管理器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self._users: Dict[str, Dict[str, Any]] = {}
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._load_users()
    
    def _load_users(self):
        """从文件加载用户数据"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._users = data.get('users', {})
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Failed to load users: {e}")
                self._users = {}
    
    def _save_users(self):
        """保存用户数据到文件"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'users': self._users,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Warning: Failed to save users: {e}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """根据邮箱获取用户"""
        for user_data in self._users.values():
            if user_data.get('email') == email:
                try:
                    # 确保日期格式正确
                    if isinstance(user_data.get('created_at'), str):
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    return UserInDB(**user_data)
                except Exception as e:
                    print(f"Warning: Failed to parse user {email}: {e}")
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        user_data = self._users.get(user_id)
        if not user_data:
            return None
        
        try:
            # 确保日期格式正确并移除密码字段
            if isinstance(user_data.get('created_at'), str):
                user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
            
            # 创建User对象（不包含密码）
            user_dict = {k: v for k, v in user_data.items() if k != 'hashed_password'}
            return User(**user_dict)
        except Exception as e:
            print(f"Warning: Failed to parse user {user_id}: {e}")
            return None
    
    def create_user(self, user_create: UserCreate) -> Optional[User]:
        """创建新用户"""
        # 检查邮箱是否已存在
        if self.get_user_by_email(user_create.email):
            return None
        
        user_id = str(uuid.uuid4())
        
        # 创建用户数据
        user_data = {
            'id': user_id,
            'email': user_create.email,
            'nickname': user_create.nickname or user_create.email.split('@')[0],
            'hashed_password': self.get_password_hash(user_create.password),
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        # 保存到内存和文件
        self._users[user_id] = user_data
        self._save_users()
        
        # 返回User对象（不包含密码）
        return User(
            id=user_id,
            email=user_create.email,
            nickname=user_data['nickname'],
            created_at=user_data['created_at'],
            is_active=True
        )
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """验证用户登录"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, user: UserInDB) -> str:
        """创建JWT访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        to_encode = {
            "user_id": user.id,
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: str = payload.get("user_id")
            email: str = payload.get("email")
            if user_id is None or email is None:
                return None
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """根据token获取当前用户"""
        token_data = self.verify_token(token)
        if not token_data:
            return None
        return self.get_user_by_id(token_data.user_id)