import React, { useState } from "react"; //useState lets the component store values and update them
import { startGame, validatePlacement } from "./services/gameApi"; //importing the two functions for fetching questions
import "./styles/QuestionPlacement.css";
import GameOverPopUp from "./components/GameOverPopUp";
import { FaInfinity } from "react-icons/fa6"; //Infintity Logo from React-Icons website
//imports from dnd website
import {
  DndContext,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  pointerWithin,
  rectIntersection,
} from "@dnd-kit/core";
import TopBar from "../../components/layout/TopBar";
import FooterBar from "../../components/layout/FooterBar";

import CurrentQuestionCard from "./components/CurrentQuestionCard";
import LineQuestions from "./components/LineQuestions";

function QuestionPlacement() {
  // The question currently being placed
  const [currentQuestion, setCurrentQuestion] = useState(null); //setting usestate to NULL, to start off with currentQuestion
  const [lineQuestions, setLineQuestions] = useState([]);
  const [score, setScore] = useState(0); //players score
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

  const sensors = useSensors(
    useSensor(MouseSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        distance: 12,
      },
    })
  );

  const collisionDetection = (args) => {
    const pointerCollisions = pointerWithin(args);

    if (pointerCollisions.length > 0) {
      return pointerCollisions;
    }

    return rectIntersection(args);
  };

  const startNewGame = async () => {
    setIsGameOver(false);
    setCurrentQuestion(null);
    setDeck([]);
    setSessionId(null);
    setMessage("");
  };

  const resetGame = () => {
    setLineQuestions([]);
    setScore(0);
    setMessage("");
  };

  const loadNextFromDeck = (nextDeck) => {
    //If no questions left: player wins and game over popup shown
    if (!nextDeck || nextDeck.length === 0) {
      setEndTitle("You Win!");
      setEndSubtitle("Congradulations, You placed all questions correctly");
      setLastScore(score);
      resetGame();
      setIsGameOver(true);
      setCurrentQuestion(null);
      return;
    }

    const [next, ...rest] = nextDeck;
    setCurrentQuestion(next);
    setDeck(rest);
  };

  //Validate placement in the deck and if correct, add to number line. if not - game over
  const handleDragEnd = async (event) => {
    if (isValidating) return;

    setMessage("");

    //over = droppable id that item is dropped on
    //active = draggable item being moved
    const { over, active } = event;

    if (!over || !currentQuestion) return;
    if (active?.id !== "current-card") return; //only one draggable at a time - the current card

    //Extract the index from "slot-#" id
    const slotId = over.id.toString();
    if (!slotId.startsWith("slot-")) return;

    const insertIndex = parseInt(slotId.replace("slot-", ""), 10);
    if (Number.isNaN(insertIndex)) return;

    //Find left and right neighbor question IDs for validation endpoint
    const left = insertIndex - 1 >= 0 ? lineQuestions[insertIndex - 1] : null;
    const right =
      insertIndex < lineQuestions.length ? lineQuestions[insertIndex] : null;

    //If null use null else use that questions id
    const leftNeighborId = left ? left.questionId : null;
    const rightNeighborId = right ? right.questionId : null;

    setIsValidating(true);
    try {
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

        const newLine = [...lineQuestions];
        newLine.splice(insertIndex, 0, newCard);

        setLineQuestions(newLine);
        setScore((prev) => prev + 1);
        setCurrentQuestion(null);

        //If 20 questions placed, win
        const placedCount = newLine.length;
        if (placedCount >= 20) {
          setEndTitle("You Win!");
          setEndSubtitle("You placed all questions correctly 🎉");
          setLastScore(score + 1);
          resetGame();
          setIsGameOver(true);
          return;
        }

        loadNextFromDeck(deck);
        return;
      }

      //If incorrect -> game over
      setLastScore(score);
      resetGame();
      setIsGameOver(true);
      setCurrentQuestion(null);
    } catch (err) {
      console.error(err);
      setMessage("Validation failed due to a server error. Try again.");
    } finally {
      setIsValidating(false);
    }
  };

  //Starts game: calls backend and prepares deck
  const handleStartGame = async () => {
    setMessage("");

    if (!categoryInput.trim()) {
      setMessage("Please enter a category.");
      return;
    }

    setIsGameOver(false);
    resetGame();
    setCurrentQuestion(null);

    try {
      const data = await startGame({
        category: categoryInput.trim(),
        difficulty: difficultyInput,
      });

      setSessionId(data.session_id);

      //Shuffle questions client-side
      const qs = [...data.questions];
      for (let i = qs.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [qs[i], qs[j]] = [qs[j], qs[i]];
      }

      setDeck(qs.slice(1));
      setCurrentQuestion(qs[0]);
    } catch (err) {
      console.error(err);
      setMessage("Failed to start game (AI generation error). Try again.");
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={collisionDetection}
      onDragEnd={handleDragEnd}
    >
      <GameOverPopUp
        open={isGameOver}
        score={lastScore}
        onStartNewGame={startNewGame}
        title={endTitle}
        subtitle={endSubtitle}
      />
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
                  onChange={(e) => setCategoryInput(e.target.value)}
                  placeholder="eg Premier League, 90s Music..."
                  disabled={
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

              <button
                className="setup-button"
                onClick={handleStartGame}
                disabled={isValidating}
              >
                Start Game
              </button>
            </div>

            {sessionId && <p>Session: {sessionId}</p>}

            {message && (
              <p>
                <strong>Message:</strong> {message}
              </p>
            )}
          </div>
          <div className="number-line">
            <CurrentQuestionCard
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