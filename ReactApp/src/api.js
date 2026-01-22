//Axio sends HTTP reuqests to a server (FastAPI/uvicorn) and receives data back from it 
//axios client side -> client sends requests 
//uvicorn server side -> waits and handles incoming requests
import axios from "axios";
const API_BASE_URL = "/api"; //Allows to easily change the URL in the future if needed

export async function fetchRandomQuestion() {
  const res = await axios.get(`${API_BASE_URL}/questions/random`);  //in main -> @app.get("/api/questions/random", response_model=QuestionReadPublic), stores response in "res"
  return res.data; // { id, question, category, difficulty } **doesnt show the answer**
}

export async function fetchQuestionById(id) {
  const res = await axios.get(`${API_BASE_URL}/questions/${id}`);
  return res.data; // { id, question, answer, ... }
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