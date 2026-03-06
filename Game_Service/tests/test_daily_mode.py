from app.GameModels import DailyChallengeDB, DailyQuestionDB, DailyCategoryDB


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

    monkeypatch.setattr(
        "app.DailyMode.generate_questions",
        fake_generate_questions
    )

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

    monkeypatch.setattr(
        "app.DailyMode.generate_questions",
        fake_generate_questions
    )

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

    monkeypatch.setattr(
        "app.DailyMode.generate_questions",
        fake_generate_questions
    )

    headers = {"X-Daily-Job-Token": "test-token"}

    r = client.post("/api/daily/generate-today", headers=headers)
    assert r.status_code == 502
    assert "Failed to generate questions" in r.text