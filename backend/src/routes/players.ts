import { Router } from "express";
import { authenticateToken } from "@/middleware/auth";
import { snowflakeClient } from "@/lib/snowflake";

const router = Router();

// GET /api/v1/players
router.get("/", authenticateToken, async (req, res) => {
  try {
    const { team, position, minPrice, maxPrice } = req.query;

    // Build dynamic WHERE clause based on filters
    const conditions: string[] = [];

    if (team) {
      conditions.push(`team = ${team}`);
    }

    if (position) {
      conditions.push(`element_type = ${position}`);
    }

    if (minPrice) {
      // Prices are stored in 0.1M units (e.g., 65 = £6.5M)
      conditions.push(`now_cost >= ${minPrice}`);
    }

    if (maxPrice) {
      conditions.push(`now_cost <= ${maxPrice}`);
    }

    const whereClause = conditions.length > 0
      ? `WHERE ${conditions.join(" AND ")}`
      : "";

    // Select relevant columns for player analytics
    const query = `
      SELECT
        player_id,
        first_name,
        second_name,
        web_name,
        team,
        element_type,
        now_cost,
        total_points,
        points_per_game,
        form,
        goals_scored,
        assists,
        expected_goals,
        expected_assists,
        expected_goal_involvements,
        expected_goals_conceded,
        clean_sheets,
        goals_conceded,
        minutes,
        selected_by_percent,
        transfers_in_event,
        transfers_out_event,
        ict_index,
        influence,
        creativity,
        threat,
        bonus,
        bps,
        yellow_cards,
        red_cards,
        saves,
        penalties_saved,
        penalties_missed,
        status
      FROM SOURCE_PLAYERS
      ${whereClause}
      ORDER BY total_points DESC
    `;

    const players = await snowflakeClient.execute(query);

    res.status(200).json({
      data: players,
      count: players.length,
    });
  } catch (error) {
    console.error("Error fetching players:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to fetch players from Snowflake",
      },
    });
  }
});

// GET /api/v1/players/:id
router.get("/:id", authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    const query = `
      SELECT
        player_id,
        first_name,
        second_name,
        web_name,
        team,
        element_type,
        now_cost,
        total_points,
        points_per_game,
        form,
        goals_scored,
        assists,
        expected_goals,
        expected_assists,
        expected_goal_involvements,
        expected_goals_conceded,
        clean_sheets,
        goals_conceded,
        minutes,
        selected_by_percent,
        transfers_in_event,
        transfers_out_event,
        ict_index,
        influence,
        creativity,
        threat,
        bonus,
        bps,
        yellow_cards,
        red_cards,
        saves,
        penalties_saved,
        penalties_missed,
        status
      FROM SOURCE_PLAYERS
      WHERE player_id = ${id}
    `;

    const players = await snowflakeClient.execute(query);

    if (players.length === 0) {
      return res.status(404).json({
        error: {
          code: "NOT_FOUND",
          message: "Player not found",
        },
      });
    }

    res.status(200).json({
      data: players[0],
    });
  } catch (error) {
    console.error("Error fetching player:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to fetch player from Snowflake",
      },
    });
  }
});

export default router;
