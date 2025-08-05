# Fantasy Football Analytics Dashboard - Technical Specification

## 1. Overview & Architecture

### Project Overview

A web application for analyzing fantasy football player statistics, comparing players, and building experimental teams within budget constraints. The application provides data visualizations and team management capabilities for fantasy football enthusiasts.

### High-Level Architecture

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

### Technology Stack

#### Frontend

- **Framework**: React 18+ with TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand
- **UI Components**: Tailwind CSS + Headless UI
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Build Tool**: Vite

#### Backend

- **Runtime**: Node.js 20+ with TypeScript
- **Framework**: Express.js
- **Authentication**: Passport.js (local + OAuth)
- **ORM**: Prisma (for PostgreSQL)
- **Snowflake Client**: snowflake-sdk
- **Caching**: Redis
- **Validation**: Zod
- **API Documentation**: OpenAPI/Swagger

#### Infrastructure

- **Databases**:
  - PostgreSQL 15+ (users, auth, teams)
  - Snowflake (player statistics)
  - Redis (caching layer)
- **Deployment**: Docker Compose (local), Google Cloud Platform (production)

### Design Principles

1. **Separation of Concerns**: Clear distinction between user data (PostgreSQL) and analytics data (Snowflake)
2. **Performance First**: Implement caching strategy to minimize Snowflake queries
3. **Type Safety**: Full TypeScript coverage across frontend and backend
4. **Scalability**: Design for 1000 daily active users
5. **Security**: Secure authentication, API rate limiting, data validation

### Key Features

- User authentication (email/password + OAuth)
- Player statistics dashboard with interactive charts
- Player comparison tools
- Team builder with budget constraints
- Multiple team management per user

## 2. Data Models

### PostgreSQL Schema

#### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL for OAuth-only users
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### OAuth Providers Table

```sql
CREATE TABLE oauth_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google', 'github'
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_providers_user_id ON oauth_providers(user_id);
CREATE INDEX idx_oauth_providers_provider ON oauth_providers(provider, provider_user_id);
```

#### Sessions Table

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

#### Teams Table

```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    budget_remaining DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    formation VARCHAR(20), -- e.g., '4-3-3', '3-5-2'
    is_valid BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teams_user_id ON teams(user_id);
```

#### Team Players Table

```sql
CREATE TABLE team_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    player_id VARCHAR(100) NOT NULL, -- References Snowflake player data
    club_id VARCHAR(100) NOT NULL, -- For enforcing max 3 per club rule
    position VARCHAR(20) NOT NULL, -- 'GK', 'DEF', 'MID', 'FWD'
    squad_position INTEGER NOT NULL CHECK (squad_position BETWEEN 1 AND 15),
    is_captain BOOLEAN DEFAULT false,
    is_vice_captain BOOLEAN DEFAULT false,
    purchase_price DECIMAL(5,2) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, player_id),
    UNIQUE(team_id, squad_position)
);

CREATE INDEX idx_team_players_team_id ON team_players(team_id);
CREATE INDEX idx_team_players_player_id ON team_players(player_id);
CREATE INDEX idx_team_players_club_id ON team_players(team_id, club_id);
```

### Prisma Schema

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(uuid())
  email         String    @unique
  username      String    @unique
  passwordHash  String?   @map("password_hash")
  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")
  isActive      Boolean   @default(true) @map("is_active")
  lastLoginAt   DateTime? @map("last_login_at")

  oauthProviders OAuthProvider[]
  sessions       Session[]
  teams          Team[]

  @@index([email])
  @@index([username])
  @@map("users")
}

model OAuthProvider {
  id             String   @id @default(uuid())
  userId         String   @map("user_id")
  provider       String   // 'google' | 'github'
  providerUserId String   @map("provider_user_id")
  accessToken    String?  @map("access_token")
  refreshToken   String?  @map("refresh_token")
  createdAt      DateTime @default(now()) @map("created_at")
  updatedAt      DateTime @updatedAt @map("updated_at")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerUserId])
  @@index([userId])
  @@index([provider, providerUserId])
  @@map("oauth_providers")
}

