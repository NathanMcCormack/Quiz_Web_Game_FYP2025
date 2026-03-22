# ---------------- Health Check ---------------------
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ------------ Question tests --------------
def test_get_random_question_empty_returns_404(client):
    response = client.get("/api/questions/random")
    assert response.status_code == 404
    assert response.json() == {"detail": "No questions available"}


def test_list_questions_empty(client):
    response = client.get("/api/questions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_question(client, create_question):
    created = create_question(
        question="When was the Declaration of Independence signed?",
        answer=1776,
        category="History",
        difficulty="easy",
    )

    assert "id" in created
    assert created["answer"] == 1776

    response = client.get(f"/api/questions/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["answer"] == 1776


def test_create_question_validation_422(client):
    response = client.post(
        "/api/questions",
        json={
            "question": "Testing",
            "answer": -1,
            "category": "History",
            "difficulty": "easy",
        },
    )
    assert response.status_code == 422

    response = client.post(
        "/api/questions",
        json={
            "question": "Testing",
            "answer": 1,
            "category": "01010101",
            "difficulty": "easy",
        },
    )
    assert response.status_code == 422

    response = client.post(
        "/api/questions",
        json={
            "question": "Bad difficulty",
            "answer": 1,
            "category": "History",
            "difficulty": "impossible",
        },
    )
    assert response.status_code == 422


def test_get_question_not_found(client):
    response = client.get("/api/questions/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_put_update_question(client, create_question):
    question = create_question(question="Q1", answer=10, category="History", difficulty="easy")

    response = client.put(
        f"/api/questions/{question['id']}",
        json={
            "question": "Q1 updated",
            "answer": 11,
            "category": "History",
            "difficulty": "medium",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == question["id"]
    assert body["answer"] == 11
    assert body["difficulty"] == "medium"


def test_put_update_question_not_found(client):
    response = client.put(
        "/api/questions/12345",
        json={"question": "X", "answer": 1, "category": "History", "difficulty": "easy"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_patch_question_updates_only_supplied_fields(client, create_question):
    question = create_question(
        question="Original question",
        answer=1950,
        category="History",
        difficulty="easy",
    )

    response = client.patch(
        f"/api/questions/{question['id']}",
        json={"difficulty": "hard", "answer": 1960},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == question["id"]
    assert body["question"] == "Original question"
    assert body["category"] == "History"
    assert body["difficulty"] == "hard"
    assert body["answer"] == 1960


def test_patch_question_not_found(client):
    response = client.patch("/api/questions/9999", json={"difficulty": "medium"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_patch_question_validation_422(client, create_question):
    question = create_question(question="Q1", answer=10, category="History", difficulty="easy")

    response = client.patch(
        f"/api/questions/{question['id']}",
        json={"difficulty": "legendary"},
    )
    assert response.status_code == 422


def test_random_question_can_filter_by_category_difficulty_and_session(client, create_question, db_session):
    first = create_question(
        question="History easy",
        answer=1901,
        category="History",
        difficulty="easy",
    )
    second = create_question(
        question="Science hard",
        answer=2005,
        category="Science",
        difficulty="hard",
    )

    client.patch(f"/api/questions/{first['id']}", json={"category": "History", "difficulty": "easy"})
    client.patch(f"/api/questions/{second['id']}", json={"category": "Science", "difficulty": "hard"})

    import app.GameMain as game_main

    history_question = db_session.get(game_main.QuestionDB, first["id"])
    science_question = db_session.get(game_main.QuestionDB, second["id"])
    history_question.game_session_id = "session-history"
    science_question.game_session_id = "session-science"
    db_session.commit()

    response = client.get(
        "/api/questions/random",
        params={
            "category": "History",
            "difficulty": "easy",
            "game_session_id": "session-history",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == first["id"]
    assert body["question"] == "History easy"
    assert "answer" not in body


def test_random_question_returns_404_when_filters_do_not_match(client, create_question):
    create_question(question="Only question", answer=20, category="History", difficulty="easy")

    response = client.get(
        "/api/questions/random",
        params={"category": "Science", "difficulty": "hard"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "No questions available"}


def test_delete_question_and_then_404(client, create_question):
    question = create_question(question="Q1", answer=10, category="History", difficulty="easy")

    response = client.delete(f"/api/questions/{question['id']}")
    assert response.status_code == 204
    assert response.text == ""

    response = client.get(f"/api/questions/{question['id']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}


def test_delete_question_not_found(client):
    response = client.delete("/api/questions/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Question not found"}