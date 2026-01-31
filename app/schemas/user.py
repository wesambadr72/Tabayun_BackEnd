from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    country: str
    language: str = "Arabic"
    avatar: str | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    country: str | None = None
    language: str | None = None
    avatar: str | None = None

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class UserSettingsBase(BaseModel):
    font_size: str = "medium"
    font_weight: str | None = None
    line_spacing: str | None = None
    theme_mode: str = "Light"
    language: str = "Arabic"
    fallback_language: str | None = None

class UserSettingsUpdate(BaseModel):
    font_size: str | None = None
    font_weight: str | None = None
    line_spacing: str | None = None
    theme_mode: str | None = None
    language: str | None = None
    fallback_language: str | None = None

class UserSettings(UserSettingsBase):
    user_id: int

    class Config:
        from_attributes = True