model Session {
  id        String   @id @default(uuid())
  userId    String   @map("user_id")
  token     String   @unique
  expiresAt DateTime @map("expires_at")
  createdAt DateTime @default(now()) @map("created_at")
  ipAddress String?  @map("ip_address")
  userAgent String?  @map("user_agent")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([token])
  @@index([userId])
  @@index([expiresAt])
  @@map("sessions")
}

model Team {
  id              String   @id @default(uuid())
  userId          String   @map("user_id")
  name            String
  budgetRemaining Decimal  @default(100.00) @map("budget_remaining") @db.Decimal(5, 2)
  formation       String?
  isValid         Boolean  @default(false) @map("is_valid")
  createdAt       DateTime @default(now()) @map("created_at")
  updatedAt       DateTime @updatedAt @map("updated_at")

  user    User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  players TeamPlayer[]

  @@index([userId])
  @@map("teams")
}

model TeamPlayer {
  id            String   @id @default(uuid())
  teamId        String   @map("team_id")
  playerId      String   @map("player_id") // References Snowflake data
  clubId        String   @map("club_id") // For enforcing max 3 per club rule
  position      String   // 'GK' | 'DEF' | 'MID' | 'FWD'
  squadPosition Int      @map("squad_position") // 1-11 starting, 12-15 bench
  isCaptain     Boolean  @default(false) @map("is_captain")
  isViceCaptain Boolean  @default(false) @map("is_vice_captain")
  purchasePrice Decimal  @map("purchase_price") @db.Decimal(5, 2)
  addedAt       DateTime @default(now()) @map("added_at")

  team Team @relation(fields: [teamId], references: [id], onDelete: Cascade)

  @@unique([teamId, playerId])
  @@unique([teamId, squadPosition])
  @@index([teamId])
  @@index([playerId])
  @@index([teamId, clubId])
  @@map("team_players")
}
```

### Database Constraints & Business Rules

1. **User Constraints**:

   - Email must be unique and valid format
   - Username must be unique (3-50 characters)
   - OAuth users may not have password_hash

2. **Team Constraints**:

   - Max teams per user: 5
   - Budget constraint: Total team cost ≤ $100
   - Total players: Exactly 15 (11 starting + 4 substitutes)
   - Max 3 players from the same club

3. **Team Player Constraints**:
   - Squad composition (15 players total):
     - GK: Exactly 2
     - DEF: Exactly 5
     - MID: Exactly 5
     - FWD: Exactly 3
   - Squad positions:
     - 1-11: Starting XI
     - 12: Substitute goalkeeper
     - 13-15: Outfield substitutes (ordered by priority)
   - Starting XI formation:
     - Position 1: Always GK
     - Positions 2-11: Valid formation of DEF/MID/FWD
   - Valid formations:
     - 3-5-2 (3 DEF, 5 MID, 2 FWD)
     - 3-4-3 (3 DEF, 4 MID, 3 FWD)
     - 4-5-1 (4 DEF, 5 MID, 1 FWD)
     - 4-4-2 (4 DEF, 4 MID, 2 FWD)
     - 4-3-3 (4 DEF, 3 MID, 3 FWD)
     - 5-4-1 (5 DEF, 4 MID, 1 FWD)
     - 5-3-2 (5 DEF, 3 MID, 2 FWD)
   - Only one captain and one vice-captain per team
   - No duplicate players in same team

### Snowflake Schema

_To be implemented - will contain player statistics, historical performance data, and other analytical metrics_

## 3. API Design

### Base Configuration

- **Base URL**: `/api/v1`
- **Authentication**: Bearer token (JWT)
- **Content-Type**: `application/json`
- **Rate Limiting**: 100 requests per minute per user

### Authentication Endpoints

#### POST /auth/register

Register a new user with email/password

```json
// Request
{
  "email": "user@example.com",
  "username": "fantasyuser",
  "password": "securepassword"
}

// Response (200)
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "fantasyuser"
  },
  "token": "jwt-token",
  "expiresIn": 604800 // 7 days in seconds
}
```

#### POST /auth/login

Login with email/password

```json
// Request
{
  "email": "user@example.com",
  "password": "securepassword",
  "rememberMe": false // optional, extends to 30 days
}

