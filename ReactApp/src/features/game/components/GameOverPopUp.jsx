import React from "react";
import "../styles/GameOverPopUp.css";

export default function GameOverPopUp({ open, score, onStartNewGame, title, subtitle }) { //open - visbalility

  //shows nothing if open is false
  if (!open) return null;

  return (
    <div className="gp-backdrop" role="dialog" aria-modal="true" aria-label={title || "Game Over"}> 
      <div className="gp-modal">
        <h2 className="gp-title">{title || "Game Over!"}</h2>
        <h3 className="gp-subtitle">{subtitle || "Try Again!"}</h3>

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
