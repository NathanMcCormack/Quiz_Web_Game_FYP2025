from typing import Optional, Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints
from annotated_types import Ge
from datetime import date

CategoryStr = Annotated[
    str,
    StringConstraints(
        pattern=r"^[A-Za-z][A-Za-z0-9 &'\-]{0,63}$",
        min_length=1,
        max_length=64,
    ),
]  # Category must start with a letter and then only contain letters, spaces, &, apostrophes, or hyphens

QuestionStr = Annotated[str, StringConstraints(min_length=1, max_length=500)]
AnswerInt = Annotated[int, Ge(0)]  # answer must be an int greater than or equal to 0
Difficulty = Literal["easy", "medium", "hard"]  # only allow easy, medium, or hard


# ------------ Questions --------------
class QuestionCreate(BaseModel):
    question: QuestionStr
    answer: AnswerInt
    category: CategoryStr
    difficulty: Difficulty


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question: QuestionStr
    answer: AnswerInt
    category: CategoryStr
    difficulty: Difficulty


class QuestionReadPublic(BaseModel):  # leave the answer out for gameplay
    model_config = ConfigDict(from_attributes=True)
    id: int
    question: QuestionStr
    category: CategoryStr
    difficulty: Difficulty


class QuestionUpdate(QuestionCreate):  # full updates of a question
    pass


class QuestionPatch(BaseModel):  # partial updates of a question
    question: Optional[QuestionStr] = None
    answer: Optional[AnswerInt] = None
    category: Optional[CategoryStr] = None
    difficulty: Optional[Difficulty] = None


# ------------ Game Runs --------------
class GameRunCreate(BaseModel):
    score: AnswerInt
    streak: AnswerInt
    total_questions: Optional[AnswerInt] = None
    category: Optional[CategoryStr] = None


class GameRunRead(GameRunCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class UserStatsRead(BaseModel):  # linked to user information via user_id
    high_score: AnswerInt
    longest_streak: AnswerInt
    average_score: float
    games_played: int


class LeaderboardEntry(BaseModel):
    user_id: int
    best_score: AnswerInt
    best_streak: AnswerInt


# --------------- Game Validation --------------
class ValidatePlacementRequest(BaseModel):
    placed_question_id: int
    left_neighbor_id: Optional[int] = None
    right_neighbor_id: Optional[int] = None


class ValidatePlacementResponse(BaseModel):
    correct: bool
    placed_answer: AnswerInt
    left_answer: Optional[AnswerInt] = None
    right_answer: Optional[AnswerInt] = None


class GameStartRequest(BaseModel):
    category: CategoryStr
    difficulty: Difficulty


class GameStartResponse(BaseModel):
    session_id: str
    questions: list[QuestionReadPublic]


# ------------- Daily Challenge ---------------
class DailyQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question: QuestionStr
    category: CategoryStr
    difficulty: Difficulty


class DailyChallengePublic(BaseModel):
    challenge_date: date
    category: CategoryStr
    difficulty: Difficulty
    questions: list[DailyQuestionPublic]


class DailyValidatePlacementRequest(BaseModel):
    placed_question_id: int
    left_neighbor_id: Optional[int] = None
    right_neighbor_id: Optional[int] = None


class DailyValidatePlacementResponse(BaseModel):
    correct: bool
    placed_answer: AnswerInt
    left_answer: Optional[AnswerInt] = None
    right_answer: Optional[AnswerInt] = None


# ------------- Daily Categories ---------------
class DailyCategoryCreate(BaseModel):
    name: CategoryStr


class DailyCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: CategoryStr
    is_used: bool
    used_at: Optional[date] = None

class DailyChallengeListEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    challenge_date: date
    category: CategoryStr
    difficulty: Difficulty