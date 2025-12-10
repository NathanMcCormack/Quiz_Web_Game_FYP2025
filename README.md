# Quiz Web Game – FYP 2025

Final Year Project – Software & Electronic Engineering  
Interactive web-based quiz game where players drag and drop question cards onto a number line, placing answers in the correct order and tracking their score.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Backend (FastAPI services)](#backend-fastapi-services)
  - [Frontend (React + Vite)](#frontend-react--vite)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Summary](#api-summary)
  - [Game Service](#game-service)
  - [User Service](#user-service)
- [Testing](#testing)
- [Development Notes & Next Steps](#development-notes--next-steps)

---

## Overview

This project implements a web-based quiz game where the player is shown a question on a draggable card. Each question has a numerical answer (e.g. a year, a count, or any non-negative integer). The player drags the card onto a number line between 0 and ∞ and drops it in the position they believe is correct relative to previously placed questions.

Core goals:

- Provide an engaging, visual way to practise estimation and ordering of numeric facts.
- Demonstrate a microservice-based backend using FastAPI and SQLAlchemy.
- Use a modern React frontend (Vite, hooks, and drag-and-drop via `@dnd-kit`).
- Apply good software engineering practices: typing, validation, tests, CI, and clear separation of concerns.

---

## Features

- Drag-and-drop quiz gameplay on a number line between 0 and infinity.
- Each question has:
  - A text prompt.
  - A non-negative integer answer.
- Current question is shown on a draggable card above the number line.
- When dropped on the line:
  - The card is “locked” in place.
  - A new random question is loaded from the backend.
  - The player’s score is updated.
- Game runs and basic stats stored in the backend, with support for:
  - User-specific stats (high score, average score, games played).
  - Leaderboard entries.
- Separate microservices for:
  - Game logic and question management.
  - User management (registration, CRUD).
- RESTful APIs with automatic interactive docs via FastAPI `/docs`.

---

## Architecture

The system is composed of three main parts:

1. **Game Service (FastAPI, port 8001)**
   - Owns the quiz questions and game run data.
   - Provides endpoints for:
     - Creating/updating/deleting questions.
     - Fetching random questions.
     - Recording game runs and computing basic user stats.
     - Leaderboard queries.
   - Persists data via SQLAlchemy ORM.

2. **User Service (FastAPI, port 8000)**
   - Owns user accounts (name, email, username, age, password).
   - Provides CRUD operations for users.
   - Uses Pydantic for strong input validation (e.g. age > 12, valid email).

3. **Frontend (React + Vite, port 5173 by default)**
   - Single-page app.
   - Main component: `QuestionPlacement`:
     - Fetches random questions from the Game Service.
     - Uses `@dnd-kit/core` for drag-and-drop.
     - Displays 0 and ∞ as fixed endpoints, with a draggable card in between.
   - Uses a Vite dev-server proxy so that calls to `/api` are forwarded to the Game Service (`http://localhost:8001`).

---

## Technology Stack

**Backend**

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Uvicorn (dev server)
- Gunicorn (production-ready process manager)
- pytest (testing)
- psycopg2-binary (PostgreSQL driver, optional)
- SQLite by default for local development

**Frontend**

- React (with `StrictMode`)
- Vite
- Axios
- `@dnd-kit/core` and related packages (drag-and-drop)
- `react-icons` (Infinity icon)
- ESLint

**Tooling & CI**

- `Makefile` for common backend tasks.
- GitHub Actions workflow (`.github/workflows/ci.yml`) to:
  - Install Python dependencies.
  - Run pytest with coverage on pushes/pull requests to `master`.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js (LTS version recommended, e.g. 18+)
- npm (comes with Node)
- Git (if cloning from a repository)

All commands below assume you are in the project root:

```bash
Quiz_Web_Game_FYP2025-main/
