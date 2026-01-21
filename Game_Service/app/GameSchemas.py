from typing import Optional, Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints
from annotated_types import Ge

CategoryStr = Annotated[str, StringConstraints(pattern=r"^[A-Za-z]+(?: [A-Za-z]+)?$", min_length=1, max_length=64)] #1 oe 2 words that only contain alphabetical characters 
QuestionStr = Annotated[str, StringConstraints(min_length=1, max_length=500)]
AnswerInt   = Annotated[int, Ge(0)] #answer for question must be an int greater than or equal to 0
Difficulty  = Literal["easy", "medium", "hard"] #Makes sure the only valeus for Diffficulty are easy, medium, hard. Using Literal

#------------ Questions -------------- 
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

class QuestionReadPublic(BaseModel): #leave the snwer out of this one, as it will be used for the gameplay and we dont want the answer to be visable to the player 
    model_config = ConfigDict(from_attributes=True)
    id: int
    question: QuestionStr
    category: CategoryStr
    difficulty: Difficulty

class QuestionUpdate(QuestionCreate): #Full updates of a question
    pass #uses same parameters from QuestionCreate

class QuestionPatch(BaseModel): #partial updates of a question
    question: Optional[QuestionStr] = None
    answer: Optional[AnswerInt] = None
    category: Optional[CategoryStr] = None
    difficulty: Optional[Difficulty] = None

    #------------ Game Runs  -------------- 
class GameRunCreate(BaseModel):
    score: AnswerInt
    streak: AnswerInt
    total_questions: Optional[AnswerInt] = None
    category: Optional[CategoryStr] = None

class GameRunRead(GameRunCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int

class UserStatsRead(BaseModel): #create foreign key as user_id oto link to user information  
    high_score: AnswerInt
    longest_streak: AnswerInt
    average_score: float
    games_played: int

class LeaderboardEntry(BaseModel):
    user_id: int
    best_score: AnswerInt
    best_streak: AnswerInt

#--------------- Game Validation -------------- 
class ValidatePlacementRequest(BaseModel):
    placed_question_id: int
    left_neighbor_id: Optional[int] = None
    right_neighbor_id: Optional[int] = None

class ValidatePlacementResponse(BaseModel):
    correct: bool
    placed_answer: AnswerInt
    left_answer: Optional[AnswerInt] = None
    right_answer: Optional[AnswerInt] = None