// Response (200)
{
  "user": { /* user object */ },
  "token": "jwt-token",
  "refreshToken": "refresh-token", // if rememberMe is true
  "expiresIn": 604800
}
```

#### GET /auth/oauth/:provider

Initiate OAuth flow (Google or GitHub)

- Redirects to provider authorization page

#### GET /auth/oauth/:provider/callback

OAuth callback handler

- Exchanges code for tokens
- Creates/updates user account
- Returns JWT token

#### POST /auth/refresh

Refresh access token

```json
// Request
{
  "refreshToken": "refresh-token"
}

// Response (200)
{
  "token": "new-jwt-token",
  "expiresIn": 604800
}
```

#### POST /auth/logout

Logout and invalidate session

### User Endpoints

#### GET /users/me

Get current user profile

```json
// Response (200)
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "fantasyuser",
  "createdAt": "2025-01-15T10:00:00Z",
  "teamCount": 2
}
```

#### PATCH /users/me

Update user profile

```json
// Request
{
  "username": "newusername"
}
```

### Team Management Endpoints

#### GET /teams

Get all teams for current user

```json
// Response (200)
{
  "teams": [
    {
      "id": "uuid",
      "name": "Dream Team",
      "budgetRemaining": 15.5,
      "formation": "4-3-3",
      "isValid": true,
      "playerCount": 15,
      "createdAt": "2025-01-15T10:00:00Z",
      "updatedAt": "2025-01-20T15:30:00Z"
    }
  ]
}
```

#### POST /teams

Create a new team with initial players

```json
// Request
{
  "name": "Dream Team",
  "players": [
    {
      "playerId": "player-123",
      "squadPosition": 1
    },
    {
      "playerId": "player-456",
      "squadPosition": 2
    }
    // ... up to 15 players
  ]
}

// Response (201)
{
  "id": "uuid",
  "name": "Dream Team",
  "budgetRemaining": 15.5,
  "formation": "4-3-3", // auto-detected from players
  "isValid": true,
  "playerCount": 15,
  "players": [ /* full player details */ ],
  "validation": {
    "isValid": true,
    "errors": [],
    "warnings": []
  }
}
```

#### GET /teams/:teamId

Get team details with all players

```json
// Response (200)
{
  "id": "uuid",
  "name": "Dream Team",
  "budgetRemaining": 15.5,
  "formation": "4-3-3",
  "isValid": true,
  "players": [
    {
      "id": "uuid",
      "playerId": "player-123",
      "playerName": "Mohamed Salah", // from Snowflake
      "clubId": "liverpool",
      "clubName": "Liverpool", // from Snowflake
      "position": "MID",
      "squadPosition": 7,
      "isCaptain": true,
      "isViceCaptain": false,
      "purchasePrice": 13.0,
      "currentPrice": 13.5, // from Snowflake
      "points": 125, // from Snowflake
      "form": 8.5 // from Snowflake
    }
    // ... 14 more players
  ],
  "validation": {
    "isValid": true,
    "errors": [],
    "warnings": []
  }
}
```

#### PUT /teams/:teamId

Update entire team (replaces all players)

```json
// Request
{
  "name": "Updated Dream Team",
  "players": [
    {
      "playerId": "player-123",
      "squadPosition": 1,
      "isCaptain": false,
      "isViceCaptain": true
    },
    {
      "playerId": "player-789",
      "squadPosition": 2,
      "isCaptain": true,
      "isViceCaptain": false
    }
    // ... all 15 players (or partial for draft mode)
  ]
}

// Response (200)
{
  "id": "uuid",
  "name": "Updated Dream Team",
  "budgetRemaining": 12.0,
  "formation": "4-4-2",
  "isValid": true,
  "players": [ /* full player details */ ],
  "validation": {
    "isValid": true,
    "errors": [],
    "warnings": []
  }
}
```

#### DELETE /teams/:teamId

Delete a team

### Player Data Endpoints (Snowflake)

**TODO**: Define specific endpoints once Snowflake schema is decided. Will include:

- Player listing with filters and search
- Individual player statistics and history
- Player comparison tools
- Performance analytics and predictions

### Error Responses

All errors follow consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

Error Codes:

- `AUTHENTICATION_ERROR` (401)
- `AUTHORIZATION_ERROR` (403)
- `NOT_FOUND` (404)
- `VALIDATION_ERROR` (400)
- `TEAM_LIMIT_EXCEEDED` (400)
- `BUDGET_EXCEEDED` (400)
- `INVALID_FORMATION` (400)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_ERROR` (500)

