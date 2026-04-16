"""用户认证和管理"""

import json
import uuid
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger

from ..models.schemas import User, UserCreate, UserInDB, TokenData
from config.settings import settings


class UserManager:
    """用户管理器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.reset_codes_file = self.data_dir / "reset_codes.json"
        self.registration_codes_file = self.data_dir / "registration_codes.json"
        self._users: Dict[str, Dict[str, Any]] = {}
        self._reset_codes: Dict[str, Dict[str, Any]] = {}
        self._registration_codes: Dict[str, Dict[str, Any]] = {}
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._load_users()
        self._load_reset_codes()
        self._load_registration_codes()
    
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
            # 确保所有datetime对象都转换为字符串
            users_data = {}
            for user_id, user_info in self._users.items():
                user_copy = user_info.copy()
                if 'created_at' in user_copy and isinstance(user_copy['created_at'], datetime):
                    user_copy['created_at'] = user_copy['created_at'].isoformat()
                users_data[user_id] = user_copy
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'users': users_data,
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
    
    def _load_reset_codes(self):
        """加载密码重置验证码"""
        if self.reset_codes_file.exists():
            try:
                with open(self.reset_codes_file, 'r', encoding='utf-8') as f:
                    self._reset_codes = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Failed to load reset codes: {e}")
                self._reset_codes = {}
        else:
            self._reset_codes = {}
    
    def _save_reset_codes(self):
        """保存密码重置验证码"""
        try:
            with open(self.reset_codes_file, 'w', encoding='utf-8') as f:
                json.dump(self._reset_codes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save reset codes: {e}")
    
    def _clean_expired_reset_codes(self):
        """清理过期的重置验证码"""
        current_time = datetime.now()
        expired_codes = []
        
        for email, code_data in self._reset_codes.items():
            expires_at = datetime.fromisoformat(code_data.get('expires_at', ''))
            if current_time > expires_at:
                expired_codes.append(email)
        
        for email in expired_codes:
            del self._reset_codes[email]
        
        if expired_codes:
            self._save_reset_codes()
    
    def generate_reset_code(self, email: str) -> Optional[str]:
        """生成密码重置验证码"""
        # 清理过期验证码
        self._clean_expired_reset_codes()
        
        # 检查用户是否存在
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # 生成6位数字验证码
        reset_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # 设置10分钟过期
        expires_at = datetime.now() + timedelta(minutes=10)
        
        # 保存验证码
        self._reset_codes[email] = {
            'code': reset_code,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        self._save_reset_codes()
        
        print(f"Generated reset code for {email}")
        return reset_code
    
    def verify_reset_code(self, email: str, code: str) -> bool:
        """验证密码重置验证码"""
        # 清理过期验证码
        self._clean_expired_reset_codes()
        
        code_data = self._reset_codes.get(email)
        if not code_data:
            return False
        
        return code_data.get('code') == code
    
    def reset_password(self, email: str, code: str, new_password: str) -> bool:
        """重置用户密码"""
        # 验证重置码
        if not self.verify_reset_code(email, code):
            return False
        
        # 获取用户ID
        user_id = None
        for uid, user_data in self._users.items():
            if user_data.get('email') == email:
                user_id = uid
                break
        
        if not user_id:
            return False
        
        # 更新密码
        self._users[user_id]['hashed_password'] = self.get_password_hash(new_password)
        self._save_users()
        
        # 删除使用过的验证码
        if email in self._reset_codes:
            del self._reset_codes[email]
            self._save_reset_codes()
        
        print(f"Password reset successful for {email}")
        return True
    
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

    def _load_registration_codes(self):
        """从文件加载注册验证码数据"""
        if self.registration_codes_file.exists():
            try:
                with open(self.registration_codes_file, 'r', encoding='utf-8') as f:
                    self._registration_codes = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"加载注册验证码文件失败: {e}")
                self._registration_codes = {}
        else:
            self._registration_codes = {}

    def _save_registration_codes(self):
        """保存注册验证码数据到文件"""
        try:
            with open(self.registration_codes_file, 'w', encoding='utf-8') as f:
                json.dump(self._registration_codes, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.error(f"保存注册验证码文件失败: {e}")

    def _clean_expired_registration_codes(self):
        """清理过期的注册验证码"""
        current_time = datetime.now()
        expired_emails = []
        
        for email, code_data in self._registration_codes.items():
            expires_at = datetime.fromisoformat(code_data['expires_at'])
            if current_time > expires_at:
                expired_emails.append(email)
        
        for email in expired_emails:
            del self._registration_codes[email]
        
        if expired_emails:
            self._save_registration_codes()
            logger.info(f"清理了 {len(expired_emails)} 个过期的注册验证码")

    def generate_registration_code(self, email: str) -> str:
        """为邮箱生成注册验证码"""
        # 检查邮箱是否已注册
        if self.get_user_by_email(email):
            raise ValueError("邮箱已被注册")
        
        # 清理过期验证码
        self._clean_expired_registration_codes()
        
        # 生成6位数字验证码
        code = str(secrets.randbelow(900000) + 100000)
        expires_at = datetime.now() + timedelta(minutes=10)
        
        self._registration_codes[email] = {
            'code': code,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        self._save_registration_codes()
        logger.info(f"为 {email} 生成注册验证码")
        return code

    def verify_registration_code(self, email: str, code: str) -> bool:
        """验证注册验证码"""
        # 清理过期验证码
        self._clean_expired_registration_codes()
        
        if email not in self._registration_codes:
            logger.warning(f"邮箱 {email} 没有有效的注册验证码")
            return False
        
        code_data = self._registration_codes[email]
        if code_data['code'] != code:
            logger.warning(f"邮箱 {email} 注册验证码错误")
            return False
        
        # 验证成功后删除验证码
        del self._registration_codes[email]
        self._save_registration_codes()
        
        logger.info(f"邮箱 {email} 注册验证码验证成功")
        return True