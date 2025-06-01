from fastapi import FastAPI, Depends, HTTPException, status, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from models import User, UserCreate, UserLogin, UserOut
from security import get_password_hash, verify_password, create_access_token, ALGORITHM, get_current_user
from models import Note, NoteCreate, NoteUpdate, NoteOut  # убедитесь, что NoteUpdate импортирован
from database import async_session, init_db
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.get("/notes/{note_id}", response_model=NoteOut)
async def read_note(
    note_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    note = await session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteOut)
async def update_note(
    note_update: NoteUpdate,
    note_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    note = await session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    for key, value in note_update.dict(exclude_unset=True).items():
        setattr(note, key, value)
    note.updated_at = datetime.utcnow()
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    note = await session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.delete(note)
    await session.commit()

@app.post("/notes/", response_model=NoteOut)
async def create_note(
    note: NoteCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> NoteOut:
    db_note = Note(**note.dict(), owner_id=current_user.id)
    session.add(db_note)
    await session.commit()
    await session.refresh(db_note)
    return db_note

@app.get("/notes/", response_model=List[NoteOut])
async def read_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search notes by title or content"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[NoteOut]:
    statement = select(Note).where(Note.owner_id == current_user.id).offset(skip).limit(limit)
    if search:
        statement = statement.where(
            (Note.title.ilike(f"%{search}%")) | (Note.content.ilike(f"%{search}%"))
        )
    result = await session.execute(statement)
    statement = statement.offset(skip).limit(limit)
    notes = result.scalars().all()
    return notes

@app.post("/register/", response_model=UserOut)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password, role="user")
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@app.post("/login/")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.username == username))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/admin/users/", response_model=List[UserOut])
async def read_users(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users