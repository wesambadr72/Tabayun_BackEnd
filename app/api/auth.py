from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.db.models import User
from app.core.security import (
    create_access_token, verify_password, 
    get_password_hash, get_current_user
)
from app.core.config import settings
from app.schemas.user import (
    UserCreate, UserResponse, Token, UserUpdate, 
    CurrentUserResponse
)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # التحقق من وجود الإيميل مسبقاً
    user = db.query(User).filter(func.lower(User.email) == user_in.email.lower()).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # إنشاء المستخدم وتشفير كلمة المرور
    new_user = User(
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        country=user_in.country,
        language=user_in.language,
        role="user", # افتراضي
        is_active=1, # 1 for active
        is_verified=0 # 0 for not verified
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
   # البحث عن المستخدم باستخدام الإيميل (الإيميل يُمرر في حقل username من فورم OAuth2)
    user = db.query(User).filter(func.lower(User.email) == form_data.username.lower()).first()
    
    # التحقق من وجود المستخدم وتشابه كلمة المرور
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # إنشاء التوكن
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    # Include admin status in token payload if user is admin
    if user.is_admin:
        access_token = create_access_token(
            data={"sub": user.email, "admin": True}, expires_delta=access_token_expires
        )
    else:
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """الحصول على بيانات المستخدم الحالي"""
    return current_user
    
@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """تعديل بيانات الحساب للمستخدم المسجل حالياً"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # التحقق من كلمة المرور لتغيير الايميل او الاسم
    needs_password = False
    if "email" in update_data and update_data["email"] != current_user.email:
        needs_password = True
    if "full_name" in update_data and update_data["full_name"] != current_user.full_name:
        needs_password = True
        
    if needs_password:
        if not user_update.current_password or not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="كلمة المرور الحالية غير صحيحة يرجى التأكد منها")
            
    # التحقق من أن الإيميل الجديد غير مستخدم
    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = db.query(User).filter(func.lower(User.email) == update_data["email"].lower()).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="البريد الإلكتروني الجديد مستخدم بالفعل")
            
    # إزالة current_password من الداتا حتى لا يتم حفظها بحقل غير موجود
    if "current_password" in update_data:
        update_data.pop("current_password")
    
    # إذا أراد المستخدم تغيير كلمة المرور
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    في نظام JWT، الخروج يتم بمسح التوكن من جهة الفرونت إند.
    برمجياً، يمكننا هنا تسجيل العملية في الـ Audit Log إذا أردنا.
    """
    return {"message": "Successfully logged out"}
