import React, { useState } from "react"; //useState lets the component store values and update them
import { startGame, validatePlacement } from "./services/gameApi"; //importing the two functions for fetching questions
import "./styles/QuestionPlacement.css";
import GameOverPopUp from "./components/GameOverPopUp";
import { FaInfinity } from "react-icons/fa6"; //Infintity Logo from React-Icons website
//imports from dnd website
import {DndContext,MouseSensor,TouchSensor,useSensor,useSensors,pointerWithin,rectIntersection,} from "@dnd-kit/core";
import TopBar from "../../components/layout/TopBar";
import FooterBar from "../../components/layout/FooterBar";

import CurrentQuestionCard from "./components/CurrentQuestionCard";
import LineQuestions from "./components/LineQuestions";

function QuestionPlacement() {
  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null); //setting usestate to NULL, to start off with currentQuestion
  const [lineQuestions, setLineQuestions] = useState([]); //stores cards on the number line
  const [score, setScore] = useState(0); //players score
  const [message, setMessage] = useState(""); //used for feedback errors
  const [isValidating, setIsValidating] = useState(false); //tracks if backend is still loading validation
  const [isGameOver, setIsGameOver] = useState(false); //shows/hides game over popup
  const [lastScore, setLastScore] = useState(0);
  const [categoryInput, setCategoryInput] = useState("");
  const [difficultyInput, setDifficultyInput] = useState("easy"); //defaults to easy
  const [deck, setDeck] = useState([]); // remaining questions
  const [sessionId, setSessionId] = useState(null);

  const [endTitle, setEndTitle] = useState("Game Over!");
  const [endSubtitle, setEndSubtitle] = useState("Try Again!");

  //imported from dnd kit to allow drag and drop on laptops or phones
  //tells dnd kit to use the mouse as one way to drag teh current question
  const sensors = useSensors(
    useSensor(MouseSensor, {
      activationConstraint: {
        distance: 8, //mouse must move at least 8 pixels before game starts
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        distance: 12,
      },
    })
  );

  //checks wjether mouse pointer position is inside a droppable slot
  const collisionDetection = (args) => {
    const pointerCollisions = pointerWithin(args);

    if (pointerCollisions.length > 0) { //if array length is greater than 0, the pointer is inside a droppable slot
      return pointerCollisions; //returns drop target found by pointerWithin
    }

    return rectIntersection(args); //This checks whether the crad and drop zones areas overlap, more forgiving for user
  };

  const startNewGame = async () => {
    setIsGameOver(false);
    setCurrentQuestion(null);
    setDeck([]);
    setSessionId(null);
    setMessage("");
  };

  //seperate function if user wants to resest the game (retry)
  const resetGame = () => {
    setLineQuestions([]);
    setScore(0);
    setMessage("");
  };

  const loadNextFromDeck = (nextDeck) => {
    //If no questions left: player wins and game over popup shown
    //nextDeck is an array of any leftover questions
    if (!nextDeck || nextDeck.length === 0) {
      setEndTitle("You Win!");
      setEndSubtitle("Congradulations, You placed all questions correctly");
      setLastScore(score);
      resetGame();
      setIsGameOver(true);
      setCurrentQuestion(null);
      return;
    }

    //takes current question and stores it in next, takes all other questions and puts it in rest -> nextDeck = [next, rest1, rest2 ...]
    const [next, ...rest] = nextDeck;
    setCurrentQuestion(next);
    setDeck(rest);
  };

  //when player drops card, calls backend
  const handleDragEnd = async (event) => {
    if (isValidating) return;

    setMessage(""); //clears old messages

    //over is the drop zone
    //active is the card being being dragged 
    const { over, active } = event;

    if (!over || !currentQuestion) return; //if not over dropzone or no card being dragged
    if (active?.id !== "current-card") return; //checks that dragged item is the current card

    //coverts dropped slot ID into a string
    const slotId = over.id.toString();
    if (!slotId.startsWith("slot-")) return;

    const insertIndex = parseInt(slotId.replace("slot-", ""), 10); //extracts number from slot ID eg. slot-3 -> 3
    if (Number.isNaN(insertIndex)) return; //ensure id is a number , not "test"

    //Find left and right neighbor question IDs for validation endpoint
    const left = insertIndex - 1 >= 0 ? lineQuestions[insertIndex - 1] : null;
    const right = insertIndex < lineQuestions.length ? lineQuestions[insertIndex] : null;

    //If null use null else use that questions id
    const leftNeighborId = left ? left.questionId : null;
    const rightNeighborId = right ? right.questionId : null;
    //send request to backend for validation
    setIsValidating(true);
    try {
      //sends neighbour ids 
      const result = await validatePlacement({
        placedQuestionId: currentQuestion.id,
        leftNeighborId, 
        rightNeighborId,
      });

      //If correct, insert into the number line and load next
      if (result.correct) {
        const newCard = {
          id: `card-${currentQuestion.id}`,
          questionId: currentQuestion.id,
          question: currentQuestion,
        };
        const newLine = [...lineQuestions]; //creates a new array to avoid driectly mutating a state
        newLine.splice(insertIndex, 0, newCard); //inserts new card - start at insertIndex, delete 0 items, insert newCard
        setLineQuestions(newLine);
        setScore((prev) => prev + 1);
        setCurrentQuestion(null);
        loadNextFromDeck(deck); //if player has not won yet, loads next question
        return;
      }

      //If incorrect -> game over
      setLastScore(score);
      resetGame();
      setIsGameOver(true);
      setCurrentQuestion(null);
    } 
    
    catch (err) {
      console.error(err);
      setMessage("Validation failed due to a server error. Try again.");
    } finally {
      setIsValidating(false);
    }
  };

  //Starts game: calls backend and prepares deck
  const handleStartGame = async () => {
    setMessage("");

    if (!categoryInput.trim()) { //checks if category input is empty 
      setMessage("Please enter a category.");
      return;
    }

    setIsGameOver(false);
    resetGame();
    setCurrentQuestion(null);

    try {
      const data = await startGame({ //calls backend and sends category and difficulty
        category: categoryInput.trim(),
        difficulty: difficultyInput,
      });

      setSessionId(data.session_id); //stores backend sesssiom

      //Shuffle questions client-side
      const qs = [...data.questions]; //creates copy of questions array
      
      //Fisher Yates shuffle Loop
      for (let i = qs.length - 1; i > 0; i--) { 
        const j = Math.floor(Math.random() * (i + 1));
        [qs[i], qs[j]] = [qs[j], qs[i]];
      }

      setDeck(qs.slice(1)); //stores all questions except for first in the deck
      setCurrentQuestion(qs[0]);
    } catch (err) {
      console.error(err);
      setMessage("Failed to start game (AI generation error). Try again.");
    }
  };

  return (
    <DndContext sensors={sensors} collisionDetection={collisionDetection} onDragEnd={handleDragEnd}> {/* passes DnD Logic */}
      <GameOverPopUp open={isGameOver} score={lastScore} onStartNewGame={startNewGame} title={endTitle} subtitle={endSubtitle} />
      <TopBar />
      <div className="page-center">
        {" "}
        {/* Centering wrapper */}
        <div className="qp-card">
          <div className="setup-panel">
            <h2>Start a new game</h2>

            <div className="setup-row">
              <div className="setup-field">
                <div className="setup-label">Category</div>
                <input
                  className="setup-input"
                  type="text"
                  value={categoryInput}
                  onChange={(e) => setCategoryInput(e.target.value)} //runs every tim ethe user canges it, current text in input, updates catgeory input
                  placeholder="eg Premier League, 90s Music..."
                  disabled={ //disables input if there is - an active card, questions already in the number line, or is validating 
                    isValidating ||
                    currentQuestion !== null ||
                    lineQuestions.length > 0
                  }
                />
              </div>

              <div className="setup-field">
                <div className="setup-label">Difficulty</div>
                <select
                  className="setup-select"
                  value={difficultyInput}
                  onChange={(e) => setDifficultyInput(e.target.value)}
                  disabled={
                    isValidating ||
                    currentQuestion !== null ||
                    lineQuestions.length > 0
                  }
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <button //start game button
                className="setup-button"
                onClick={handleStartGame}
                disabled={isValidating}
              >
                Start Game
              </button>
            </div>

            {sessionId && <p>Session: {sessionId}</p>} {/* if session ID exists - show it */}

            {message && ( //checks for error message
              <p>
                <strong>Message:</strong> {message}
              </p>
            )}
          </div>
          <div className="number-line">
            <CurrentQuestionCard //renders current question
              question={currentQuestion}
              isDisabled={isValidating}
            />
            <strong>Score:</strong> {score}
          </div>
          <div className="number-line">
            <div className="number-box boundary-box">0</div>
            <LineQuestions lineQuestions={lineQuestions} />{" "}
            {/* Left boundary: 0 */}
            <div className="number-box boundary-box">
              {/* right boundry box: infinity */}
              <FaInfinity />
            </div>
          </div>
        </div>
      </div>
      <FooterBar />
    </DndContext>
  );
}
export default QuestionPlacement;