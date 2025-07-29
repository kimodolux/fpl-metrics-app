# Premier League Fantasy Football App

A full-stack TypeScript application for managing Premier League Fantasy Football teams with user authentication, team management, and league functionality.

## Project Structure

```
├── frontend/          # React + TypeScript + Vite
└── backend/           # Node.js + Express + TypeScript
```

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite for build tooling
- Better-Auth React client
- TanStack Query for data fetching
- Axios for HTTP requests

### Backend
- Node.js + Express + TypeScript
- Better-Auth for authentication (email/password + OAuth)
- Drizzle ORM + PostgreSQL
- Security middleware (helmet, cors, morgan)

## Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL database
- Google OAuth credentials (optional)
- Facebook OAuth credentials (optional)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your database credentials and OAuth keys

5. Generate and run database migrations:
   ```bash
   npm run db:generate
   npm run db:migrate
   ```

6. Start development server:
   ```bash
   npm run dev
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Database Schema

The application includes tables for:
- **Users & Authentication**: Better-Auth compatible user management
- **FPL Data**: Players, teams, fixtures, gameweeks, and statistics
- **User Teams**: Fantasy teams created by users with formations and budgets
- **Leagues**: Private leagues for competing with friends
- **Transfers**: Player transfer tracking
- **Team Selections**: Weekly team selections with captains

## API Endpoints

### Authentication (Better-Auth)
- `POST /api/auth/sign-up` - User registration
- `POST /api/auth/sign-in` - User login
- `GET /api/auth/session` - Get current session
- `POST /api/auth/sign-out` - User logout
- OAuth endpoints for Google and Facebook

### Protected Routes
- `GET/POST/PUT /api/user-teams` - Team management
- `POST /api/user-teams/:id/transfers` - Player transfers
- `GET/POST /api/leagues` - League management
- `POST /api/leagues/:id/join` - Join league

### Public Routes
- `GET /api/players` - Browse players with filters
- `GET /api/players/:id/stats` - Player statistics
- `GET /api/gameweeks/current` - Current gameweek info

## Features

- ✅ User registration and authentication
- ✅ OAuth integration (Google, Facebook)
- ✅ Team creation with budget constraints
- ✅ Player browsing and statistics
- ✅ Transfer system
- ✅ Private leagues
- ✅ Gameweek scoring
- ✅ Responsive design

## Development

- Backend runs on `http://localhost:3001`
- Frontend runs on `http://localhost:5173`
- Database migrations in `backend/drizzle/`
- Better-Auth handles user sessions and OAuth flows