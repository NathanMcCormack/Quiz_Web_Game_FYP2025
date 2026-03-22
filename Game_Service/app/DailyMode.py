# Game_Service/app/DailyMode.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timezone
from .GameDatabase import SessionLocal
from .GameModels import DailyChallengeDB, DailyQuestionDB, DailyCategoryDB
from .GameSchemas import (
    DailyChallengePublic,
    DailyQuestionPublic,
    DailyValidatePlacementRequest,
    DailyValidatePlacementResponse,
    DailyCategoryRead,
    DailyCategoryCreate,
    DailyChallengeListEntry,
)
from .QuestionGenerator import generate_questions
import os
import secrets

router = APIRouter(prefix="/api/daily", tags=["daily"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_utc_today() -> date:
    return datetime.now(timezone.utc).date()


def difficulty_for_date(d: date) -> str:
    cycle = ["easy", "medium", "hard"]
    return cycle[d.toordinal() % 3]


def verify_daily_job_token(x_daily_job_token: str = Header(default="")):
    expected = os.getenv("DAILY_JOB_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="DAILY_JOB_TOKEN is not configured")

    if not secrets.compare_digest(x_daily_job_token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


def ensure_categories_seeded(db: Session):
    existing = db.execute(select(DailyCategoryDB)).scalars().first()
    if existing:
        return

    defaults = [
        "History",
        "Space",
        "Movies",
        "Football",
        "Music",
        "Science",
        "Geography",
        "Technology",
    ]
    for name in defaults:
        db.add(DailyCategoryDB(name=name))
    db.commit()


def pick_unused_category(db: Session) -> str:
    ensure_categories_seeded(db)

    cat = db.execute(
        select(DailyCategoryDB)
        .where(DailyCategoryDB.is_used == False)
        .order_by(func.random())
    ).scalars().first()

    if not cat:
        # Reset if all categories have been used
        cats = db.execute(select(DailyCategoryDB)).scalars().all()
        for c in cats:
            c.is_used = False
            c.used_at = None
        db.commit()

        cat = db.execute(
            select(DailyCategoryDB)
            .where(DailyCategoryDB.is_used == False)
            .order_by(func.random())
        ).scalars().first()

    if not cat:
        raise HTTPException(status_code=500, detail="No categories available")

    cat.is_used = True
    cat.used_at = get_utc_today()
    db.commit()
    return cat.name


# -------- Daily Mode Endpoints --------

@router.post("/generate-today")
def generate_today(
    db: Session = Depends(get_db),
    _auth: None = Depends(verify_daily_job_token),
):
    """
    Creates today's daily challenge once, using the UTC date.
    If it already exists and succeeded, return a non-error response.
    """
    today = get_utc_today()

    existing = db.execute(
        select(DailyChallengeDB).where(DailyChallengeDB.challenge_date == today)
    ).scalars().first()

    if existing:
        if existing.status == "success":
            return {
                "status": "already_exists",
                "date": str(today),
                "category": existing.category,
                "difficulty": existing.difficulty,
            }
        raise HTTPException(
            status_code=409,
            detail="Daily challenge already exists for today but is not in success state",
        )

    difficulty = difficulty_for_date(today)
    category = pick_unused_category(db)

    challenge = DailyChallengeDB(
        challenge_date=today,
        category=category,
        difficulty=difficulty,
        status="pending",
    )
    db.add(challenge)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Daily challenge already exists for today")

    db.refresh(challenge)

    try:
        generated = generate_questions(category=category, difficulty=difficulty, count=8)
    except Exception as e:
        challenge.status = "failed"
        challenge.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=502, detail=f"Failed to generate questions: {str(e)}")

    for q in generated:
        db.add(
            DailyQuestionDB(
                daily_challenge_id=challenge.id,
                question=q.question,
                answer=q.answer,
                category=q.category,
                difficulty=q.difficulty,
            )
        )

    challenge.status = "success"
    challenge.error_message = None
    db.commit()

    return {
        "status": "created",
        "date": str(today),
        "category": category,
        "difficulty": difficulty,
    }


@router.get("/today", response_model=DailyChallengePublic)
def get_today(db: Session = Depends(get_db)):
    today = get_utc_today()

    challenge = db.execute(
        select(DailyChallengeDB).where(DailyChallengeDB.challenge_date == today)
    ).scalars().first()

    if not challenge or challenge.status != "success":
        raise HTTPException(status_code=404, detail="Daily challenge not available yet")

    questions = db.execute(
        select(DailyQuestionDB)
        .where(DailyQuestionDB.daily_challenge_id == challenge.id)
        .order_by(DailyQuestionDB.id)
    ).scalars().all()

    # Convert to public schema (NO answer field)
    public_questions = [DailyQuestionPublic.model_validate(q) for q in questions]

    return DailyChallengePublic(
        challenge_date=challenge.challenge_date,
        category=challenge.category,
        difficulty=challenge.difficulty,
        questions=public_questions,
    )

router.get("/history", response_model=list[DailyChallengeListEntry])
def list_past_challenges(db: Session = Depends(get_db)):
    """
    Returns all past daily challenges that successfully generated questions,
    ordered most recent first. Excludes today.
    """
    today = get_utc_today()
    challenges = db.execute(
        select(DailyChallengeDB)
        .where(DailyChallengeDB.status == "success")
        .where(DailyChallengeDB.challenge_date < today)
        .order_by(DailyChallengeDB.challenge_date.desc())
    ).scalars().all()
    return challenges


@router.get("/history/{challenge_date}", response_model=DailyChallengePublic)
def get_past_challenge(challenge_date: date, db: Session = Depends(get_db)):
    """
    Returns a specific past challenge by date including its questions (no answers).
    Returns 404 if the date has no successful challenge.
    """
    challenge = db.execute(
        select(DailyChallengeDB)
        .where(DailyChallengeDB.challenge_date == challenge_date)
        .where(DailyChallengeDB.status == "success")
    ).scalars().first()

    if not challenge:
        raise HTTPException(status_code=404, detail="No challenge found for this date")

    questions = db.execute(
        select(DailyQuestionDB)
        .where(DailyQuestionDB.daily_challenge_id == challenge.id)
        .order_by(DailyQuestionDB.id)
    ).scalars().all()

    public_questions = [DailyQuestionPublic.model_validate(q) for q in questions]

    return DailyChallengePublic(
        challenge_date=challenge.challenge_date,
        category=challenge.category,
        difficulty=challenge.difficulty,
        questions=public_questions,
    )

@router.post("/validate-placement", response_model=DailyValidatePlacementResponse)
def validate_daily(payload: DailyValidatePlacementRequest, db: Session = Depends(get_db)):
    placed = db.get(DailyQuestionDB, payload.placed_question_id)
    if not placed:
        raise HTTPException(status_code=404, detail="Placed question not found")

    left = db.get(DailyQuestionDB, payload.left_neighbor_id) if payload.left_neighbor_id is not None else None
    if payload.left_neighbor_id is not None and not left:
        raise HTTPException(status_code=404, detail="Left neighbor question not found")

    right = db.get(DailyQuestionDB, payload.right_neighbor_id) if payload.right_neighbor_id is not None else None
    if payload.right_neighbor_id is not None and not right:
        raise HTTPException(status_code=404, detail="Right neighbor question not found")

    placed_answer = placed.answer
    left_answer = left.answer if left else None
    right_answer = right.answer if right else None

    if left is None and right is None:
        correct = True
    elif left is None:
        correct = placed_answer <= right_answer
    elif right is None:
        correct = left_answer <= placed_answer
    else:
        correct = left_answer <= placed_answer <= right_answer

    return DailyValidatePlacementResponse(
        correct=correct,
        placed_answer=placed_answer,
        left_answer=left_answer,
        right_answer=right_answer,
    )


@router.get("/categories", response_model=list[DailyCategoryRead])
def list_daily_categories(db: Session = Depends(get_db)):
    cats = db.execute(select(DailyCategoryDB).order_by(DailyCategoryDB.id)).scalars().all()
    return cats


@router.post("/categories", status_code=status.HTTP_201_CREATED, response_model=DailyCategoryRead)
def create_daily_category(payload: DailyCategoryCreate, db: Session = Depends(get_db)):
    cat = DailyCategoryDB(name=payload.name, is_used=False, used_at=None)
    db.add(cat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Daily category already exists")
    db.refresh(cat)
    return cat