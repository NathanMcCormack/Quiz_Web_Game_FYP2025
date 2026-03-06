export async function generateTodayDaily() {
  const res = await fetch("/api/daily/generate-today", { method: "POST" });
  if (!res.ok && res.status !== 409) {
    const text = await res.text();
    throw new Error(`generateTodayDaily failed: ${res.status} ${text}`);
  }
}

export async function fetchTodayDaily() {
  const res = await fetch("/api/daily/today");
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`fetchTodayDaily failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function validateDailyPlacement({placedQuestionId,leftNeighborId,rightNeighborId,}) {
  const res = await fetch("/api/daily/validate-placement", {
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
    throw new Error(`validateDailyPlacement failed: ${res.status} ${text}`);
  }
  return res.json();
}