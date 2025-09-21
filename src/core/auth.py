from datetime import timedelta, datetime, timezone
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.base import get_db
from src.models.user import User
from src.core.config import settings
from src.utils.hash import hash_password, verify_password
from src.utils.maybe import Maybe, Nothing, Some
from src.utils.result import Result, Err, Ok
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_by_email(email: str, db: Session = None) -> Maybe[User]:
    database = db or get_db()

    user = database.query(User).filter(User.email == email).first()
    return Nothing() if user is None else Some(user)


def create_user(
    email: str, password: str, username: str, db: Session = None
) -> Result[User, HTTPException]:
    database = db or get_db()

    existing_user = get_user_by_email(email, database)
    if existing_user.is_some():
        return Err(HTTPException(status_code=400, detail="Email already registered"))

    hashed_password = hash_password(password)

    user = User(
        email=email,
        password_hash=hashed_password.decode('utf-8'),
        display_name=username
    )

    database.add(user)
    database.commit()
    database.refresh(user)

    return Ok(user)


def authenticate_user(email: str, password: str, db: Session) -> Maybe[User]: 
    user = get_user_by_email(email, db)

    if user.is_nothing():
        return Nothing()

    user_instance = user.unwrap()
    if not verify_password(password, user_instance.password_hash):
        return Nothing()

    user_instance.last_login = func.now()
    db.commit()

    return Some(user_instance)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(email, next(get_db()))
    if user.is_nothing():
        raise credentials_exception

    return user.unwrap()