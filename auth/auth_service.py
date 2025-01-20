from datetime import datetime, timedelta
import jwt
import bcrypt
import re
from typing import Optional, Dict
from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, validator
from config.roles import Role, Permission, ROLE_PERMISSIONS
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

class SignupRequest(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: Optional[Role] = None

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

    async def signup(self, request: SignupRequest, admin_user: Optional[User] = None) -> Dict:
        """Register a new user with role validation"""
        if request.username in self._users:
            raise ValueError('Username already exists')

        # Role validation
        requested_role = request.role if hasattr(request, 'role') else Role.USER
        
        # Only admins can create other admins
        if requested_role == Role.ADMIN and (not admin_user or admin_user.role != Role.ADMIN):
            raise ValueError('Unauthorized to create admin users')

        if requested_role not in Role:
            raise ValueError('Invalid role specified')

        # Create user with role
        user = User(
            id=len(self._users) + 1,
            username=request.username,
            email=request.email,
            role=requested_role,
            password_hash=self._hash_password(request.password),
            created_at=datetime.utcnow()
        )
        
        self._users[request.username] = user
        return self._create_user_response(user)

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

    async def update_user_role(
        self, 
        user_id: int, 
        new_role: Role, 
        admin_user: User
    ) -> Dict:
        """Update user role (admin only)"""
        if admin_user.role != Role.ADMIN:
            raise ValueError('Only admins can update user roles')

        if new_role not in Role:
            raise ValueError('Invalid role specified')

        user = self._find_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        user.role = new_role
        return self._create_user_response(user)

    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in ROLE_PERMISSIONS.get(user.role, set())

    def _create_user_response(self, user: User) -> Dict:
        """Create standardized user response"""
        return {
            'token': self.create_token(user),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'permissions': list(ROLE_PERMISSIONS.get(user.role, set()))
            }
        }

    def _hash_password(self, password: str) -> str:
        # Implement password hashing logic
        pass

    def _find_user_by_id(self, user_id: int) -> Optional[User]:
        # Implement logic to find a user by ID
        return None

    def _hash_password(self, password: str) -> str:
        # Implement password hashing logic
        pass

    def _find_user_by_id(self, user_id: int) -> Optional[User]:
        # Implement logic to find a user by ID
        return None 