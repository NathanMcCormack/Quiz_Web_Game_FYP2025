from fastapi import FastAPI, Depends, HTTPException, status 
from sqlalchemy.orm import Session 
from sqlalchemy import select 
from sqlalchemy.exc import IntegrityError 
 
from .database import engine, SessionLocal 
from .models import Base, UserDB 
from .schemas import UserCreate, UserRead 

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/health")
def get_users():
    return {"status": "ok"} 
 
def get_db(): 
    db = SessionLocal() 
    try: 
        yield db 
    finally: 
        db.close() 

@app.get("/api/users", response_model=list[UserRead]) 
def list_users(db: Session = Depends(get_db)): 
    stmt = select(UserDB).order_by(UserDB.user_id) 
    return list(db.execute(stmt).scalars()) 
 
@app.get("/api/users/{user_id}", response_model=UserRead) 
def get_user(user_id: int, db: Session = Depends(get_db)): 
    user = db.get(UserDB, user_id) 
    if not user: 
        raise HTTPException(status_code=404, detail="User not found") 
    return user 
 
@app.post("/api/users", response_model=UserRead, status_code=status.HTTP_201_CREATED) 
def add_user(payload: UserCreate, db: Session = Depends(get_db)): 
    user = UserDB(**payload.model_dump()) 
    db.add(user) 
    try: 
        db.commit() 
        db.refresh(user) 
    except IntegrityError: 
        db.rollback() 
        raise HTTPException(status_code=409, detail="User already exists") 
    return user 