import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("GAME_DATABASE_URL", "sqlite:///./game.db") #looks for variable called GAME_DATABSE_URL if it doesnt exist it uses game.db which is stored in our current folder
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {} #{"check_same_thread": False} allows same connection to be used multiple timechecks if db URL starts with sqlite
engine = create_engine(DATABASE_URL, connect_args=connect_args) #creates engine - connects to db commit() etc
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False) 