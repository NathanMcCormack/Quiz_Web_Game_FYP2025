from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from fastapi.middleware.cors import CORSMiddleware

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
    LeaderboardEntry
)

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
def get_random_question(db: Session = Depends(get_db)):
    stmt = select(QuestionDB).order_by(func.random()).limit(1) #uses a function to get one random question from the QestionDB table 
    db_random_question = db.execute(stmt).scalars().first() #.execute - runs query, .scalars - returns values in the rows, .first - first row is returned. **this is only used fr get randm
    if not db_random_question:
        raise HTTPException(status_code=404, detail="No questions available") #returns error if a question can't be found
    return QuestionReadPublic.model_validate(db_random_question) #returns the random question without the answer

#Gets a specific Question which the frontend will use to validate correct answers
@app.get("/api/questions/{question_id}", response_model=QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(QuestionDB, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@app.post("/api/questions", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
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
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.get(QuestionDB, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

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