## 4. Frontend Components & Routes

### Route Structure

```
/                           # Landing page (redirects to /login or /dashboard)
/login                      # Login page
/register                   # Registration page
/auth/callback/:provider    # OAuth callback handler

# Authenticated routes
/dashboard                  # Main dashboard with team overview
/teams                      # List all user teams
/teams/new                  # Create new team
/teams/:teamId              # View/edit specific team

/players                    # Player list/search
/players/:playerId          # Player detail view
/compare                    # Player comparison tool
```

### Component Architecture (MVP)

```
src/
├── components/
│   ├── common/
│   │   ├── Layout.tsx          # App layout with navigation
│   │   ├── PrivateRoute.tsx    # Auth route wrapper
│   │   └── LoadingSpinner.tsx  # Loading states
│   │
│   ├── auth/
│   │   ├── LoginForm.tsx       # Email/password login
│   │   ├── RegisterForm.tsx    # User registration
│   │   └── OAuthButton.tsx     # Google/GitHub login
│   │
│   ├── team/
│   │   ├── TeamList.tsx        # Display user's teams
│   │   ├── TeamCard.tsx        # Team summary card
│   │   ├── TeamBuilder.tsx     # Team editing interface
│   │   ├── PlayerSlot.tsx      # Player position slot
│   │   └── BudgetBar.tsx       # Budget indicator
│   │
│   ├── player/
│   │   ├── PlayerList.tsx      # Player table with search
│   │   ├── PlayerCard.tsx      # Player info card
│   │   └── PlayerSearch.tsx    # Search/filter controls
│   │
│   └── charts/
│       └── StatsChart.tsx      # Basic player stats chart
│
├── pages/
│   ├── Dashboard.tsx           # Home page after login
│   ├── Teams.tsx              # Team management page
│   ├── TeamDetail.tsx         # Single team view/edit
│   ├── Players.tsx            # Player browser
│   └── Compare.tsx            # Player comparison
│
├── hooks/
│   ├── useAuth.ts             # Authentication hook
│   ├── useTeam.ts             # Team operations
│   └── usePlayer.ts           # Player data fetching
│
├── stores/
│   ├── authStore.ts           # Zustand auth state
│   └── teamStore.ts           # Zustand team state
│
├── services/
│   ├── api.ts                 # Axios configuration
│   ├── auth.service.ts        # Auth API calls
│   └── team.service.ts        # Team API calls
│
└── types/
    └── index.ts               # TypeScript types
```

### Key Components (MVP Focus)

#### TeamBuilder

- Display 15 player slots (1-11 starting, 12-15 bench)
- Add/remove players functionality
- Show current formation
- Display budget remaining
- Save team changes

#### PlayerList

- Table view of all players
- Basic search by name
- Filter by position
- Add to team functionality

#### TeamCard

- Team name and formation
- Total team value
- Valid/invalid status indicator
- Edit and delete actions

### State Management (Zustand)

#### Auth Store

- User session management
- Login/logout functionality
- Token storage

#### Team Store

- Current user's teams
- Active team being edited
- Basic CRUD operations

### UI/UX Patterns

#### Mobile Responsiveness

- **Responsive grid** for team cards
- **Bottom sheet** pattern for mobile player selection
- **Touch-friendly** drag handles
- **Simplified mobile formation** view

#### Loading States

- **Skeleton screens** for initial loads
- **Optimistic updates** for team changes
- **Progress indicators** for saves
- **Stale-while-revalidate** for player data

#### Error Handling

- **Toast notifications** for transient errors
- **Inline validation** messages
- **Retry mechanisms** with exponential backoff
- **Offline support** with sync queue

#### Accessibility

- **ARIA labels** for all interactive elements
- **Keyboard navigation** for team builder
- **Screen reader** announcements
- **High contrast** mode support

## 5. Caching & Performance

### Caching Strategy

#### Redis Cache Layers

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   API +     │────▶│   Redis     │
│   (React)   │     │   Node.js   │     │   Cache     │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼─────┐ ┌────▼────┐
              │PostgreSQL │ │Snowflake│
              └───────────┘ └─────────┘
