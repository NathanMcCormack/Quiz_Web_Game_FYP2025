from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .GameDatabase import engine, SessionLocal
from .GameModels import Base, QuestionDB, GameRunDB
from .GameSchemas import (
    QuestionCreate, 
    QuestionRead,
    QuestionUpdate, 
    QuestionReadPublic,
    QuestionPatch,
    UserStatsRead,
    GameRunCreate,
    GameRunRead,
    LeaderboardEntry,
    ValidatePlacementRequest,
    ValidatePlacementResponse,
)
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"   # Game_Service/.env
load_dotenv(ENV_PATH)

import uuid #generates univerally unique identifiers 
from .QuestionGenerator import generate_questions
from .GameSchemas import GameStartRequest, GameStartResponse

#creates a fastapi object called app - what we you for endpoints. @app.get/post/put/patch/delete. Also used for running the server - uvicorn main:app
app = FastAPI()
#looks at all tables made from Base and rceates them
Base.metadata.create_all(bind=engine)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#function for reusability - opens request, waits until the route is finished, finally closes  the session (whether it finshed successfully or raised error)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#commits changes to db, if error - undoes changes
def commit_or_rollback(db: Session, error_msg: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_msg)
    
#----------- Health Check -------------
@app.get("/health")
def health():
    return {"status": "ok"}

#----------- Questions -----------------
@app.get("/api/questions", response_model=list[QuestionRead]) #gets all questions, limits can be added later on and we can have multiple endpoints, so we could list x amount of qestions at a time
def list_questions(db: Session = Depends(get_db)):
    stmt = select(QuestionDB).order_by(QuestionDB.id)
    return db.execute(stmt).scalars().all()

@app.get("/api/questions/random", response_model=QuestionReadPublic)
def get_random_question(category: Optional[str] = None,difficulty: Optional[str] = None,game_session_id: Optional[str] = None,db: Session = Depends(get_db),):
    stmt = select(QuestionDB)

    #can use this to fetch random categories, diffculty, or game sessions
    if category:
        stmt = stmt.where(QuestionDB.category == category)
    if difficulty:
        stmt = stmt.where(QuestionDB.difficulty == difficulty)
    if game_session_id:
        stmt = stmt.where(QuestionDB.game_session_id == game_session_id)

    stmt = stmt.order_by(func.random()).limit(1)
    db_random_question = db.execute(stmt).scalars().first()
    if not db_random_question:
        raise HTTPException(status_code=404, detail="No questions available")
    return QuestionReadPublic.model_validate(db_random_question)

