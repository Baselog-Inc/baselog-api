from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from src.models.user import User

from src.core.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)
from src.models.base import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db=Depends(get_db)):
    new_user = create_user(user.email, user.password, user.username, db)

    if new_user.is_err():
        error = new_user.unwrap()

        if isinstance(error, HTTPException):
            raise error

        raise HTTPException(status_code=500, detail="Internal server error")

    result = new_user.unwrap()

    return {"id": str(result.id), "username": result.display_name, "email": result.email}


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)

    if user.is_nothing():
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.unwrap().email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.display_name,
        "email": current_user.email,
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token():
    return {"access_token": "new_dummy_access_token", "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(email: str):
    return {"message": "Password reset email sent"}


@router.post("/change-password")
async def change_password(password_data: PasswordChangeRequest):
    return {"message": "Password changed successfully"}
