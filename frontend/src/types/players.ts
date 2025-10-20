export interface Player {
  PLAYER_ID: number;
  FIRST_NAME: string;
  SECOND_NAME: string;
  WEB_NAME: string;
  TEAM: number;
  ELEMENT_TYPE: number;
  NOW_COST: number;
  TOTAL_POINTS: number;
  POINTS_PER_GAME: number;
  FORM: number;
  GOALS_SCORED: number;
  ASSISTS: number;
  EXPECTED_GOALS: number;
  EXPECTED_ASSISTS: number;
  EXPECTED_GOAL_INVOLVEMENTS: number;
  EXPECTED_GOALS_CONCEDED: number;
  CLEAN_SHEETS: number;
  GOALS_CONCEDED: number;
  MINUTES: number;
  SELECTED_BY_PERCENT: number;
  TRANSFERS_IN_EVENT: number;
  TRANSFERS_OUT_EVENT: number;
  ICT_INDEX: number;
  INFLUENCE: number;
  CREATIVITY: number;
  THREAT: number;
  BONUS: number;
  BPS: number;
  YELLOW_CARDS: number;
  RED_CARDS: number;
  SAVES: number;
  PENALTIES_SAVED: number;
  PENALTIES_MISSED: number;
  STATUS: string;
}

export interface PlayersResponse {
  data: Player[];
  count: number;
}

export enum Position {
  Goalkeeper = 1,
  Defender = 2,
  Midfielder = 3,
  Forward = 4,
}

export const POSITION_LABELS: Record<Position, string> = {
  [Position.Goalkeeper]: "GK",
  [Position.Defender]: "DEF",
  [Position.Midfielder]: "MID",
  [Position.Forward]: "FWD",
};