#Gets a specific Question which the frontend will use to validate correct answers
@app.get("/api/questions/{question_id}", response_model=QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(QuestionDB, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@app.post("/api/questions", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session=Depends(get_db)):
    db_question = QuestionDB(**payload.model_dump()) #'**payload' creates the body sent by the user filling the field sexactly by the payload, .model_dump - turns object into reualr python dictionary
    db.add(db_question)
    commit_or_rollback(db, "Question creation failed")
    db.refresh(db_question)
    return db_question

@app.put("/api/questions/{question_id}", response_model=QuestionRead)
def update_question(question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)): #payload - the data sent by he client
    question = db.get(QuestionDB, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    for field_name, field_value in payload.model_dump().items():
        setattr(question, field_name, field_value)
    commit_or_rollback(db, "Question update failed")
    db.refresh(question)
    return question
 
@app.patch("/api/questions/{question_id}", response_model=QuestionRead)
def patch_question(question_id: int, payload: QuestionPatch, db_session: Session = Depends(get_db)):
    question = db_session.get(QuestionDB, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    partial_data = payload.model_dump(exclude_unset=True) #Only apply fields the client actually sent

    for field_name, field_value in partial_data.items():
        setattr(question, field_name, field_value)

    commit_or_rollback(db_session, "Question update failed")
    db_session.refresh(question)
    return question

@app.delete("/api/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session=Depends(get_db)):
    question = db.get(QuestionDB, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#creates new sesion ID, generates 20 questions using OpenAI, saves them to the database under the sessions ID, returns teh sesionID and the saved questions to the frontend 
@app.post("/api/game/start", response_model=GameStartResponse)
def start_game(payload: GameStartRequest, db: Session = Depends(get_db)):
    #generates a unique identifier for this game session 
    session_id = str(uuid.uuid4())

    #calls the openAI function and passes the needed parameters 
    try:
        generated = generate_questions(
            category=payload.category,
            difficulty=payload.difficulty,
            count=8,
        )
    except Exception as e:
        # log full error server-side
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Failed to generate questions: {str(e)}")

    #convert the generated questions into teh DB rows and stage them for inserting 
    db_rows: list[QuestionDB] = []
    for q in generated:
        row = QuestionDB(
            question=q.question,
            answer=q.answer,
            category=q.category,
            difficulty=q.difficulty,
            game_session_id=session_id,
        )
        db.add(row)
        db_rows.append(row)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    for row in db_rows:
        db.refresh(row)

    #includes only what the player should see (no answer)
    public_questions = [QuestionReadPublic.model_validate(r) for r in db_rows]
    return GameStartResponse(session_id=session_id, questions=public_questions)

#----------- Gameplay Validation -----------
@app.post("/api/game/validate-placement", response_model=ValidatePlacementResponse)
def validate_placement(payload: ValidatePlacementRequest, db: Session=Depends(get_db)):
    placed = db.get(QuestionDB, payload.placed_question_id)
    if not placed:
        raise HTTPException(status_code=404, detail="Placed question not found")
    left=None
    right=None
    #if there is a crad on the left
    if payload.left_neighbor_id is not None:
        #get the id from db
        left=db.get(QuestionDB, payload.left_neighbor_id)
        if not left:
            raise HTTPException(status_code=404, detail="Left neighbor question not found")

    if payload.right_neighbor_id is not None:
        right = db.get(QuestionDB, payload.right_neighbor_id)
        if not right:
            raise HTTPException(status_code=404, detail="Right neighbor question not found")

    placed_answer = placed.answer
    left_answer = left.answer if left else None
    right_answer = right.answer if right else None

    #Allows ansers to be equal
    if left is None and right is None:
        correct = True
    elif left is None:
        #error handling for if on right card exists
        correct = placed_answer <= right_answer  # right_answer is not None here
    elif right is None:
        #"" for if only left card exsts 
        correct = left_answer <= placed_answer   # left_answer is not None here
    else:
        #card on both keft and right
        correct = left_answer <= placed_answer <= right_answer

    return ValidatePlacementResponse(
        correct=correct,
        placed_answer=placed_answer,
        left_answer=left_answer,
        right_answer=right_answer,
    )

#----------- Game Runs -----------------
@app.get("/api/users/{user_id}/stats", response_model=UserStatsRead)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    count_stmt = select(func.count()).select_from(GameRunDB).where(GameRunDB.user_id == user_id)
    games_played = db.execute(count_stmt).scalar_one()

    if games_played == 0:
        return UserStatsRead(high_score=0, longest_streak=0, average_score=0.0, games_played=0)

    #functions to retrieve the user high scores, later we will link these to the actual users in the other microservice
    max_score = db.execute(select(func.max(GameRunDB.score)).where(GameRunDB.user_id == user_id)).scalar_one() #.scalar_obne() just pulls a single number result 
    max_streak = db.execute(select(func.max(GameRunDB.streak)).where(GameRunDB.user_id == user_id)).scalar_one()
    avg_score = db.execute(select(func.avg(GameRunDB.score)).where(GameRunDB.user_id == user_id)).scalar_one()
    return UserStatsRead(high_score=max_score, longest_streak=max_streak, average_score=round(float(avg_score or 0.0), 2), games_played=games_played)

#Post user run once game is ended.
@app.post("/api/users/{user_id}/runs", response_model=GameRunRead, status_code=status.HTTP_201_CREATED)
def add_user_run(user_id: int, payload: GameRunCreate, db: Session = Depends(get_db)):
    run = GameRunDB(user_id=user_id, **payload.model_dump())
    db.add(run)
    commit_or_rollback(db, "Run creation failed")
    db.refresh(run)
    return run

# Leaderboard
#we are using a list because the users best scores are not stored in a db in this microservice 
@app.get("/api/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    stmt = (
        select(
            GameRunDB.user_id,
            func.max(GameRunDB.score).label("best_score"),
            func.max(GameRunDB.streak).label("best_streak"),
        )
        .group_by(GameRunDB.user_id)
        .order_by(func.max(GameRunDB.score).desc(), func.max(GameRunDB.streak).desc())
    )
    rows = db.execute(stmt).all() #sends the above statement to the db 
    return [
        {"user_id": r.user_id, "best_score": r.best_score, "best_streak": r.best_streak}
        for r in rows #returns multiple users with thei rallocated stats
    ]



