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

  //function for handling an object being dragged
  function handleDragEnd(dragEvent) {
    const { active, over } = dragEvent;
    //if the question card is not over a drop zone, dont do anything
    if(!over){
      return;
    }
    //if something is being dragged that isnt the current question card, do nothing
    if(active.id !== "current-card"){
      return;
    }
    //if theres a bug and no question loads, do nothing
    if(!currentQuestion){
      return;
    }
    //the "over id" is the slots id that a card can be dragged into
    const slotId = over.id;
    if(!slotId.startsWith("slot-")){
      return;
    }

    const indexString = slotId.replace("slot-", ""); //the slots are labled slot-X, so we're just removing the "slot-", so the indexString contains numbers only
    const insertIndex = parseInt(indexString, 10); //using number base 10 (decimal, 0-9) as apposed to other forms lik ebinary or hex

    if(Number.isNaN(insertIndex)){ //checks that the slot number inserted into the indexString was actually a number - for debugging
      return;
    }

    /* Creating new question card with id and question, id will look like "card-xx", it either picks the current question card ID or assign a random number based off current time*/
    //?? mean sthat whater is on the right side will be used if th eleft side is null or undefined
    const newCard = {id: `card-${currentQuestion.id ?? Date.now()}`,question: currentQuestion};

    // Insert this card into lineQuestions at the chosen position
    setLineQuestions((prev) => {
      const next = [...prev];
      next.splice(insertIndex, 0, newCard);
      return next;
    });

    setScore((prevScore) => prevScore + 1); //increase score by 1
    setCurrentQuestion(null); //clear current card so it can't be dragged again
    loadNextQuestion(); //load the next question from the backend
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
          <div className="number-box boundary-box">   {/* Right boundary: infinity*/}
            <FaInfinity />
          </div>
        </div>

          <button className="qp-button" onClick={loadNextQuestion}>Load another random question</button>

        </div>
      </div>
    </DndContext>
  );
}

export default QuestionPlacement;
