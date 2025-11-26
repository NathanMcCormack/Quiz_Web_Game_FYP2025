import React, { useEffect, useState } from "react"; //useState lets the component store values and update them, useEffect... 
import { fetchRandomQuestion, fetchQuestionById } from "./api"; //importing our two functions for fetching questions 
import "./QuestionPlacement.css";
import { FaInfinity } from "react-icons/fa6"; //Infintity Logo from React-Icons website
//imports from dnd website 
import { DndContext, closestCenter } from "@dnd-kit/core";

import {
  SortableContext,
  useSortable,
  arrayMove,
  horizontalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";


function QuestionPlacement() {
  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null); //setting usestate to NULL, to start off with currentQuestion

const [lineQuestions, setLineQuestions] = useState([]);

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
    <div className="page-center">
      <div className="qp-card">
        <h1>Question Placement Testing</h1>

        <div className="number-line">
          <p className="current-question" draggable="true">
            <strong>Current question:</strong>{" "}
            {currentQuestion ? currentQuestion.question : "Loading..."}
          </p>
          <strong>Score:</strong> {score}
        </div>

        {message && (
          <p>
            <strong>Message:</strong> {message} 
          </p>
        )}

        <p>
          <strong>Positions array:</strong>
        </p>
        <div className="number-line">
          <div className="number-box">0</div>
          <div className="number-box" ><FaInfinity/></div>
        </div>

        <button className="qp-button" onClick={loadNextQuestion}>Load another random question</button>

      </div>
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
