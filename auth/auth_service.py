from datetime import datetime, timedelta
import jwt
import bcrypt
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    role: str
    password_hash: str

class AuthService:
    def __init__(self, secret_key: str, token_expiry: int = 24):
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self._users = {}  # In-memory user store (replace with database)

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