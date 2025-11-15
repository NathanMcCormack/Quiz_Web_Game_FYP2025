import axios from "axios";
const API_BASE_URL = "/api";

export async function fetchRandomQuestion() {
  const res = await axios.get(`${API_BASE_URL}/questions/random`);  //in main -> @app.get("/api/questions/random", response_model=QuestionReadPublic)
  return res.data; // { id, question, category, difficulty }
}

export async function fetchQuestionById(id) {
  const res = await axios.get(`${API_BASE_URL}/questions/${id}`);
  return res.data; // { id, question, answer, ... }
}
