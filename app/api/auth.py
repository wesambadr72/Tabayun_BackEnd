from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_current_user, get_password_hash, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.user import CurrentUserResponse, Token, UserCreate, UserResponse, UserUpdate
from app.services.demo_fallback import (
    authenticate_user as authenticate_demo_user,
    is_email_available as is_demo_email_available,
    register_user as register_demo_user,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(func.lower(User.email) == user_in.email.lower()).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

        new_user = User(
            email=user_in.email.lower(),
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            country=user_in.country,
            language=user_in.language,
            role="user",
            is_active=1,
            is_verified=0,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError:
        try:
            return register_demo_user(user_in)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = db.query(User).filter(func.lower(User.email) == form_data.username.lower()).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        email = user.email
        is_admin = user.is_admin
    except SQLAlchemyError:
        user = authenticate_demo_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        email = user["email"]
        is_admin = user["is_admin"]

    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    token_data = {"sub": email}
    if is_admin:
        token_data["admin"] = True

    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = user_update.model_dump(exclude_unset=True)

    needs_password = "email" in update_data and update_data["email"] != current_user.email
    if needs_password:
        if not user_update.current_password or not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

    try:
        if "email" in update_data and update_data["email"] != current_user.email:
            existing_user = db.query(User).filter(func.lower(User.email) == update_data["email"].lower()).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email is already used")

        update_data.pop("current_password", None)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(current_user, field, value)

        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is not available in demo mode") from exc


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}


@router.get("/check-email")
def check_email(email: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(func.lower(User.email) == email.lower()).first()
        return {"available": user is None}
    except SQLAlchemyError:
        return {"available": is_demo_email_available(email)}


@router.post("/forgot-password")
def forgot_password(email_data: dict, db: Session = Depends(get_db)):
    email = email_data.get("email")
    if not email:
        return {"message": "If the email exists, a reset link has been sent."}

    try:
        db.query(User).filter(func.lower(User.email) == email.lower()).first()
    except SQLAlchemyError:
        pass

    return {"message": "If the email exists, a reset link has been sent."}
