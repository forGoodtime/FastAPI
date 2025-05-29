from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, created_at={self.created_at})>"
    
class NoteCreate(SQLModel):
    title: str
    content: str

class NoteOut(SQLModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True