```

#### Cache Levels

1. **Client-Side Caching**

   - Browser localStorage for user preferences
   - React Query / SWR for API response caching
   - Service Worker for offline support
   - Cache duration: 5 minutes for dynamic data

2. **API Response Caching (Redis)**

   ```
   Key Pattern                          TTL
   ----------------------------------------
   auth:session:{token}                 7 days
   user:teams:{userId}                  5 minutes
   team:detail:{teamId}                 5 minutes
   players:all                          7 days
   players:detail:{playerId}            7 days
   players:search:{hash}                1 hour
   ```

3. **Database Query Caching**
   - PostgreSQL: Use prepared statements
   - Snowflake: Result set caching (built-in)

### Performance Optimizations

#### Backend Optimizations

1. **Database Performance**

   ```sql
   -- Composite indexes for common queries
   CREATE INDEX idx_teams_user_created
   ON teams(user_id, created_at DESC);

   CREATE INDEX idx_team_players_composite
   ON team_players(team_id, squad_position);

   -- Materialized view for team summaries
   CREATE MATERIALIZED VIEW team_summaries AS
   SELECT
     t.id,
     t.user_id,
     t.name,
     COUNT(tp.id) as player_count,
     SUM(tp.purchase_price) as total_cost,
     t.formation,
     t.is_valid
   FROM teams t
   LEFT JOIN team_players tp ON t.id = tp.team_id
   GROUP BY t.id;
   ```

2. **API Optimizations**

   - **Batch loading**: DataLoader pattern for N+1 queries
   - **Pagination**: Cursor-based for large datasets
   - **Compression**: gzip responses
   - **Connection pooling**: PostgreSQL (20) and Snowflake (10)

3. **Snowflake Query Optimization**

   ```sql
   -- Clustering for common access patterns
   ALTER TABLE player_stats
   CLUSTER BY (season, gameweek, player_id);

   -- Pre-aggregated views
   CREATE VIEW player_current_stats AS
   SELECT * FROM player_stats
   WHERE season = CURRENT_SEASON()
   AND gameweek = LATEST_GAMEWEEK();
   ```

#### Frontend Optimizations

1. **Bundle Size Reduction**

   - Lazy load routes with React.lazy()
   - Tree-shake Recharts imports
   - Use production builds of libraries
   - Target: < 200KB initial bundle

2. **Rendering Performance**

   - React.memo for expensive components
   - useMemo/useCallback for computed values
   - Virtual scrolling for player lists
   - Debounce search inputs (300ms)

3. **Network Optimization**
   - HTTP/2 multiplexing
   - Preload critical resources
   - Image optimization (WebP format)
   - API request batching

### Monitoring & Metrics

#### Performance Metrics to Track

1. **API Metrics**

   - Response time percentiles (p50, p95, p99)
   - Cache hit rates
   - Database query times
   - Snowflake credit usage

2. **Frontend Metrics**

   - Core Web Vitals (LCP, FID, CLS)
   - Time to Interactive (TTI)
   - Bundle sizes
   - API call frequency

3. **Business Metrics**
   - User session duration
   - Team save success rate
   - Player search effectiveness
   - Feature adoption rates

#### Monitoring Tools

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-loki-datasource

  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./promtail-config.yaml:/etc/promtail/config.yml
      - /var/log:/var/log
      - ./logs:/app/logs # Application logs
    command: -config.file=/etc/promtail/config.yml

  redis-exporter:
    image: oliver006/redis_exporter
    environment:
      - REDIS_ADDR=redis:6379

volumes:
  loki_data:
```

#### Application Logging Setup

```typescript
// src/utils/logger.ts
import winston from "winston";
import LokiTransport from "winston-loki";

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: "fantasy-football-api",
    environment: process.env.NODE_ENV,
  },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: winston.format.simple(),
    }),
    // Loki transport for production
    new LokiTransport({
      host: process.env.LOKI_URL || "http://loki:3100",
      labels: { app: "fantasy-football" },
      batching: true,
      interval: 5,
    }),
  ],
});

export default logger;
```

### Scaling Considerations

#### Horizontal Scaling Plan

1. **Phase 1 (MVP - 100 users)**

   - Single Node.js instance
   - Single Redis instance
   - Shared PostgreSQL
   - Basic monitoring

2. **Phase 2 (1000 users)**

   - 2-3 Node.js instances with load balancer
   - Redis with persistence enabled
   - Read replicas for PostgreSQL
   - CDN for static assets

