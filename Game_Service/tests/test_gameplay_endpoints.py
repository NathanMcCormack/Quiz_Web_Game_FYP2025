from types import SimpleNamespace


def test_start_game_creates_session_questions_and_hides_answers(client, monkeypatch):
    def fake_generate_questions(*, category, difficulty, count):
        return [
            SimpleNamespace(
                question=f"Question {index}",
                answer=1900 + index,
                category=category,
                difficulty=difficulty,
            )
            for index in range(count)
        ]

    monkeypatch.setattr("app.GameMain.generate_questions", fake_generate_questions)

    response = client.post(
        "/api/game/start",
        json={"category": "History", "difficulty": "easy"},
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["session_id"], str)
    assert len(body["questions"]) == 8
    assert all(question["difficulty"] == "easy" for question in body["questions"])
    assert all(question["category"] == "History" for question in body["questions"])
    assert all("answer" not in question for question in body["questions"])


def test_start_game_returns_502_when_generation_fails(client, monkeypatch):
    def fake_generate_questions(*, category, difficulty, count):
        raise RuntimeError("OpenAI generation failed")

    monkeypatch.setattr("app.GameMain.generate_questions", fake_generate_questions)

    response = client.post(
        "/api/game/start",
        json={"category": "History", "difficulty": "easy"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Failed to generate questions: OpenAI generation failed"


def test_validate_placement_returns_404_when_placed_question_missing(client):
    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": 999, "left_neighbor_id": None, "right_neighbor_id": None},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Placed question not found"}


def test_validate_placement_returns_404_when_left_neighbor_missing(client, create_question):
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": 999, "right_neighbor_id": None},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Left neighbor question not found"}


def test_validate_placement_returns_404_when_right_neighbor_missing(client, create_question):
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": None, "right_neighbor_id": 999},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Right neighbor question not found"}


def test_validate_placement_with_no_neighbors_is_always_correct(client, create_question):
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": None, "right_neighbor_id": None},
    )

    assert response.status_code == 200
    assert response.json() == {
        "correct": True,
        "placed_answer": 10,
        "left_answer": None,
        "right_answer": None,
    }


def test_validate_placement_with_only_right_neighbor_uses_upper_bound(client, create_question):
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")
    right = create_question(question="Right", answer=12, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": None, "right_neighbor_id": right["id"]},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_validate_placement_with_only_right_neighbor_can_fail(client, create_question):
    placed = create_question(question="Placed", answer=15, category="History", difficulty="easy")
    right = create_question(question="Right", answer=12, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": None, "right_neighbor_id": right["id"]},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is False


def test_validate_placement_with_only_left_neighbor_uses_lower_bound(client, create_question):
    left = create_question(question="Left", answer=8, category="History", difficulty="easy")
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": left["id"], "right_neighbor_id": None},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is True


def test_validate_placement_with_only_left_neighbor_can_fail(client, create_question):
    left = create_question(question="Left", answer=18, category="History", difficulty="easy")
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": left["id"], "right_neighbor_id": None},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is False


def test_validate_placement_with_both_neighbors_accepts_value_in_range(client, create_question):
    left = create_question(question="Left", answer=8, category="History", difficulty="easy")
    placed = create_question(question="Placed", answer=10, category="History", difficulty="easy")
    right = create_question(question="Right", answer=12, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": left["id"], "right_neighbor_id": right["id"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "correct": True,
        "placed_answer": 10,
        "left_answer": 8,
        "right_answer": 12,
    }


def test_validate_placement_with_both_neighbors_rejects_value_outside_range(client, create_question):
    left = create_question(question="Left", answer=8, category="History", difficulty="easy")
    placed = create_question(question="Placed", answer=15, category="History", difficulty="easy")
    right = create_question(question="Right", answer=12, category="History", difficulty="easy")

    response = client.post(
        "/api/game/validate-placement",
        json={"placed_question_id": placed["id"], "left_neighbor_id": left["id"], "right_neighbor_id": right["id"]},
    )

    assert response.status_code == 200
    assert response.json()["correct"] is False