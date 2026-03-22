def test_add_user_run_creates_row(client):
    response = client.post(
        "/api/users/7/runs",
        json={"score": 5, "streak": 3, "total_questions": 8, "category": "History"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == 7
    assert body["score"] == 5
    assert body["streak"] == 3
    assert body["total_questions"] == 8
    assert body["category"] == "History"


def test_add_user_run_validation_422(client):
    response = client.post(
        "/api/users/7/runs",
        json={"score": -1, "streak": 3, "total_questions": 8, "category": "History"},
    )

    assert response.status_code == 422


def test_get_user_stats_returns_zeroes_when_user_has_no_runs(client):
    response = client.get("/api/users/77/stats")

    assert response.status_code == 200
    assert response.json() == {
        "high_score": 0,
        "longest_streak": 0,
        "average_score": 0.0,
        "games_played": 0,
    }


def test_get_user_stats_aggregates_only_requested_user(client, add_run):
    add_run(user_id=10, score=4, streak=1, total_questions=8, category="History")
    add_run(user_id=10, score=8, streak=4, total_questions=8, category="History")
    add_run(user_id=10, score=6, streak=2, total_questions=8, category="Science")
    add_run(user_id=11, score=99, streak=99, total_questions=8, category="Sports")

    response = client.get("/api/users/10/stats")

    assert response.status_code == 200
    assert response.json() == {
        "high_score": 8,
        "longest_streak": 4,
        "average_score": 6.0,
        "games_played": 3,
    }


def test_leaderboard_returns_best_score_and_best_streak_per_user_in_rank_order(client, add_run):
    add_run(user_id=1, score=5, streak=3, total_questions=8, category="History")
    add_run(user_id=1, score=9, streak=4, total_questions=8, category="History")
    add_run(user_id=2, score=9, streak=6, total_questions=8, category="Science")
    add_run(user_id=2, score=7, streak=2, total_questions=8, category="Science")
    add_run(user_id=3, score=4, streak=4, total_questions=8, category="Sports")

    response = client.get("/api/leaderboard")

    assert response.status_code == 200
    assert response.json() == [
        {"user_id": 2, "best_score": 9, "best_streak": 6},
        {"user_id": 1, "best_score": 9, "best_streak": 4},
        {"user_id": 3, "best_score": 4, "best_streak": 4},
    ]


def test_leaderboard_returns_empty_list_when_no_runs_exist(client):
    response = client.get("/api/leaderboard")

    assert response.status_code == 200
    assert response.json() == []