from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.user_service import UserService
from app.schemas.user_schemas import (
    UserCreate, 
    UserLogin, 
    UserUpdate, 
    UserPasswordUpdate,
    UserResponse, 
    UserLoginResponse, 
    StandardResponse
)
from app.utils.auth import AuthUtils


router = APIRouter(prefix="/api/v1/users", tags=["Users"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    payload = AuthUtils.verify_token(token)
    return payload


@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    
    - **name**: User's full name (2-100 characters)
    - **email**: Valid email address
    - **password**: Password (8-128 characters)
    """
    user_service = UserService()
    try:
        user = await user_service.register_user(user_data)
        return StandardResponse(
            success=True,
            message="User registered successfully",
            data=user.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login_user(user_credentials: UserLogin):
    """
    Login user with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token and user information
    """
    user_service = UserService()
    try:
        login_data = await user_service.login_user(
            user_credentials.email, 
            user_credentials.password
        )
        return UserLoginResponse(**login_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile
    
    Requires valid JWT token in Authorization header
    """
    user_service = UserService()
    try:
        user_id = current_user.get("sub")
        user = await user_service.get_user_profile(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/profile", response_model=StandardResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's profile
    
    - **name**: New name (optional)
    - **email**: New email address (optional)
    
    Requires valid JWT token in Authorization header
    """
    user_service = UserService()
    try:
        user_id = current_user.get("sub")
        updated_user = await user_service.update_user_profile(user_id, update_data)
        return StandardResponse(
            success=True,
            message="Profile updated successfully",
            data=updated_user.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/profile/password", response_model=StandardResponse)
async def update_user_password(
    password_data: UserPasswordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's password
    
    - **current_password**: Current password for verification
    - **new_password**: New password (8-128 characters)
    
    Requires valid JWT token in Authorization header
    """
    user_service = UserService()
    try:
        user_id = current_user.get("sub")
        result = await user_service.update_user_password(user_id, password_data)
        return StandardResponse(
            success=True,
            message=result["message"]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user profile by ID (for admin or public profile view)
    
    Requires valid JWT token in Authorization header
    """
    user_service = UserService()
    try:
        user = await user_service.get_user_profile(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
