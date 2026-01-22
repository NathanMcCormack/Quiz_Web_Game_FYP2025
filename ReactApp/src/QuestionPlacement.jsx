import React, { useEffect, useState } from "react"; //useState lets the component store values and update them, useEffect... 
import { fetchRandomQuestion, validatePlacement } from "./api"; //importing the two functions for fetching questions 
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
  const [isValidating, setIsValidating] = useState(false);

  //set helepr to reset the number line to an empty array and the score to 0
  const resetGame = () => {
    setLineQuestions([]);
    setScore(0);
  }

  //*********************   function for handling an object being dragged   *********************
 const handleDragEnd = async (event) => {
  setMessage("");

  const { over, active } = event;

  // Only handle drops of the current card
  if (!over || !currentQuestion) return;
  if (active?.id !== "current-card") return;

  const slotId = over.id.toString();
  if (!slotId.startsWith("slot-")) return;

  const insertIndex = parseInt(slotId.replace("slot-", ""), 10);
  if (Number.isNaN(insertIndex)) return;

  // Neighbors are read from the CURRENT line (before insertion)
  const left = insertIndex - 1 >= 0 ? lineQuestions[insertIndex - 1] : null;
  const right = insertIndex < lineQuestions.length ? lineQuestions[insertIndex] : null;

  const leftNeighborId = left ? left.questionId : null;
  const rightNeighborId = right ? right.questionId : null;

  setIsValidating(true);
  try {
    const result = await validatePlacement({
      placedQuestionId: currentQuestion.id,
      leftNeighborId,
      rightNeighborId,
    });

    if (result.correct) {
      const newCard = {
        id: `card-${currentQuestion.id}`,
        questionId: currentQuestion.id,
        question: currentQuestion,
      };

      const newLine = [...lineQuestions];
      newLine.splice(insertIndex, 0, newCard);

      setLineQuestions(newLine);
      setScore((prev) => prev + 1);

      setCurrentQuestion(null);
      loadNextQuestion();
      return;
    }

    // Incorrect placement => end game and reset
    setMessage("Incorrect placement. Game reset.");
    resetGame();
    setCurrentQuestion(null);
    loadNextQuestion();
  } catch (err) {
    console.error(err);
    setMessage("Validation failed due to a server error. Try again.");
  } finally {
    setIsValidating(false);
  }
};


  //********************* The current card - draggable, style *********************
  function CurrentQuestionCard({question, isDisabled}){
    //attributes - , listneers - event handlers (cursor change...), setNodeRef - pass this to the element uou want to be draggable (DnD Kit), transform - how far its being dragged, isDragging - Boolean (useful fo rCSS)
    const { attributes, listeners, setNodeRef, transform, isDragging } = 
      useDraggable({
        id: "current-card", //unique id for draggable card 
        disabled: !question || isValidating, // dont drag when no question
    });

    const style = {
      transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined, //if transform exists (how far the item has been dragged), move the element by Xpx & Ypx
      opacity: isDragging ? 0.8 : 1, //if dragging opacacity becomes .8 to be more obvious that user is dragging card
      cursor: question ? "grab" : "default", //if the cursor is over the question, it will have a grab icon 
    };

  return (
    <div ref={setNodeRef} style={style} className="current-question" {...attributes} {...(question ? listeners : {})}> {/* attributes - nice to have for accessibility features for DnD kit */}
      <strong>Current question:</strong>                                             {/* if a question exists it becomes listeners (event handlers are attached), if not - nothing */}
      <div className="current-question-text">
        {question ? question.question : "Loading..."}
      </div>
      <p className="current-question-hint">
        Drag this card and drop it between 0 and ∞
      </p>
    </div>
  );
  }

//*********************  Drop Zone   *********************
 function DroppableSlot({slotIndex}){
  //isOver - when a draggable item is over the drop zone
    const { setNodeRef, isOver } = useDroppable({ id: `slot-${slotIndex}`}); //useDroppable - from DnD kit, turns component into a drop zone. id = "slot-xxx"

    //This div creates the drop zone
    return (
      <div ref={setNodeRef} className={`drop-slot ${isOver ? "drop-slot--active" : ""}`}/>
    );
  } 

  //********************* Shows questions in the line *********************
  function LineQuestions({lineQuestions}){ //takes in the cards that are already placed on the number line 
    return (
      <>
        {lineQuestions.map((item, index) => ( //goes through each question already on the line; item (id, question), index(position in the array)
          <React.Fragment key={item.id}> {/* key required to track which card is which */}
            <DroppableSlot slotIndex={index} /> {/* renders teh droppable slot before the question, slotIndex decideds where to put it in the array */}
            <div className="number-box line-question-box">
              {item.question?.question ?? "Question"} {/* if question exists - show it, if not just show  the word "Question" to avoid crashes*/}
            </div>
          </React.Fragment>
        ))}

        {/* Final slot after the last question */}
        <DroppableSlot slotIndex={lineQuestions.length} />
      </>
    );
  } 

  //******************* fetchRandomQuestion - grabs new question from backend - async so we can use await for API calls ******************8
  async function loadNextQuestion() {
    try {
      const q = await fetchRandomQuestion(); //call our function sto call a random question from the backend
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
            <CurrentQuestionCard question={currentQuestion} isDisabled={isValidating} />
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
          <div className="number-box boundary-box">   {/* Right boundary: infinity*/}
            <FaInfinity />
          </div>
        </div>
        </div>
      </div>
    </DndContext>
  );
}

export default QuestionPlacement;
