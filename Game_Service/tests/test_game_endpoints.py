import pytest

#---------------- Health Check ---------------------
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

#------------Question tests --------------
def _create_question(client, *, question: str, answer: int, category: str = "General Knowledge", difficulty: str = "easy"):
    payload = {
        "question": question,
        "answer": answer,
        "category": category,
        "difficulty": difficulty,
    }
    r = client.post("/api/questions", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

def _add_run(client, *, user_id: int, score: int, streak: int, total_questions: int | None = None, category: str | None = None):
    payload = {
        "score": score,
        "streak": streak,
        "total_questions": total_questions,
        "category": category,
    }
    r = client.post(f"/api/users/{user_id}/runs", json=payload)
    assert r.status_code == 201, r.text
    return r.json()

def test_get_random_question_empty_returns_404(client):
    r = client.get("/api/questions/random")
    assert r.status_code == 404
    assert r.json() == {"detail": "No questions available"}

def test_list_questions_empty(client):
    r = client.get("/api/questions")
    assert r.status_code == 200
    assert r.json() == []

def test_create_and_get_question(client):
    created = _create_question(
        client,
        question="When was the Declaration of Independence signed?",
        answer=1776,
        category="History",
        difficulty="easy",
    )

    assert "id" in created
    assert created["answer"] == 1776

    r = client.get(f"/api/questions/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]
    assert r.json()["answer"] == 1776

def test_create_question_validation_422(client):
    # Negative answer should fail (Ge(0))
    r = client.post(
        "/api/questions",
        json={
            "question": "Testing",
            "answer": -1,
            "category": "History",
            "difficulty": "easy",
        },
    )
    assert r.status_code == 422

    # category must be letters= only 
    r = client.post(
        "/api/questions",
        json={
            "question": "Testing",
            "answer": 1,
            "category": "01010101",
            "difficulty": "easy",
        },
    )
    assert r.status_code == 422

    # difficulty must be only: easy, medium, hard
    r = client.post(
        "/api/questions",
        json={
            "question": "Bad difficulty",
            "answer": 1,
            "category": "History",
            "difficulty": "impossible",
        },
    )
    assert r.status_code == 422

def test_get_question_not_found(client):
    r = client.get("/api/questions/9999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Question not found"}

def test_put_update_question(client):
    q = _create_question(client, question="Q1", answer=10, category="History", difficulty="easy")

    r = client.put(
        f"/api/questions/{q['id']}",
        json={"question": "Q1 updated", "answer": 11, "category": "History", "difficulty": "medium"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == q["id"]
    assert body["answer"] == 11
    assert body["difficulty"] == "medium"


def test_put_update_question_not_found(client):
    r = client.put(
        "/api/questions/12345",
        json={"question": "X", "answer": 1, "category": "History", "difficulty": "easy"},
    )
    assert r.status_code == 404
    assert r.json() == {"detail": "Question not found"}    


def test_delete_question_and_then_404(client):
    q = _create_question(client, question="Q1", answer=10, category="History", difficulty="easy")

    r = client.delete(f"/api/questions/{q['id']}")
    assert r.status_code == 204
    assert r.text == ""

    r = client.get(f"/api/questions/{q['id']}")
    assert r.status_code == 404
    assert r.json() == {"detail": "Question not found"}

def test_delete_question_not_found(client):
    r = client.delete("/api/questions/9999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Question not found"}

