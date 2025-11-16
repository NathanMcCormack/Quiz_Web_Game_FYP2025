import React, { useEffect, useState } from "react"; //useState lets the component store values and update them, useEffect... 
import { fetchRandomQuestion, fetchQuestionById } from "./api"; //importing our two functions for fetching questions 

function QuestionPlacement() {

  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null); //setting usestate to NULL, to start off with currentQuestion

  // The number line, setting just 0 and infinity in here first 
  const [positions, setPositions] = useState([//setPositions wil be used later as the positions of the cards will be changing
    { id: "zero", label: "0", type: "boundary", value: 0 },
    {id: "infinity", label: "∞", type: "boundary", value: Number.POSITIVE_INFINITY,},
  ]);

  const [score, setScore] = useState(0);   //players score

  const [message, setMessage] = useState(""); //used for feedback errors

  async function loadNextQuestion() {
    try {
      const q = await fetchRandomQuestion(); //call our function sto call a question from the backend
      console.log("Loaded random question: ", q); //message to the console 
      setCurrentQuestion(q);
      setMessage("");
    } catch (err) { //if it fails to get a question form the backend, the error message below will be returned
      console.error("Failed to load random question: ", err);
      setMessage("Could not load question from backend.");
    }
  }


  useEffect(() => {loadNextQuestion();}, []); //this run safter the initial render of the webpage. the empty array tells it to only run once 

//What will show up on the webpage - everything inside div.
  return (
    <div>
      <h1>Question Placement Testing</h1>

      <p>
        <strong>Score:</strong> {score}
      </p>

      <p id="p1" draggable="true">This Test is draggable.</p>

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
//{currentQuestion ? currentQuestion.question : "Loading..."} if currentQuestion is not null - show the question. Otherwise disaplay "Loading..."

//If the "message" is empty tgen it displays nothing, otherwise it will display the message 
// {message && (
//   <p>
//     <strong>Message:</strong> {message} 
//   </p>
// )}

export default QuestionPlacement;
