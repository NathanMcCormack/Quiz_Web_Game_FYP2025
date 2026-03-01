import React from "react";
import { Routes, Route } from "react-router-dom";
import QuestionPlacement from "../features/game/QuestionPlacement.jsx";
import DailyModePage from "../features/daily/DailyModePage.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<QuestionPlacement />} />
      <Route path="/daily" element={<DailyModePage />} />
    </Routes>
  );
}