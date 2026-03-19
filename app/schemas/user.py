from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

# الأجزاء المشتركة
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    country: str
    language: Optional[str] = "Arabic"

# بيانات التسجيل
class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('يجب أن تكون كلمة المرور 8 خانات على الأقل')
        if not re.search(r'[A-Z]', v):
            raise ValueError('يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل')
        if not re.search(r'[a-z]', v):
            raise ValueError('يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل')
        if not re.search(r'\d', v):
            raise ValueError('يجب أن تحتوي كلمة المرور على رقم واحد على الأقل')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('يجب أن تحتوي كلمة المرور على رمز واحد على الأقل')
        return v

# تحديث الملف الشخصي 
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

# ما يعود للواجهة (Response)
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_admin: bool
    role: str

    class Config:
        from_attributes = True

# User Settings (Accessibility & Preferences)
class UserSettingsBase(BaseModel):
    font_size: str = "medium"
    theme_mode: str = "Light"
    language: str = "Arabic"

class UserSettingsUpdate(UserSettingsBase):
    font_size: Optional[str] = None
    theme_mode: Optional[str] = None
    language: Optional[str] = None

class UserSettingsResponse(UserSettingsBase):
    user_id: int
    
    class Config:
        from_attributes = True

# بيانات تسجيل الدخول

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# بيانات المفضلة
class BookmarkCreate(BaseModel):
    comparison_id: int

class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    comparison_id: int
    created_at: datetime

    class Config:
        from_attributes = True

