import React, { useEffect, useState } from "react"; //useState lets the component store values and update them, useEffect... 
import { fetchRandomQuestion, fetchQuestionById } from "./api"; //importing our two functions for fetching questions 
import "./QuestionPlacement.css";
import { FaInfinity } from "react-icons/fa6"; //Infintity Logo from React-Icons website
//imports from dnd website 
import { DndContext, closestCenter, useDraggable, useDroppable } from "@dnd-kit/core";


function QuestionPlacement() {
  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null); //setting usestate to NULL, to start off with currentQuestion
  const [lineQuestions, setLineQuestions] = useState([]);
  const [score, setScore] = useState(0);   //players score
  const [message, setMessage] = useState(""); //used for feedback errors

  function handleDragEnd(dragEvent) {
    const { active, over } = dragEvent;

    // If we didn't drop over anything, do nothing
    if (!over) {
      return;
    }

    // We only care about the current question card
    if (active.id !== "current-card") {
      return;
    }

    // If for some reason there's no question loaded, bail
    if (!currentQuestion) {
      return;
    }

    // over.id will look like "slot-0", "slot-1", ...
    const slotId = over.id;
    if (!slotId.startsWith("slot-")) {
      return;
    }

    const indexString = slotId.replace("slot-", "");
    const insertIndex = parseInt(indexString, 10);
    if (Number.isNaN(insertIndex)) {
      return;
    }

    // Build a new "fixed" card for the line
    const newCard = {
      id: `line-${currentQuestion.id ?? Date.now()}-${Math.random()
        .toString(36)
        .slice(2)}`,
      question: currentQuestion,
    };

    // Insert this card into lineQuestions at the chosen position
    setLineQuestions((prev) => {
      const next = [...prev];
      next.splice(insertIndex, 0, newCard);
      return next;
    });

    // Increase score by 1
    setScore((prevScore) => prevScore + 1);

    // Clear current card so it can't be dragged again
    setCurrentQuestion(null);

    // Load the next question from the backend
    loadNextQuestion();
  }

  function CurrentQuestionCard({question}){
    const { attributes, listeners, setNodeRef, transform, isDragging } =
      useDraggable({
        id: "current-card",
        disabled: !question, // dont drag when no question
    });

    const style = {
      transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
      opacity: isDragging ? 0.8 : 1, //if dragging opacacity becomes .8 to be more obvious that user is dragging card
      cursor: question ? "grab" : "default", //if the cursor is over the question, it will have a grab icon 
    };

  return (
    <div ref={setNodeRef} style={style} className="current-question" {...attributes} {...(question ? listeners : {})}>
      <strong>Current question:</strong>
      <div className="current-question-text">
        {question ? question.question : "Loading..."}
      </div>
      <p className="current-question-hint">
        Drag this card and drop it between 0 and ∞
      </p>
    </div>
  );
  }

 function DroppableSlot({slotIndex}){
    const { setNodeRef, isOver } = useDroppable({ id: `slot-${slotIndex}`});

    return (
      <div ref={setNodeRef} className={`drop-slot ${isOver ? "drop-slot--active" : ""}`}/>
    );
  } 

 function LineQuestions({lineQuestions}){
  return (
    <>
      {lineQuestions.map((item, index) => (
        <React.Fragment key={item.id}>
          <DroppableSlot slotIndex={index} />
          <div className="number-box line-question-box">
            {item.question?.question ?? "Question"}
          </div>
        </React.Fragment>
      ))}

      {/* Final slot after the last question */}
      <DroppableSlot slotIndex={lineQuestions.length} />
    </>
  );
} 

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
     <DndContext onDragEnd={handleDragEnd}>
      <div className="page-center">
        <div className="qp-card">
          <h1>Question Placement Testing</h1>

          <div className="number-line">
            <CurrentQuestionCard question={currentQuestion} />
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
          <div className="number-box boundary-box">0</div>
          <LineQuestions lineQuestions={lineQuestions} /> {/* Left boundary: 0 */}
          <DroppableSlot slotIndex={lineQuestions.length} />  {/* Final slot after the last question */}
          <div className="number-box boundary-box">   {/* Right boundary: ∞ */}
            <FaInfinity />
          </div>
        </div>

          <button className="qp-button" onClick={loadNextQuestion}>Load another random question</button>

        </div>
      </div>
    </DndContext>
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
