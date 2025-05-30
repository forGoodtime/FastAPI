from fastapi import FastAPI, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from models import User, UserCreate, UserLogin, UserOut
from security import get_password_hash, verify_password, create_access_token, ALGORITHM, get_current_user
from models import Note, NoteCreate, NoteOut
from database import async_session, init_db
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.post("/notes/", response_model=NoteOut)
async def create_note(note: NoteCreate, session: AsyncSession = Depends(get_session)) -> NoteOut:
    db_note = Note.model_validate(note)
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