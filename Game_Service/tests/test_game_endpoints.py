import pytest

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


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

#------------Question tests --------------
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