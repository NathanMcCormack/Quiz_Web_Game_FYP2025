from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column 
from sqlalchemy import String, Integer 

class Base(DeclarativeBase): 
    pass 

class UserDB(Base): 
    __tablename__ = "users" 
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True) 
    name: Mapped[str] = mapped_column(String, nullable=False) 
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False) 
    age: Mapped[int] = mapped_column(Integer, nullable=False) 
    student_id: Mapped[str] = mapped_column(String, unique=True, nullable=False) 