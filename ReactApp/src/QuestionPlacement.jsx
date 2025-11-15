// ReactApp/src/QuestionPlacement.jsx

import React, { useEffect, useState } from "react";
import { fetchRandomQuestion, fetchQuestionById } from "./api";

function QuestionPlacement() {

  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null);

  // The number line: [0, Q1, Q2, ..., ∞]
  const [positions, setPositions] = useState([
    { id: "zero", label: "0", type: "boundary", value: 0 },
    {id: "infinity", label: "∞", type: "boundary", value: Number.POSITIVE_INFINITY,},
  ]);

  // Score for the player
  const [score, setScore] = useState(0);

  // Feedback / error messages
  const [message, setMessage] = useState("");

  // STEP 5.2 – load the first random question (and every time we want a new one)

  async function loadNextQuestion() {
    try {
      const q = await fetchRandomQuestion();
      console.log("Loaded random question: ", q);
      setCurrentQuestion(q);
      setMessage("");
    } catch (err) {
      console.error("Failed to load random question: ", err);
      setMessage("Could not load question from backend.");
    }
  }

  // Run once when the component mounts
  useEffect(() => {
    loadNextQuestion();
  }, []);

  // For now, just render some basic info so you can see state updates.
  // We'll replace this later with the full drag & drop UI.
  return (
    <div>
      <h1>Question Placement Testing</h1>

      <p>
        <strong>Score:</strong> {score}
      </p>

      <p>
        <strong>Current question:</strong>{" "}
        {currentQuestion ? currentQuestion.question : "Loading..."}
      </p>

      {message && (
        <p>
          <strong>Message:</strong> {message}
        </p>
      )}

      <p>
        <strong>Positions array:</strong>
      </p>
      <pre>{JSON.stringify(positions, null, 2)}</pre>

      <button onClick={loadNextQuestion}>Load another random question</button>
    </div>
  );
}

export default QuestionPlacement;
