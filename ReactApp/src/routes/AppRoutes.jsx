import React from "react";
import { Routes, Route } from "react-router-dom";
import QuestionPlacement from "../features/game/QuestionPlacement.jsx";

//current game uusing default path
export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<QuestionPlacement />} /> 
    </Routes>
  );
}