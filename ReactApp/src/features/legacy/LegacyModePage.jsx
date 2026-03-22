import React, { useEffect, useState, useMemo } from "react";
import "../game/styles/QuestionPlacement.css";
import "./LegacyModePage.css";

import TopBar from "../../components/layout/TopBar";
import FooterBar from "../../components/layout/FooterBar";
import GameOverPopUp from "../game/components/GameOverPopUp";
import CurrentQuestionCard from "../game/components/CurrentQuestionCard";
import LineQuestions from "../game/components/LineQuestions";
import { FaInfinity } from "react-icons/fa6";

import { DndContext, closestCenter } from "@dnd-kit/core";
import { fetchLegacyHistory, fetchLegacyChallenge } from "./services/legacyApi";
import { validateDailyPlacement } from "../daily/services/dailyApi";

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function buildCalendarCells(viewMonth, availableDates) {
  const year = viewMonth.getFullYear();
  const month = viewMonth.getMonth();
  // getDay() returns 0=Sun...6=Sat, adjust for Monday-first grid
  const rawFirstDay = new Date(year, month, 1).getDay();
  const firstDay = (rawFirstDay + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const cells = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ day: d, dateStr, hasChallenge: availableDates.includes(dateStr) });
  }
  return cells;
}

export default function LegacyModePage() {
  // ---- Calendar state ----
  const [availableDates, setAvailableDates] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [historyError, setHistoryError] = useState("");
  const [viewMonth, setViewMonth] = useState(() => {
    const d = new Date();
    d.setDate(1);
    return d;
  });

  // ---- Selected challenge ----
  const [selectedChallenge, setSelectedChallenge] = useState(null);
  const [isLoadingChallenge, setIsLoadingChallenge] = useState(false);

  // ---- Gameplay state ----
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [deck, setDeck] = useState([]);
  const [lineQuestions, setLineQuestions] = useState([]);
  const [score, setScore] = useState(0);
  const [message, setMessage] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [isGameOver, setIsGameOver] = useState(false);
  const [lastScore, setLastScore] = useState(0);
  const [endTitle, setEndTitle] = useState("Game Over!");
  const [endSubtitle, setEndSubtitle] = useState("Try Again!");

  useEffect(() => {
    fetchLegacyHistory()
      .then((data) => setAvailableDates(data.map((c) => c.challenge_date)))
      .catch(() => setHistoryError("Failed to load past challenges. Is the backend running?"))
      .finally(() => setIsLoadingHistory(false));
  }, []);

  // ---- Calendar helpers ----
  const today = new Date();
  today.setDate(1);
  const isCurrentMonth =
    viewMonth.getFullYear() === today.getFullYear() &&
    viewMonth.getMonth() === today.getMonth();

  const calendarCells = useMemo(
    () => buildCalendarCells(viewMonth, availableDates),
    [viewMonth, availableDates]
  );

  const monthLabel = viewMonth.toLocaleDateString("en-IE", {
    month: "long",
    year: "numeric",
  });

  const prevMonth = () => {
    const d = new Date(viewMonth);
    d.setMonth(d.getMonth() - 1);
    setViewMonth(d);
  };

  const nextMonth = () => {
    if (isCurrentMonth) return;
    const d = new Date(viewMonth);
    d.setMonth(d.getMonth() + 1);
    setViewMonth(d);
  };

  // ---- Load a specific day's challenge ----
  const selectDay = async (dateStr) => {
    setMessage("");
    setIsLoadingChallenge(true);
    try {
      const data = await fetchLegacyChallenge(dateStr);
      const qs = [...data.questions];
      for (let i = qs.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [qs[i], qs[j]] = [qs[j], qs[i]];
      }
      setSelectedChallenge(data);
      setCurrentQuestion(qs[0] ?? null);
      setDeck(qs.slice(1));
      setLineQuestions([]);
      setScore(0);
      setIsGameOver(false);
    } catch (err) {
      setMessage("Failed to load this challenge. Please try again.");
    } finally {
      setIsLoadingChallenge(false);
    }
  };

  // ---- Gameplay ----
  const resetGame = () => {
    setLineQuestions([]);
    setScore(0);
    setMessage("");
  };

  const loadNextFromDeck = (nextDeck) => {
    if (!nextDeck || nextDeck.length === 0) {
      setEndTitle("Challenge Complete!");
      setEndSubtitle("Pick another day to play.");
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

  const backToCalendar = () => {
    setSelectedChallenge(null);
    setCurrentQuestion(null);
    setDeck([]);
    setLineQuestions([]);
    setScore(0);
    setMessage("");
    setIsGameOver(false);
  };

  const handleDragEnd = async (event) => {
    if (isValidating || isLoadingChallenge) return;
    setMessage("");
    const { over, active } = event;
    if (!over || !currentQuestion) return;
    if (active?.id !== "current-card") return;
    const slotId = over.id.toString();
    if (!slotId.startsWith("slot-")) return;
    const insertIndex = parseInt(slotId.replace("slot-", ""), 10);
    if (Number.isNaN(insertIndex)) return;

    const left = insertIndex - 1 >= 0 ? lineQuestions[insertIndex - 1] : null;
    const right = insertIndex < lineQuestions.length ? lineQuestions[insertIndex] : null;
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

        if (newLine.length >= 8) {
          setEndTitle("Challenge Complete!");
          setEndSubtitle("Pick another day to play.");
          setLastScore(score + 1);
          resetGame();
          setIsGameOver(true);
          return;
        }
        loadNextFromDeck(deck);
        return;
      }

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

  // ---- Render: calendar picker ----
  if (!selectedChallenge) {
    return (
      <>
        <TopBar />
        <div className="page-center">
          <div className="qp-card">
            <div className="setup-panel">
              <h2>Legacy Mode</h2>
              <p>Pick a past daily challenge to play.</p>

              {isLoadingHistory && <p>Loading past challenges...</p>}
              {historyError && <p><strong>{historyError}</strong></p>}

              {!isLoadingHistory && !historyError && (
                <div className="legacy-calendar">
                  <div className="calendar-nav">
                    <button onClick={prevMonth}>‹</button>
                    <span>{monthLabel}</span>
                    <button onClick={nextMonth} disabled={isCurrentMonth}>›</button>
                  </div>

                  <div className="calendar-grid">
                    {DAY_LABELS.map((label) => (
                      <div key={label} className="calendar-day-label">{label}</div>
                    ))}
                    {calendarCells.map((cell, i) =>
                      cell === null ? (
                        <div key={`empty-${i}`} className="calendar-cell" />
                      ) : cell.hasChallenge ? (
                        <div
                          key={cell.dateStr}
                          className="calendar-cell calendar-cell--has-challenge"
                          onClick={() => !isLoadingChallenge && selectDay(cell.dateStr)}
                          title={cell.dateStr}
                        >
                          {cell.day}
                        </div>
                      ) : (
                        <div key={cell.dateStr} className="calendar-cell calendar-cell--no-challenge">
                          {cell.day}
                        </div>
                      )
                    )}
                  </div>

                  {availableDates.length === 0 && (
                    <p>No past challenges available yet.</p>
                  )}
                  {isLoadingChallenge && <p>Loading challenge...</p>}
                  {message && <p><strong>{message}</strong></p>}
                </div>
              )}
            </div>
          </div>
        </div>
        <FooterBar />
      </>
    );
  }

  // ---- Render: gameplay ----
  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <GameOverPopUp
        open={isGameOver}
        score={lastScore}
        onStartNewGame={backToCalendar}
        title={endTitle}
        subtitle={endSubtitle}
      />
      <TopBar />
      <div className="page-center">
        <div className="qp-card">
          <div className="setup-panel">
            <h2>Legacy Mode</h2>
            <p>
              <strong>Date:</strong> {selectedChallenge.challenge_date}{" "}
              <strong>Category:</strong> {selectedChallenge.category}{" "}
              <strong>Difficulty:</strong> {selectedChallenge.difficulty}
            </p>
            <button onClick={backToCalendar} disabled={isValidating}>
              ← Back to Calendar
            </button>
            {message && <p><strong>{message}</strong></p>}
          </div>

          <div className="number-line">
            <CurrentQuestionCard
              question={currentQuestion}
              isDisabled={isValidating || isLoadingChallenge}
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