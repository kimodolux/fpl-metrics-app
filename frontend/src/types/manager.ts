export interface GameweekHistory {
  event: number;
  points: number;
  total_points: number;
  rank: number;
  overall_rank: number;
  percentile_rank: number;
  bank: number;
  value: number;
  event_transfers: number;
  event_transfers_cost: number;
  points_on_bench: number;
}

export interface PastSeason {
  season_name: string;
  total_points: number;
  rank: number;
}

export interface ChipUsage {
  name: string;
  time: string;
  event: number;
}

export interface ManagerHistory {
  current: GameweekHistory[];
  past: PastSeason[];
  chips: ChipUsage[];
}

export interface ManagerHistoryResponse {
  data: ManagerHistory;
}
