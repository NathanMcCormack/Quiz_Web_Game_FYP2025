def test_get_daily_today_404_when_missing(client):
    r = client.get("/api/daily/today")
    assert r.status_code == 404


def test_generate_today_creates_challenge_and_questions(client, monkeypatch):
    class FakeQuestion:
        def __init__(self, question, answer, category, difficulty):
            self.question = question
            self.answer = answer
            self.category = category
            self.difficulty = difficulty

    def fake_generate_questions(*, category, difficulty, count):
        return [
            FakeQuestion(
                question=f"Question {i}",
                answer=1900 + i,
                category=category,
                difficulty=difficulty,
            )
            for i in range(count)
        ]

    monkeypatch.setattr("app.DailyMode.generate_questions", fake_generate_questions)

    headers = {"X-Daily-Job-Token": "test-token"}

    r = client.post("/api/daily/generate-today", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "created"

    r2 = client.get("/api/daily/today")
    assert r2.status_code == 200
    daily = r2.json()

    assert len(daily["questions"]) == 8
    assert "answer" not in daily["questions"][0]


def test_generate_today_is_idempotent(client, monkeypatch):
    class FakeQuestion:
        def __init__(self, question, answer, category, difficulty):
            self.question = question
            self.answer = answer
            self.category = category
            self.difficulty = difficulty

    def fake_generate_questions(*, category, difficulty, count):
        return [
            FakeQuestion(
                question=f"Question {i}",
                answer=1900 + i,
                category=category,
                difficulty=difficulty,
            )
            for i in range(count)
        ]

    monkeypatch.setattr("app.DailyMode.generate_questions", fake_generate_questions)

    headers = {"X-Daily-Job-Token": "test-token"}

    r1 = client.post("/api/daily/generate-today", headers=headers)
    assert r1.status_code == 200
    assert r1.json()["status"] == "created"

    r2 = client.post("/api/daily/generate-today", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "already_exists"


def test_generate_today_marks_failed_on_generator_error(client, monkeypatch):
    def fake_generate_questions(*, category, difficulty, count):
        raise RuntimeError("OpenAI generation failed")

    monkeypatch.setattr("app.DailyMode.generate_questions", fake_generate_questions)

    headers = {"X-Daily-Job-Token": "test-token"}

    r = client.post("/api/daily/generate-today", headers=headers)
    assert r.status_code == 502
    assert "Failed to generate questions" in r.text

    # -------- Legacy / History Endpoint Tests --------

from datetime import date, timedelta
from app.GameModels import DailyChallengeDB, DailyQuestionDB


def _make_challenge(db, challenge_date, category="History", difficulty="easy", status="success"):
    """Helper: seed a DailyChallengeDB row directly."""
    c = DailyChallengeDB(
        challenge_date=challenge_date,
        category=category,
        difficulty=difficulty,
        status=status,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _make_daily_question(db, challenge_id, index=0):
    """Helper: seed a DailyQuestionDB row directly."""
    q = DailyQuestionDB(
        daily_challenge_id=challenge_id,
        question=f"Question {index}",
        answer=1900 + index,
        category="History",
        difficulty="easy",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def test_list_past_challenges_returns_empty_when_no_history(client):
    response = client.get("/api/daily/history")
    assert response.status_code == 200
    assert response.json() == []


def test_list_past_challenges_returns_only_successful_past_challenges(client, db_session):
    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    _make_challenge(db_session, yesterday, status="success")
    _make_challenge(db_session, two_days_ago, status="failed")

    response = client.get("/api/daily/history")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["challenge_date"] == str(yesterday)


def test_list_past_challenges_excludes_today(client, db_session):
    today = date.today()
    yesterday = today - timedelta(days=1)

    _make_challenge(db_session, today, status="success")
    _make_challenge(db_session, yesterday, status="success")

    response = client.get("/api/daily/history")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["challenge_date"] == str(yesterday)


def test_list_past_challenges_ordered_most_recent_first(client, db_session):
    today = date.today()
    days = [today - timedelta(days=i) for i in range(1, 4)]

    for d in days:
        _make_challenge(db_session, d, status="success")

    response = client.get("/api/daily/history")
    assert response.status_code == 200
    body = response.json()
    dates = [entry["challenge_date"] for entry in body]
    assert dates == sorted(dates, reverse=True)


def test_get_past_challenge_returns_questions_without_answers(client, db_session):
    yesterday = date.today() - timedelta(days=1)
    challenge = _make_challenge(db_session, yesterday)

    for i in range(3):
        _make_daily_question(db_session, challenge.id, index=i)

    response = client.get(f"/api/daily/history/{yesterday}")
    assert response.status_code == 200
    body = response.json()
    assert body["challenge_date"] == str(yesterday)
    assert body["category"] == "History"
    assert len(body["questions"]) == 3
    assert all("answer" not in q for q in body["questions"])


def test_get_past_challenge_returns_404_for_unknown_date(client):
    response = client.get("/api/daily/history/2000-01-01")
    assert response.status_code == 404
    assert response.json() == {"detail": "No challenge found for this date"}


def test_get_past_challenge_returns_404_when_status_is_not_success(client, db_session):
    yesterday = date.today() - timedelta(days=1)
    _make_challenge(db_session, yesterday, status="failed")

    response = client.get(f"/api/daily/history/{yesterday}")
    assert response.status_code == 404


def test_get_past_challenge_returns_422_for_invalid_date_format(client):
    response = client.get("/api/daily/history/not-a-date")
    assert response.status_code == 422