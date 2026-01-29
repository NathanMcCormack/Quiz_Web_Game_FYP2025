import React from "react";
import "./GameOverPopUp.css";

export default function GameOverPopUp({ open, score, onStartNewGame }) {
  if (!open) return null;

  // Clicking the backdrop should NOT close it (blocks everything until button pressed)
  return (
    <div className="gp-backdrop" role="dialog" aria-modal="true" aria-label="Game Over">
      <div className="gp-modal">
        <h2 className="gp-title">Game Over!</h2>
        <h3 gp-title>Try Again!</h3>

        <p className="gp-text">
          Your score: <strong>{score}</strong>
        </p>

        <button className="gp-button" onClick={onStartNewGame}>
          Start New Game
        </button>
      </div>
    </div>
  );
}
