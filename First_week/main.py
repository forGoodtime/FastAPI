from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from typing import List

from models import Note, NoteCreate, NoteOut
from database import async_session, init_db

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.post("/notes/", response_model=NoteOut)
async def create_note(note: NoteCreate, session: AsyncSession = Depends(get_session)) -> NoteOut:
    db_note = Note.from_orm(note)
    session.add(db_note)
    await session.commit()
    await session.refresh(db_note)
    return db_note

@app.get("/notes/", response_model=List[NoteOut])
async def read_notes(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)) -> List[NoteOut]:
    statement = select(Note).offset(skip).limit(limit)
    result = await session.execute(statement)
    notes = result.scalars().all()
    return notes