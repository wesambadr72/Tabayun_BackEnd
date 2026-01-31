from pydantic import BaseModel, EmailStr
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class Login(BaseModel):
    email: EmailStr
    password: str

class LoginHistory(BaseModel):
    id: int
    email: EmailStr
    login_time: datetime
    status: str

    class Config:
        from_attributes = True

class Logout(BaseModel):
    user_id: int
    session_token: str
    logout_time: datetime

    class Config:
        from_attributes = True