3. **Phase 3 (10,000+ users)**
   - Auto-scaling Node.js cluster
   - Redis Cluster for cache
   - PostgreSQL with pgBouncer
   - Snowflake warehouse scaling
   - Global CDN distribution

#### Cost Optimization

1. **Snowflake Cost Control**

   - Use smallest warehouse size (X-Small)
   - Auto-suspend after 60 seconds
   - Query result caching
   - Weekly data refresh only

2. **GCP Cost Management**
   - Use preemptible instances for workers
   - Cloud CDN for static assets
   - Committed use discounts
   - Resource quotas and alerts

### Development Performance

#### Local Development

```yaml
# docker-compose.dev.yml
services:
  app:
    build: .
    volumes:
      - ./src:/app/src # Hot reload
    environment:
      - NODE_ENV=development
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=fantasy_football
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

#### CI/CD Pipeline Performance

- Parallel test execution
- Docker layer caching
- Dependency caching
- Progressive deployment (canary releases)

## 6. Development Phases - Task Checklist

### Phase 1: Foundation (Weeks 1-3)

#### Infrastructure Setup

- [x] Create project repository with .gitignore
- [x] Set up Docker Compose for local development
- [x] Configure PostgreSQL container with initial database
- [ ] Set up Redis container
- [x] Create TypeScript configurations for frontend and backend
- [x] Set up ESLint and Prettier
- [ ] Configure environment variables (.env files)
- [ ] Set up basic CI/CD pipeline (GitHub Actions/GitLab CI)

#### Backend Foundation

- [x] Initialize Node.js/Express project with TypeScript
- [x] Set up Prisma ORM
- [ ] Create database migrations for users, sessions, teams tables
- [ ] Implement error handling middleware
- [ ] Set up Winston logger with Loki transport
- [x] Configure CORS and security middleware
- [x] Create health check endpoint

#### Authentication System

- [x] Implement user registration endpoint
- [x] Implement login endpoint with JWT
- [x] Create password hashing with bcrypt
- [x] Implement JWT token generation and validation
- [x] Create auth middleware for protected routes
- [ ] Set up Redis session storage
- [x] Implement logout endpoint
- [x] Add input validation with Zod

#### Frontend Foundation

- [x] Create React app with TypeScript (Vite)
- [x] Set up React Router
- [x] Configure Tailwind CSS
- [ ] Create basic layout component
- [x] Implement Zustand auth store
- [x] Create login page component
- [ ] Create registration page component (Done but need OAuth)
- [ ] Implement protected route wrapper
- [ ] Set up Axios with interceptors

#### Basic Team Management

- [ ] Create team CRUD API endpoints
- [ ] Implement team creation with 5-team limit
- [ ] Create team list endpoint
- [ ] Create team update endpoint
- [ ] Create team deletion endpoint
- [ ] Build TeamList component
- [ ] Build TeamCard component
- [ ] Create new team page
- [ ] Implement team name editing

### Phase 2: Player Integration (Weeks 4-6)

#### Snowflake Setup

- [ ] Set up Snowflake connection in Node.js
- [ ] Create connection pool configuration
- [ ] Implement query timeout handling
- [ ] Create player data access layer
- [ ] Set up mock player data for development
- [ ] Implement Snowflake query caching

#### Player API Endpoints

- [ ] Create GET /players endpoint with pagination
- [ ] Implement player search functionality
- [ ] Add position and price filters
- [ ] Create player data transformation layer
- [ ] Implement Redis caching for player data
- [ ] Add cache invalidation strategy
- [ ] Create player enrichment service

#### Team Builder Backend

- [ ] Update team model to include players
- [ ] Implement PUT /teams/:id endpoint for bulk updates
- [ ] Add formation validation logic
- [ ] Implement budget calculation
- [ ] Add squad position validation (1-15)
- [ ] Implement max 3 players per club rule
- [ ] Add captain/vice-captain validation
- [ ] Create team validation service

#### Team Builder Frontend

- [ ] Create TeamBuilder component
- [ ] Build PlayerSlot component
- [ ] Implement player addition modal
- [ ] Create player removal functionality
- [ ] Build BudgetBar component
- [ ] Add formation display
- [ ] Implement captain selection UI
- [ ] Add squad position management
- [ ] Create save team functionality

#### Player Browser

- [ ] Build PlayerList component
- [ ] Implement player search UI
- [ ] Create position filter dropdown
- [ ] Add price range slider
- [ ] Build PlayerCard component
- [ ] Implement pagination controls
- [ ] Add loading states
- [ ] Create empty state designs

### Phase 3: Polish & Performance (Weeks 7-8)

#### OAuth Integration

- [ ] Configure Passport.js
- [ ] Implement Google OAuth strategy
- [ ] Create Google OAuth callback handler
- [ ] Implement GitHub OAuth strategy
- [ ] Create GitHub OAuth callback handler
- [ ] Update user model for OAuth providers
- [ ] Build OAuth button components
- [ ] Add OAuth error handling

#### Enhanced Authentication

- [ ] Implement refresh token functionality
- [ ] Add "Remember Me" feature
- [ ] Create password reset request endpoint
- [ ] Build password reset email template
- [ ] Implement password reset confirmation
- [ ] Add rate limiting to auth endpoints
- [ ] Create account verification flow

#### UI/UX Improvements

- [ ] Implement responsive grid layouts
- [ ] Add loading skeletons
- [ ] Create error boundary component
- [ ] Build toast notification system
- [ ] Add form validation feedback
- [ ] Implement mobile navigation
- [ ] Create empty states for all views
- [ ] Add confirmation dialogs

#### Performance Optimization

- [ ] Implement React.lazy for routes
- [ ] Add React Query for data fetching
- [ ] Optimize bundle with code splitting
- [ ] Compress API responses with gzip
- [ ] Add database query optimization
- [ ] Implement image optimization
- [ ] Add service worker for offline support
- [ ] Create performance monitoring dashboard

#### Monitoring Setup

- [ ] Deploy Prometheus configuration
- [ ] Set up Grafana dashboards
- [ ] Configure Loki for log aggregation
- [ ] Create Promtail configuration
- [ ] Add application metrics
- [ ] Set up alerts for critical issues
- [ ] Create runbooks for common issues

#### Production Deployment

- [ ] Create production Dockerfiles
- [ ] Set up GCP project
- [ ] Configure Cloud Run services
- [ ] Set up Cloud SQL for PostgreSQL
- [ ] Configure Redis on GCP
- [ ] Set up Cloud CDN
- [ ] Configure SSL certificates
- [ ] Set up domain and DNS
- [ ] Create deployment scripts
- [ ] Implement health checks

### Phase 4: Advanced Features (Weeks 9-12)

#### Player Comparison

- [ ] Design comparison API endpoint
- [ ] Create comparison algorithm
- [ ] Build comparison UI layout
- [ ] Implement player selection for comparison
- [ ] Create comparison charts
- [ ] Add stat normalization
- [ ] Build shareable comparison links

#### Analytics Dashboard

- [ ] Create team statistics calculator
- [ ] Build analytics API endpoints
- [ ] Implement performance charts
- [ ] Create form indicators
- [ ] Add position distribution chart
- [ ] Build club distribution view
- [ ] Implement export functionality

#### Enhanced Team Features

- [ ] Add team duplication endpoint
- [ ] Build team copy UI
- [ ] Create formation visualization
- [ ] Implement drag-and-drop for players
- [ ] Add auto-pick algorithm
- [ ] Build team suggestions UI
- [ ] Create team history tracking

#### Data Enrichment

- [ ] Add fixture difficulty calculation
- [ ] Implement player availability tracking
- [ ] Create injury/suspension indicators
- [ ] Add price change predictions
- [ ] Build news aggregation service
- [ ] Implement predicted points algorithm

#### Testing & Documentation

- [ ] Write unit tests for all services
- [ ] Create integration tests for APIs
- [ ] Build E2E tests with Cypress
- [ ] Write component tests
- [ ] Create API documentation
- [ ] Build user guide
- [ ] Create developer documentation
- [ ] Implement automated testing in CI

#### Final Polish

- [ ] Conduct security audit
- [ ] Perform load testing
- [ ] Optimize database queries
- [ ] Review and refactor code
- [ ] Update all dependencies
- [ ] Create backup strategies
- [ ] Set up monitoring alerts
- [ ] Plan maintenance windows
