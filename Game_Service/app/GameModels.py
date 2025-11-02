from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func

class Base(DeclarativeBase):
    pass

class QuestionDB(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[int] = mapped_column(Integer, nullable=False)  # integer >= 0
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String, nullable=False)  #easy, medium, hard 
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class GameRunDB(Base):
    __tablename__ = "game_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False) #later tokens will be implemented o connect a game run to the suer that is logged in 
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    streak: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=True)
    started_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)