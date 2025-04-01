from passlib.context import CryptContext
from models import TokenData, UserDB
from config import SECRET_KEY, ALGORITHM

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from datetime import datetime, timedelta, timezone

import database
from typing import Optional

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password, hashed_password):
    """Функция для проверки, соответствует ли полученный пароль сохраненному хэшу"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Функция генерации хэша пароля"""
    return pwd_context.hash(password)


def get_user(db, username: str):
    """Функция получения данных о пользователе из БД"""
    for u in db:
        if u.login == username:
            return u
    
    return None


def authenticate_user(fake_db, username: str, password: str):

    user = get_user(fake_db, username)
    # проверяем, получены ли данные пользователя 
    if not user:
        return False
    # проверяем соответствие пароля и хэша пароля из базы данных
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token = Depends(oauth2_scheme)) -> Optional[UserDB]:
    if not token:
        return None  # Анонимный пользователь
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except InvalidTokenError:
        # если токен недействителен, отдадим HTTP-ошибку.
        return None
    
    users = await database.get_all_users()
    user = get_user(users, username=token_data.username)
    return user if user else None

