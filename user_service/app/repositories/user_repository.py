from typing import Optional, List
from bson import ObjectId
from app.models.user import User


class UserRepository:
    """Repository layer for User data access operations"""
    
    @staticmethod
    async def create_user(user_data: dict) -> User:
        """Create a new user in the database"""
        user = User(**user_data)
        await user.insert()
        return user
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(ObjectId(user_id))
        except Exception:
            return None
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address"""
        return await User.find_one(User.email == email)
    
    @staticmethod
    async def update_user(user_id: str, update_data: dict) -> Optional[User]:
        """Update user information"""
        try:
            user = await User.get(ObjectId(user_id))
            if user:
                # Update fields
                for field, value in update_data.items():
                    if hasattr(user, field):
                        setattr(user, field, value)
                
                # Update the updated_at timestamp
                from datetime import datetime
                user.updated_at = datetime.utcnow()
                
                await user.save()
                return user
            return None
        except Exception:
            return None
    
    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete a user (soft delete by setting is_active to False)"""
        try:
            user = await User.get(ObjectId(user_id))
            if user:
                user.is_active = False
                from datetime import datetime
                user.updated_at = datetime.utcnow()
                await user.save()
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    async def get_all_users(skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users with pagination"""
        return await User.find(User.is_active == True).skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def user_exists(email: str) -> bool:
        """Check if user exists by email"""
        user = await User.find_one(User.email == email)
        return user is not None
