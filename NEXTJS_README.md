# GeoChallenge — Next.js Frontend Guide

This document contains everything a new agent or developer needs to build (or continue building) a Next.js frontend for GeoChallenge **without reading the rest of the repo**.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Layout](#2-repository-layout)
3. [Backend API Reference](#3-backend-api-reference)
4. [TypeScript Types](#4-typescript-types)
5. [Environment Variables](#5-environment-variables)
6. [Next.js Project Setup](#6-nextjs-project-setup)
7. [Suggested Page / Route Structure](#7-suggested-page--route-structure)
8. [API Client Utility](#8-api-client-utility)
9. [Key Implementation Notes](#9-key-implementation-notes)

---

## 1. Project Overview

**GeoChallenge** is a geography-guessing game. The player is shown a globe and must click the correct location for a given place name. Guesses are scored by distance from the actual coordinates.

### Tech Stack (existing)

| Layer | Technology |
|---|---|
| Backend API | Python · FastAPI |
| Database | PostgreSQL (via Docker or Render.com) |
| Current frontend | Vanilla HTML/CSS/JS (`web/`) |
| Desktop app | Panda3D (`p3d/`) |
| **New frontend (target)** | **Next.js (App Router)** |

---

## 2. Repository Layout

```
pandapandas/                   ← this repo (geochallenge-frontend)
├── web/                       ← existing vanilla JS frontend (reference)
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── game.js            ← core game logic (reference)
│       ├── challenges.js      ← challenge loading
│       └── version.js
├── p3d/                       ← Panda3D desktop app (ignore for web)
├── NEXTJS_README.md           ← this file
└── .env.example               ← env template

geochallenge-backend/          ← separate repo / git submodule
├── api/
│   ├── main.py                ← FastAPI app, CORS config, static mounts
│   ├── models.py              ← ALL request/response Pydantic models
│   └── routes/
│       ├── game.py            ← /api/game/*
│       ├── challenges.py      ← /api/challenges/*
│       ├── scores.py          ← /api/scores/*
│       └── boundaries.py      ← /api/boundaries/*
├── services/
│   ├── scoring_service.py
│   └── challenges_service.py
├── docker-compose.yml         ← spins up local PostgreSQL
└── .env.example
```

---

## 3. Backend API Reference

### Base URL

```
http://localhost:8000          # local dev
https://<your-render-url>      # production
```

The FastAPI server auto-generates interactive docs at `/docs` (Swagger UI).

---

### 3.1 Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check — returns `{"status": "healthy"}` |

---

### 3.2 Challenges  `/api/challenges`

#### GET `/api/challenges/`
List all challenges, optionally filtered by difficulty.

**Query params:**
- `difficulty` — `easy` | `medium` | `hard` | `expert` (optional)

**Response `200`:**
```json
{
  "challenges": [
    {
      "id": "string",
      "location_name": "string",
      "latitude": 0.0,
      "longitude": 0.0,
      "country": "string",
      "continent": "string",
      "difficulty": "medium",
      "hints": ["string"],
      "max_distance_km": 0.0
    }
  ],
  "total": 42
}
```

---

#### GET `/api/challenges/random`
Get one random challenge.

**Query params:**
- `difficulty` — `easy` | `medium` | `hard` | `expert` (optional)
- `exclude` — comma-separated challenge IDs to skip (optional)

**Response `200`:** Single `ChallengeResponse` object (same shape as above).

---

#### GET `/api/challenges/{challenge_id}`
Get a specific challenge by ID.

**Response `200`:** Single `ChallengeResponse`.
**Response `404`:** `{"detail": "Challenge not found"}`

---

#### POST `/api/challenges/guess`
Submit a lat/lng guess and receive scoring feedback.

**Request body:**
```json
{
  "challenge_id": "string",
  "guessed_lat": 48.8566,
  "guessed_lng": 2.3522
}
```

**Response `200`:**
```json
{
  "challenge_id": "string",
  "guessed_lat": 48.8566,
  "guessed_lng": 2.3522,
  "actual_lat": 48.8566,
  "actual_lng": 2.3522,
  "distance_km": 0.0,
  "threshold_km": 500.0,
  "score": 95,
  "scoring_zone": "inner",
  "is_correct": true
}
```

> `score` is 0–100. This is the canonical score value.

---

#### GET `/api/challenges/{challenge_id}/scoring-zones`
Get concentric scoring zone rings for a challenge (use to draw hint circles on the map).

**Response `200`:**
```json
{
  "challenge_id": "string",
  "threshold_km": 500.0,
  "zones": [
    {
      "inner_fraction": 0.0,
      "outer_fraction": 0.2,
      "color": "#00ff00",
      "inner_km": 0.0,
      "outer_km": 100.0
    }
  ]
}
```

---

### 3.3 Game Sessions  `/api/game`

Game sessions track a complete multi-round game for a user.

#### POST `/api/game/start`
Start a new game session. Abandons any existing active session for the user.

**Request body:**
```json
{
  "user_id": 1,
  "game_mode": "classic",
  "difficulty": "medium",
  "total_rounds": 5
}
```

- `game_mode`: `classic` | `time_attack` | `challenge` | `multiplayer`
- `difficulty`: `easy` | `medium` | `hard` | `expert`
- `total_rounds`: 1–20

**Response `200`:** `GameSessionResponse`
```json
{
  "id": 42,
  "user_id": 1,
  "game_mode": "classic",
  "status": "in_progress",
  "score": 0,
  "rounds_played": 0,
  "total_rounds": 5,
  "total_distance_error": 0.0,
  "avg_response_time": 0.0,
  "difficulty": "medium",
  "started_at": "2024-01-01T00:00:00",
  "completed_at": null
}
```

---

#### POST `/api/game/{session_id}/round`
Record a round result.

**Request body:**
```json
{
  "distance_error_km": 123.4,
  "response_time_seconds": 8.5
}
```

**Response `200`:**
```json
{
  "round_number": 1,
  "distance_error_km": 123.4,
  "response_time_seconds": 8.5,
  "points_earned": 750,
  "accuracy_percent": 82.5,
  "total_score": 750
}
```

---

#### POST `/api/game/{session_id}/end`
Close the session and get the final result.

**Response `200`:**
```json
{
  "session_id": 42,
  "user_id": 1,
  "final_score": 3200,
  "rounds_played": 5,
  "total_distance_error": 612.0,
  "avg_response_time": 9.2,
  "accuracy": 78.4,
  "grade": "B",
  "is_personal_best": false,
  "rank": 14
}
```

---

#### POST `/api/game/{session_id}/abandon`
Abandon an active session.

**Response `200`:** `{"success": true, "message": "Game abandoned successfully"}`

---

#### GET `/api/game/active/{user_id}`
Get the user's current active session.

**Response `200`:** `GameSessionResponse`  
**Response `404`:** No active session.

---

### 3.4 Scores & Leaderboard  `/api/scores`

#### GET `/api/scores/leaderboard`

**Query params:**
- `game_mode` — `classic` | `time_attack` | `challenge` | `multiplayer` (default: `classic`)
- `period` — `daily` | `weekly` | `all_time` (default: `all_time`)
- `limit` — 1–100 (default: `50`)

**Response `200`:**
```json
{
  "game_mode": "classic",
  "period": "all_time",
  "total_entries": 20,
  "entries": [
    {
      "rank": 1,
      "user_id": 7,
      "username": "geo_master",
      "display_name": "Geo Master",
      "points": 9800,
      "accuracy": 94.2,
      "game_mode": "classic",
      "achieved_at": "2024-01-01T00:00:00"
    }
  ]
}
```

---

#### GET `/api/scores/user/{user_id}/stats`

**Response `200`:**
```json
{
  "user_id": 1,
  "games_played": 12,
  "total_score": 45000,
  "best_score": 4800,
  "avg_score": 3750.0,
  "avg_accuracy": 81.3,
  "best_rank": 3
}
```

---

#### GET `/api/scores/user/{user_id}/rank`

**Query params:**
- `game_mode` — default: `classic`

**Response `200`:** `{"user_id": 1, "game_mode": "classic", "rank": 5}`

---

### 3.5 Scoring Zones  `/api/scoring/zones`

#### GET `/api/scoring/zones`
Global scoring zone config (single source of truth for zone boundaries).

**Response `200`:**
```json
{
  "zones": [...],
  "description": "Zone boundaries as fraction of threshold. inner/outer define the ring bounds."
}
```

---

## 4. TypeScript Types

Paste these into `src/types/api.ts`:

```typescript
export type GameMode = 'classic' | 'time_attack' | 'challenge' | 'multiplayer';
export type GameStatus = 'pending' | 'in_progress' | 'completed' | 'abandoned';
export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';
export type LeaderboardPeriod = 'daily' | 'weekly' | 'all_time';

// Challenges
export interface Challenge {
  id: string;
  location_name: string;
  latitude: number;
  longitude: number;
  country: string;
  continent: string;
  difficulty: Difficulty;
  hints: string[];
  max_distance_km: number;
}

export interface ChallengeListResponse {
  challenges: Challenge[];
  total: number;
}

export interface GuessRequest {
  challenge_id: string;
  guessed_lat: number;
  guessed_lng: number;
}

export interface GuessResult {
  challenge_id: string;
  guessed_lat: number;
  guessed_lng: number;
  actual_lat: number;
  actual_lng: number;
  distance_km: number;
  threshold_km: number;
  score: number;          // 0-100
  scoring_zone: string;
  is_correct: boolean;
}

export interface ScoringZone {
  inner_fraction: number;
  outer_fraction: number;
  color: string;
  inner_km: number;
  outer_km: number;
}

export interface ScoringZonesResponse {
  challenge_id: string;
  threshold_km: number;
  zones: ScoringZone[];
}

// Game Sessions
export interface StartGameRequest {
  user_id: number;
  game_mode?: GameMode;
  difficulty?: Difficulty;
  total_rounds?: number;
}

export interface GameSession {
  id: number;
  user_id: number;
  game_mode: GameMode;
  status: GameStatus;
  score: number;
  rounds_played: number;
  total_rounds: number;
  total_distance_error: number;
  avg_response_time: number;
  difficulty: Difficulty;
  started_at: string | null;
  completed_at: string | null;
}

export interface SubmitRoundRequest {
  distance_error_km: number;
  response_time_seconds: number;
}

export interface RoundResult {
  round_number: number;
  distance_error_km: number;
  response_time_seconds: number;
  points_earned: number;
  accuracy_percent: number;
  total_score: number;
}

export interface GameResult {
  session_id: number;
  user_id: number;
  final_score: number;
  rounds_played: number;
  total_distance_error: number;
  avg_response_time: float;
  accuracy: number;
  grade: string;
  is_personal_best: boolean;
  rank: number | null;
}

// Leaderboard / Scores
export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string | null;
  display_name: string | null;
  points: number;
  accuracy: number;
  game_mode: GameMode;
  achieved_at: string | null;
}

export interface LeaderboardResponse {
  game_mode: GameMode;
  period: LeaderboardPeriod;
  entries: LeaderboardEntry[];
  total_entries: number;
}

export interface UserStats {
  user_id: number;
  games_played: number;
  total_score: number;
  best_score: number;
  avg_score: number;
  avg_accuracy: number;
  best_rank: number | null;
}
```

---

## 5. Environment Variables

Create `.env.local` in the Next.js project root:

```bash
# Backend API base URL (no trailing slash)
NEXT_PUBLIC_API_URL=http://localhost:8000

# PostgreSQL (only needed if the Next.js app talks directly to the DB,
# otherwise leave these out — use the FastAPI backend instead)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geochallenge_dev
DB_USER=geochallenge
DB_PASSWORD=geochallenge_secret
```

> The backend already handles all DB access. The Next.js app only needs `NEXT_PUBLIC_API_URL` to call the FastAPI endpoints.

---

## 6. Next.js Project Setup

### Bootstrap

```bash
npx create-next-app@latest geochallenge-web \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd geochallenge-web
```

### Recommended dependencies

```bash
# Map rendering (pick one)
npm install leaflet react-leaflet @types/leaflet
# OR
npm install maplibre-gl react-map-gl

# Data fetching
npm install swr
# OR: use built-in fetch with Next.js Server Components

# Forms
npm install react-hook-form zod @hookform/resolvers
```

### Start the backend first

```bash
# From geochallenge-backend/
docker-compose up -d          # start PostgreSQL
pip install -r requirements.txt
uvicorn api.main:app --reload  # runs on :8000
```

### Start the Next.js dev server

```bash
npm run dev   # runs on :3000
```

---

## 7. Suggested Page / Route Structure

```
src/app/
├── page.tsx                   # Home — game mode selector
├── play/
│   └── page.tsx               # Main game page (globe + guess)
├── results/
│   └── [sessionId]/
│       └── page.tsx           # Post-game results screen
├── leaderboard/
│   └── page.tsx               # Leaderboard table
├── profile/
│   └── [userId]/
│       └── page.tsx           # User stats
└── layout.tsx                 # Root layout (nav, providers)
```

---

## 8. API Client Utility

Create `src/lib/api.ts`:

```typescript
import type {
  Challenge,
  ChallengeListResponse,
  GuessRequest,
  GuessResult,
  StartGameRequest,
  GameSession,
  SubmitRoundRequest,
  RoundResult,
  GameResult,
  LeaderboardResponse,
  UserStats,
  Difficulty,
  GameMode,
  LeaderboardPeriod,
} from '@/types/api';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'API error');
  }
  return res.json();
}

// Challenges
export const api = {
  challenges: {
    list: (difficulty?: Difficulty) => {
      const qs = difficulty ? `?difficulty=${difficulty}` : '';
      return req<ChallengeListResponse>(`/api/challenges/${qs}`);
    },
    random: (opts?: { difficulty?: Difficulty; exclude?: string[] }) => {
      const p = new URLSearchParams();
      if (opts?.difficulty) p.set('difficulty', opts.difficulty);
      if (opts?.exclude?.length) p.set('exclude', opts.exclude.join(','));
      return req<Challenge>(`/api/challenges/random?${p}`);
    },
    get: (id: string) => req<Challenge>(`/api/challenges/${id}`),
    guess: (body: GuessRequest) =>
      req<GuessResult>('/api/challenges/guess', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
  },

  game: {
    start: (body: StartGameRequest) =>
      req<GameSession>('/api/game/start', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    submitRound: (sessionId: number, body: SubmitRoundRequest) =>
      req<RoundResult>(`/api/game/${sessionId}/round`, {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    end: (sessionId: number) =>
      req<GameResult>(`/api/game/${sessionId}/end`, { method: 'POST' }),
    abandon: (sessionId: number) =>
      req<{ success: boolean; message: string }>(`/api/game/${sessionId}/abandon`, { method: 'POST' }),
    getActive: (userId: number) =>
      req<GameSession>(`/api/game/active/${userId}`),
  },

  scores: {
    leaderboard: (opts?: { game_mode?: GameMode; period?: LeaderboardPeriod; limit?: number }) => {
      const p = new URLSearchParams();
      if (opts?.game_mode) p.set('game_mode', opts.game_mode);
      if (opts?.period) p.set('period', opts.period);
      if (opts?.limit) p.set('limit', String(opts.limit));
      return req<LeaderboardResponse>(`/api/scores/leaderboard?${p}`);
    },
    userStats: (userId: number) =>
      req<UserStats>(`/api/scores/user/${userId}/stats`),
    userRank: (userId: number, gameMode?: GameMode) => {
      const qs = gameMode ? `?game_mode=${gameMode}` : '';
      return req<{ user_id: number; game_mode: string; rank: number }>(
        `/api/scores/user/${userId}/rank${qs}`
      );
    },
  },
};
```

---

## 9. Key Implementation Notes

### Game Flow

1. Call `api.challenges.random()` to get a challenge.
2. Render a world map; let the user click to place a pin.
3. On submit, call `api.challenges.guess({ challenge_id, guessed_lat, guessed_lng })`.
4. The response includes `distance_km`, `score` (0–100), and `scoring_zone`.
5. Optionally use `api.game.*` to persist a full multi-round session (requires a `user_id`).

### Scoring Zones

Each challenge has concentric rings. Fetch them with `GET /api/challenges/{id}/scoring-zones` and draw them on the map as overlaid circles. The `inner_km` / `outer_km` fields give the radii; `color` is a hex string.

### CORS

The backend is configured with `allow_origins=["*"]` for development. For production, update `api/main.py` to whitelist the Next.js origin.

### User ID

There is no auth system yet. For prototyping, use a fixed `user_id` (e.g. `1`) stored in `localStorage` or a cookie. A real auth layer (NextAuth.js / Clerk) can be added later — the backend just expects a numeric `user_id`.

### No SSR needed for game data

Challenge data changes per round, so fetch it client-side. Leaderboard and stats can use `next: { revalidate: 60 }` cache hints in Server Components.

### Interactive docs

With the backend running locally, visit `http://localhost:8000/docs` for the full Swagger UI — useful for exploring all request/response shapes interactively.
