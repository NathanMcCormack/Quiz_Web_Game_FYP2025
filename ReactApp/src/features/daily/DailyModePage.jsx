// ReactApp/src/features/daily/DailyModePage.jsx
import React, { useEffect, useState } from "react";
import "../game/styles/QuestionPlacement.css";

import TopBar from "../../components/layout/TopBar";
import FooterBar from "../../components/layout/FooterBar";
import GameOverPopUp from "../game/components/GameOverPopUp";
import CurrentQuestionCard from "../game/components/CurrentQuestionCard";
import LineQuestions from "../game/components/LineQuestions";
import { FaInfinity } from "react-icons/fa6";

import {
  DndContext,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  pointerWithin,
  rectIntersection,
} from "@dnd-kit/core";
import {
  generateTodayDaily,
  fetchTodayDaily,
  validateDailyPlacement,
} from "./services/dailyApi";

export default function DailyModePage() {
  const [meta, setMeta] = useState(null); // { date, category, difficulty }
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [deck, setDeck] = useState([]);
  const [lineQuestions, setLineQuestions] = useState([]);
  const [score, setScore] = useState(0);
  const [message, setMessage] = useState("");
  const [isLoadingDaily, setIsLoadingDaily] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);
  const [lastScore, setLastScore] = useState(0);
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

  const resetGame = () => {
    setLineQuestions([]);
    setScore(0);
    setMessage("");
  };

  const loadNextFromDeck = (nextDeck) => {
    //if deck is empty, daily challenge should be complete
    if (!nextDeck || nextDeck.length === 0) {
      setEndTitle("Daily Complete!");
      setEndSubtitle("Come back tomorrow for a new challenge.");
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

  const startDaily = async () => {
    setMessage("");
    setIsGameOver(false);
    setEndTitle("Game Over!");
    setEndSubtitle("Try Again!");
    resetGame();
    setCurrentQuestion(null);
    setDeck([]);
    setMeta(null);

    setIsLoadingDaily(true);
    try {
      //fetch today's stored challenge
      const data = await fetchTodayDaily();

      setMeta({
        date: data.challenge_date,
        category: data.category,
        difficulty: data.difficulty,
      });

      //shuffle questions client-side (keeps gameplay varied even though content is shared)
      const qs = [...(Array.isArray(data.questions) ? data.questions : [])];
      for (let i = qs.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [qs[i], qs[j]] = [qs[j], qs[i]];
      }

      //expect 8 questions for the daily challenge
      setDeck(qs.slice(1));
      setCurrentQuestion(qs[0] ?? null);

      if (qs.length !== 8) {
        setMessage(`Warning: expected 8 questions, got ${qs.length}.`);
      }
    } catch (err) {
      console.error(err);
      const msg = String(err?.message || "");

      if (msg.includes("404")) {
        setMessage(
          "Daily challenge not generated yet. Click Reload Daily or wait until midnight (Ireland time)."
        );
      } else {
        setMessage(
          "Daily mode failed to load (backend offline or server error)."
        );
      }

      setMeta(null);
      setDeck([]);
      setCurrentQuestion(null);
    } finally {
      setIsLoadingDaily(false);
    }
  };

  useEffect(() => {
    startDaily();
  }, []);

  const startNewGame = async () => {
    setIsGameOver(false);
    await startDaily();
  };

  const handleDragEnd = async (event) => {
    //prevent interactions while loading/validating
    if (isValidating || isLoadingDaily) return;

    setMessage("");
    const { over, active } = event;

    //must have a valid drop target AND a current card to place
    if (!over || !currentQuestion) return;

    if (active?.id !== "current-card") return;

    //lineQuestions drop zones use ids like "slot-0", "slot-1"...
    const slotId = over.id.toString();
    if (!slotId.startsWith("slot-")) return;

    const insertIndex = parseInt(slotId.replace("slot-", ""), 10);
    if (Number.isNaN(insertIndex)) return;

    //identify neighbors based on where the user dropped the card
    const left = insertIndex - 1 >= 0 ? lineQuestions[insertIndex - 1] : null;
    const right =
      insertIndex < lineQuestions.length ? lineQuestions[insertIndex] : null;

    const leftNeighborId = left ? left.questionId : null;
    const rightNeighborId = right ? right.questionId : null;

    setIsValidating(true);
    try {
      const result = await validateDailyPlacement({
        placedQuestionId: currentQuestion.id,
        leftNeighborId,
        rightNeighborId,
      });

      if (result.correct) {
        //build the same line card structure your LineQuestions component expects
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

        //daily ends after 8 correct placements
        if (newLine.length >= 8) {
          setEndTitle("Daily Complete!");
          setEndSubtitle("Come back tomorrow for a new challenge.");
          setLastScore(score + 1);
          resetGame();
          setIsGameOver(true);
          return;
        }

        //move on to next question
        loadNextFromDeck(deck);
        return;
      }

      //incorrect placement -> game over
      setEndTitle("Game Over!");
      setEndSubtitle("Try Again!");
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
        <div className="qp-card">
          <div className="setup-panel">
            <h2>Daily Mode</h2>
            {meta && (
              <div className="daily-meta" aria-label="Daily challenge details">
                <div className="daily-meta-card">
                  <div className="daily-meta-label">Date</div>
                  <div className="daily-meta-value">
                    {new Date(`${meta.date}T00:00:00`).toLocaleDateString(
                      "en-IE",
                      {
                        weekday: "long",
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                      }
                    )}
                  </div>
                </div>

                <div className="daily-meta-card">
                  <div className="daily-meta-label">Category</div>
                  <div className="daily-meta-value">{meta.category}</div>
                </div>

                <div className="daily-meta-card">
                  <div className="daily-meta-label">Difficulty</div>
                  <div className="daily-meta-value daily-meta-value--caps">
                    {meta.difficulty}
                  </div>
                </div>
              </div>
            )}

            <button
              className="setup-button"
              onClick={startDaily}
              disabled={isValidating || isLoadingDaily}
            >
              {isLoadingDaily ? "Loading..." : "Reload Daily"}
            </button>

            {message && (
              <p className="setup-message">
                <strong>Message:</strong> {message}
              </p>
            )}
          </div>

          <div className="number-line">
            <CurrentQuestionCard
              question={currentQuestion}
              isDisabled={isValidating || isLoadingDaily}
            />
            <strong>Score:</strong> {score}
          </div>

          <div className="number-line">
            <div className="number-box boundary-box">0</div>
            <LineQuestions lineQuestions={lineQuestions} />
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