from config import settings
from sqlmodel import SQLModel, Field as ORMField, Relationship
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    username: str
    password: str
    email: Optional[str] = ORMField(default=None)
    role: str = ORMField(default="user")
    created_at: datetime = ORMField(default_factory=datetime.utcnow)
    updated_at: datetime = ORMField(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class Note(SQLModel, table=True):
    id: Optional[int] = ORMField(default=None, primary_key=True)
    title: str
    content: str
    owner_id: int = ORMField(foreign_key="user.id")
    created_at: datetime = ORMField(default_factory=datetime.utcnow)
    updated_at: datetime = ORMField(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, created_at={self.created_at})>"

class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    username: str = Field(..., description="Имя пользователя", example="user1")
    password: str = Field(..., description="Пароль пользователя", example="strongpassword")

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str = Field(..., description="Имя пользователя", example="user1")
    password: str = Field(..., description="Пароль пользователя", example="strongpassword")

class UserOut(BaseModel):
    """Схема пользователя для ответа"""
    id: int
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    """Схема для создания заметки"""
    title: str = Field(..., description="Заголовок заметки", example="Моя заметка")
    content: str = Field(..., description="Текст заметки", example="Текст заметки...")

class NoteUpdate(BaseModel):
    """Схема для обновления заметки"""
    title: Optional[str] = Field(None, description="Новый заголовок", example="Обновлённая заметка")
    content: Optional[str] = Field(None, description="Новый текст", example="Обновлённый текст...")

    class Config:
        from_attributes = True

class NoteOut(BaseModel):
    """Схема заметки для ответа"""
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True