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
