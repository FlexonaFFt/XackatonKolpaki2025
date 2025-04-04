from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db, User
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Проверка соответствия пароля хешу"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Получение хеша пароля"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """Аутентификация пользователя по имени и паролю"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

def get_user_by_username(db: Session, username: str):
    """Получение пользователя по имени"""
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user