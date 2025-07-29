# Fantasy Football Analytics Dashboard

A web application for analyzing fantasy football player statistics, comparing players, and building experimental teams within budget constraints. The application provides data visualizations and team management capabilities for fantasy football enthusiasts.

## Project Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React SPA     │────▶│   Node.js API   │────▶│   PostgreSQL    │
│  (TypeScript)   │     │  (TypeScript)   │     │  (Users/Auth)   │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 │               ┌─────────────────┐
                                 └──────────────▶│    Snowflake    │
                                                 │ (Player Stats)  │
                                                 └─────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand
- **UI Components**: Tailwind CSS + Headless UI
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Build Tool**: Vite

### Backend
- **Runtime**: Node.js 20+ with TypeScript
- **Framework**: Express.js
- **Authentication**: Passport.js (local + OAuth)
- **ORM**: Prisma (for PostgreSQL)
- **Snowflake Client**: snowflake-sdk
- **Caching**: Redis
- **Validation**: Zod
- **API Documentation**: OpenAPI/Swagger

### Infrastructure
- **Databases**:
  - PostgreSQL 15+ (users, auth, teams)
  - Snowflake (player statistics)
  - Redis (caching layer)
- **Deployment**: Docker Compose (local), Google Cloud Platform (production)

## Getting Started

### Prerequisites
- Node.js 20+
- Docker and Docker Compose
- PostgreSQL database
- Snowflake account (for player statistics)
- Redis instance
- Google OAuth credentials (optional)
- GitHub OAuth credentials (optional)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fantasy-football-analytics
   ```

2. Start infrastructure services:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   npm install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Update with your database, Snowflake, and OAuth credentials
   ```

5. Run database migrations:
   ```bash
   npx prisma migrate dev
   npx prisma generate
   ```

6. Start backend development server:
   ```bash
   npm run dev
   ```

7. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```

8. Start frontend development server:
   ```bash
   npm run dev
   ```

## Database Schema

### PostgreSQL (User Data)
- **Users**: User accounts with email/password and OAuth providers
- **Sessions**: JWT token management and session tracking
- **Teams**: User-created fantasy teams with budget constraints
- **Team Players**: Player selections for each team (15 players max)

### Snowflake (Analytics Data)
- **Player Statistics**: Historical performance data and analytics
- **Fixture Data**: Match information and difficulty ratings
- **Performance Metrics**: Advanced statistics and predictions

### Business Rules
- **Team Constraints**:
  - Maximum 5 teams per user
  - Exactly 15 players per team (11 starting + 4 substitutes)
  - Budget limit: $100.00 total team cost
  - Maximum 3 players from same club
  - Required positions: 2 GK, 5 DEF, 5 MID, 3 FWD

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration with email/password
- `POST /login` - User authentication 
- `GET /oauth/:provider` - OAuth flow initiation (Google, GitHub)
- `GET /oauth/:provider/callback` - OAuth callback handler
- `POST /refresh` - Refresh access token
- `POST /logout` - Session termination

### User Management (`/api/v1/users`)
- `GET /me` - Get current user profile
- `PATCH /me` - Update user profile

### Team Management (`/api/v1/teams`)
- `GET /` - List all user teams
- `POST /` - Create new team with players
- `GET /:teamId` - Get team details with player statistics  
- `PUT /:teamId` - Update entire team
- `DELETE /:teamId` - Delete team

### Player Data (`/api/v1/players`) 
- `GET /` - Browse players with filters and search
- `GET /:playerId` - Individual player statistics
- `GET /:playerId/stats` - Historical performance data
- `POST /compare` - Player comparison analytics

## Key Features

### Core Functionality
- **User Authentication**: Email/password + OAuth (Google, GitHub)
- **Team Builder**: Create teams with budget constraints and formation validation
- **Player Analytics**: Interactive charts and performance visualizations
- **Player Comparison**: Side-by-side player analysis tools
- **Multi-Team Management**: Create and manage up to 5 teams per user

### Technical Features
- **Real-time Data**: Snowflake integration for live player statistics
- **Caching Strategy**: Redis-powered performance optimization
- **Responsive Design**: Mobile-first UI with Tailwind CSS
- **Type Safety**: Full TypeScript coverage across frontend and backend

## Caching & Performance

### Cache Strategy
```
Client (React Query) → API (Redis) → PostgreSQL + Snowflake
```

- **Client-side**: 5 minutes for dynamic data, localStorage for preferences
- **API-level**: Redis caching with smart TTL (5min-7days)
- **Database**: Optimized queries with composite indexes

### Performance Targets
- **Initial Bundle**: < 200KB
- **API Response**: < 500ms p95
- **Core Web Vitals**: LCP < 2.5s, FID < 100ms
- **Cache Hit Rate**: > 80% for player data

## Development Phases

### Phase 1: Foundation (Weeks 1-3)
- [x] Project setup with Docker Compose
- [x] Authentication system (Passport.js + JWT)
- [x] Basic team CRUD operations
- [x] PostgreSQL schema with Prisma
- [ ] Redis caching implementation

### Phase 2: Player Integration (Weeks 4-6)
- [ ] Snowflake connection and query optimization
- [ ] Player API endpoints with search/filtering
- [ ] Team builder with formation validation
- [ ] Player browser with advanced UI

### Phase 3: Analytics & Polish (Weeks 7-8)
- [ ] Player comparison tools
- [ ] Performance charts with Recharts
- [ ] OAuth integration (Google, GitHub)
- [ ] Responsive UI optimization

### Phase 4: Advanced Features (Weeks 9-12)
- [ ] Advanced analytics dashboard
- [ ] Predictive algorithms
- [ ] Performance monitoring (Prometheus + Grafana)
- [ ] Production deployment on GCP

## Local Development

- **Backend**: `http://localhost:3001`
- **Frontend**: `http://localhost:5173` 
- **Database**: PostgreSQL on `localhost:5432`
- **Cache**: Redis on `localhost:6379`
- **Monitoring**: Grafana on `http://localhost:3000`