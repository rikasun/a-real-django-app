from datetime import datetime, timedelta
import jwt
import bcrypt
import re
from typing import Optional, Dict
from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, validator

class SignupRequest(BaseModel):
    username: str
    password: str
    email: EmailStr

    @validator('username')
    def username_valid(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,}$', v):
            raise ValueError('Username must be at least 3 characters and contain only letters, numbers, and underscores')
        return v

    @validator('password')
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain letters')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain numbers')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special characters')
        return v

@dataclass
class User:
    id: int
    username: str
    email: str
    role: str
    password_hash: str
    created_at: datetime

class AuthService:
    def __init__(self, secret_key: str, token_expiry: int = 24):
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self._users = {}  # In-memory user store (replace with database)

    async def signup(self, request: SignupRequest) -> Dict:
        """Register a new user"""
        # Check if username exists
        if request.username in self._users:
            raise ValueError('Username already exists')

        # Hash password
        password_hash = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt())

        # Create user
        user = User(
            id=len(self._users) + 1,
            username=request.username,
            email=request.email,
            role='user',
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        
        self._users[request.username] = user

        # Generate token
        token = self.create_token(user)
        
        return {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }

    def create_user(self, username: str, password: str, role: str = 'user') -> User:
        """Create a new user with hashed password"""
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = User(
            id=len(self._users) + 1,
            username=username,
            role=role,
            password_hash=password_hash
        )
        self._users[username] = user
        return user

    async def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return JWT token"""
        user = self._users.get(username)
        if not user:
            return None

        if not bcrypt.checkpw(password.encode(), user.password_hash):
            return None

        token = self.create_token(user)
        return {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }

    def create_token(self, user: User) -> str:
        """Create JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None 