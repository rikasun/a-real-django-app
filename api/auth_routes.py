from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from auth.auth_service import AuthService, SignupRequest
import logging
from config.roles import Role, Permission

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

# Initialize auth service
auth_service = AuthService(secret_key='your-secret-key')

@router.post("/signup")
async def signup(request: SignupRequest):
    try:
        result = await auth_service.signup(request)
        logger.info(f"New user registered: {request.username}")
        return result
    except ValueError as e:
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(username: str, password: str):
    try:
        result = await auth_service.authenticate(username, password)
        if not result:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        logger.info(f"User logged in: {username}")
        return result
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.put("/users/{user_id}/role")
async def update_role(
    user_id: int,
    new_role: Role,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await auth_service.update_user_role(user_id, new_role, current_user)
        logger.info(f"Role updated for user {user_id} to {new_role}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/users/me/permissions")
async def get_permissions(current_user: User = Depends(get_current_user)):
    return {
        'role': current_user.role,
        'permissions': list(ROLE_PERMISSIONS.get(current_user.role, set()))
    } 