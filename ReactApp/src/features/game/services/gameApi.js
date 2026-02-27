import axios from "axios";
const API_BASE_URL = "/api";

export async function startGame({ category, difficulty }) {
  const res = await axios.post(`${API_BASE_URL}/game/start`, { category, difficulty });
  return res.data;
}

export async function validatePlacement({ placedQuestionId, leftNeighborId, rightNeighborId }) {
  const res = await fetch("/api/game/validate-placement", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      placed_question_id: placedQuestionId,
      left_neighbor_id: leftNeighborId ?? null,
      right_neighbor_id: rightNeighborId ?? null,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`validatePlacement failed: ${res.status} ${text}`);
  }
  return res.json();
}