from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, func, Date, Boolean, ForeignKey, UniqueConstraint

#SQLAlchemy - parent class that all db models inherit from, knows to add tables to db. pass just defines the class (no code needed)
class Base(DeclarativeBase):
    pass

class QuestionDB(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[int] = mapped_column(Integer, nullable=False)  # integer >= 0
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String, nullable=False)  #easy, medium, hard 
    game_session_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True) #used to track the game session 
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

class DailyCategoryDB(Base):
    __tablename__ = "daily_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    used_at: Mapped["date | None"] = mapped_column(Date, nullable=True)

class DailyChallengeDB(Base):
    __tablename__ = "daily_challenges"
    __table_args__ = (UniqueConstraint("challenge_date", name="uq_daily_challenge_date"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_date: Mapped["date"] = mapped_column(Date, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, nullable=False)  # "easy" | "medium" | "hard"
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="pending")  # pending/success/failed
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    generated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    questions: Mapped[list["DailyQuestionDB"]] = relationship(back_populates="challenge",cascade="all, delete-orphan",)

class DailyQuestionDB(Base):
    __tablename__ = "daily_questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_challenge_id: Mapped[int] = mapped_column(ForeignKey("daily_challenges.id"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    challenge: Mapped["DailyChallengeDB"] = relationship(back_populates="questions")