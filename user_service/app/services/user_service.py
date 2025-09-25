from typing import Optional
from fastapi import HTTPException, status
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserUpdate, UserPasswordUpdate, UserResponse
from app.utils.auth import AuthUtils


class UserService:
    """Service layer for User business logic"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.auth_utils = AuthUtils()
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        if await self.user_repository.user_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash the password
        password_hash = self.auth_utils.hash_password(user_data.password)
        
        # Create user data
        user_create_data = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": password_hash
        }
        
        # Create user in database
        user = await self.user_repository.create_user(user_create_data)
        
        # Return user response
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return None
        
        if not user.is_active:
            return None
            
        if not self.auth_utils.verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def login_user(self, email: str, password: str) -> dict:
        """Login user and return access token"""
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = self.auth_utils.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(
                id=str(user.id),
                name=user.name,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        }
    
    async def get_user_profile(self, user_id: str) -> UserResponse:
        """Get user profile by ID"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update user profile"""
        # Get current user
        user = await self.user_repository.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if email is being updated and if it already exists
        if update_data.email and update_data.email != user.email:
            if await self.user_repository.user_exists(update_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Prepare update data (only include non-None values)
        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.email is not None:
            update_dict["email"] = update_data.email
        
        # Update user
        updated_user = await self.user_repository.update_user(user_id, update_dict)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        return UserResponse(
            id=str(updated_user.id),
            name=updated_user.name,
            email=updated_user.email,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
    
    async def update_user_password(self, user_id: str, password_data: UserPasswordUpdate) -> dict:
        """Update user password"""
        # Get current user
        user = await self.user_repository.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not self.auth_utils.verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = self.auth_utils.hash_password(password_data.new_password)
        
        # Update password
        updated_user = await self.user_repository.update_user(
            user_id, 
            {"password_hash": new_password_hash}
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        return {"message": "Password updated successfully"}
