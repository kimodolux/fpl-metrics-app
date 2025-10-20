export interface Team {
  TEAM_ID: number;
  CODE: number;
  NAME: string;
  SHORT_NAME: string;
  POSITION: number;
  PLAYED: number;
  WIN: number;
  DRAW: number;
  LOSS: number;
  POINTS: number;
  FORM: string | null;
  STRENGTH: number;
  STRENGTH_OVERALL_HOME: number;
  STRENGTH_OVERALL_AWAY: number;
  STRENGTH_ATTACK_HOME: number;
  STRENGTH_ATTACK_AWAY: number;
  STRENGTH_DEFENCE_HOME: number;
  STRENGTH_DEFENCE_AWAY: number;
  PULSE_ID: number;
  UNAVAILABLE: boolean;
  TEAM_DIVISION: string | null;
  EXTRACTION_TIMESTAMP: string;
  EXTRACTION_DATE: string;
}

export interface TeamsResponse {
  data: Team[];
  count: number;
}
