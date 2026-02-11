import React, {useState } from "react"; //useState lets the component store values and update them
import { startGame, validatePlacement } from "./api"; //importing the two functions for fetching questions 
import "./QuestionPlacement.css";
import GameOverPopUp from "./GameOverPopUp";
import { FaInfinity } from "react-icons/fa6"; //Infintity Logo from React-Icons website
//imports from dnd website 
import { DndContext, closestCenter, useDraggable, useDroppable } from "@dnd-kit/core";
import TopBar from "./components/TopBar";
import FooterBar from "./components/FooterBar";


function QuestionPlacement() {
  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null); //setting usestate to NULL, to start off with currentQuestion
  const [lineQuestions, setLineQuestions] = useState([]);
  const [score, setScore] = useState(0);   //players score
  const [message, setMessage] = useState(""); //used for feedback errors
  const [isValidating, setIsValidating] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);
  const [lastScore, setLastScore] = useState(0);
  const [categoryInput, setCategoryInput] = useState("");
  const [difficultyInput, setDifficultyInput] = useState("easy");
  const [deck, setDeck] = useState([]); // remaining questions
  const [sessionId, setSessionId] = useState(null);

const [endTitle, setEndTitle] = useState("Game Over!");
const [endSubtitle, setEndSubtitle] = useState("Try Again!");

  const startNewGame = async () => {
    setIsGameOver(false);
    setCurrentQuestion(null);
    setDeck([]);
    setSessionId(null);
    setMessage("");
    // category/difficulty remain as user entered, so they can just press Start again
  };
  //set helepr to reset the number line to an empty array and the score to 0
  const resetGame = () => {
    setLineQuestions([]);
    setScore(0);
    setMessage("");
  }

  //*********************   function for handling an object being dragged   *********************
 const handleDragEnd = async (event) => {
  //clears any old messages 
  setMessage("");

  const { over, active } = event;

  //only handle drops of the current card
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

      // If this placement just completed the 20th card, win:
      const placedCount = newLine.length;
      if (placedCount >= 20) {
        setEndTitle("You Win!");
        setEndSubtitle("You placed all questions correctly 🎉");
        setLastScore(score + 1); // because score increments after success
        resetGame();
        setIsGameOver(true);
        return;
      }
      loadNextFromDeck(deck);
      return;
    }

    // Incorrect placement => end game, show modal (blocking)
    setLastScore(score);
    resetGame();             // clears line + score
    setIsGameOver(true);     // blocks UI until restart
    setCurrentQuestion(null);
    
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

  function loadNextFromDeck(nextDeck) {
    //if the player has placed all questions correctly 
    if (!nextDeck || nextDeck.length === 0) {
      setEndTitle("You Win!");
      setEndSubtitle("Congradulations, You placed all questions correctly");
      setLastScore(score);
      resetGame();
      setIsGameOver(true);
      setCurrentQuestion(null);
      return;
    }

    //next is the question that will be shown Qn, rest is the rest of the questions Qn+1, Qn+2...
    const [next, ...rest] = nextDeck;
    setCurrentQuestion(next); //updates current question 
    setDeck(rest); //sets the state to teh rest of the questions 
  }

  const handleStartGame = async () => {
  setMessage("");

  if (!categoryInput.trim()) { //trim removes any spaces before or after the category 
    setMessage("Please enter a category.");
    return;
  }

  //resets the game before starting 
  setIsGameOver(false);
  resetGame();
  setCurrentQuestion(null);

  //calls the backend to start a new session 
  try {
    const data = await startGame({
      category: categoryInput.trim(),
      difficulty: difficultyInput,
    });

    setSessionId(data.session_id); //save sthe sessions ID inm the state, used for fetching random questions in this state 

    // Shuffle questions client-side (so it's not always DB insert order)
    const qs = [...data.questions];
    for (let i = qs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [qs[i], qs[j]] = [qs[j], qs[i]];
    }

    // put into deck and load first
    setDeck(qs.slice(1));
    setCurrentQuestion(qs[0]);
  } catch (err) {
    console.error(err);
    setMessage("Failed to start game (AI generation error). Try again.");
  }
  };

//What will show up on the webpage - everything inside div.
  return (
     <DndContext onDragEnd={handleDragEnd}>
      <GameOverPopUp open={isGameOver} score={lastScore} onStartNewGame={startNewGame} title={endTitle} subtitle={endSubtitle}/>
      <TopBar title="Quiz Game"/>
      <div className="page-center">
        <div className="qp-card">
          <div className="setup-panel">
            <h2>Start a new game</h2>

            <label>
              Category:
              <input
                type="text"
                value={categoryInput} //the players input will always display in the current React state
                onChange={(e) => setCategoryInput(e.target.value)} //updates teh state whenever the user types in, typing then triggers teh setCategoryInput, and the value updates 
                placeholder="eg Premier League, 90s Music..."
                disabled={isValidating || currentQuestion !== null || lineQuestions.length > 0} //the category input becomes disbaled when: backend check in porgress, a gamne is in progress, there are any questions placed
              />
            </label>

            <label>
              Difficulty:
              <select
                value={difficultyInput}
                onChange={(e) => setDifficultyInput(e.target.value)}
                disabled={isValidating || currentQuestion !== null || lineQuestions.length > 0}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>

            <button onClick={handleStartGame} disabled={isValidating}>
              Start Game
            </button>

            {sessionId && (
              <p>
                Session: {sessionId}
              </p>
            )}
          </div>

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
          </p>
          <div className="number-line"> 
            <div className="number-box boundary-box">0</div>
          <LineQuestions lineQuestions={lineQuestions} /> {/* Left boundary: 0 */}
            <div className="number-box boundary-box">   {/* Right boundary: infinity*/}
              <FaInfinity />
            </div>
          </div>
        <FooterBar />
        </div>
      </div>
    </DndContext>
  );
}

export default QuestionPlacement;
