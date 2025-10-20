import { Router } from "express";
import { authenticateToken } from "@/middleware/auth";
import { snowflakeClient } from "@/lib/snowflake";

const router = Router();

// GET /api/v1/players
router.get("/", authenticateToken, async (req, res) => {
  try {
    const { team, position, minPrice, maxPrice, page = "1", limit = "50" } = req.query;

    // Parse pagination parameters
    const pageNum = Math.max(1, parseInt(page as string, 10));
    const limitNum = Math.min(100, Math.max(1, parseInt(limit as string, 10))); // Max 100 per page
    const offset = (pageNum - 1) * limitNum;

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

    // Get total count for pagination
    const countQuery = `
      SELECT COUNT(*) as total
      FROM SOURCE_PLAYERS
      ${whereClause}
    `;

    const countResult = await snowflakeClient.execute(countQuery);
    const totalCount = countResult[0]?.TOTAL || 0;

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
      LIMIT ${limitNum}
      OFFSET ${offset}
    `;

    const players = await snowflakeClient.execute(query);

    const totalPages = Math.ceil(totalCount / limitNum);

    res.status(200).json({
      data: players,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total: totalCount,
        totalPages: totalPages,
        hasNextPage: pageNum < totalPages,
        hasPreviousPage: pageNum > 1,
      },
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

    return res.status(200).json({
      data: players[0],
    });
  } catch (error) {
    console.error("Error fetching player:", error);
    return res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to fetch player from Snowflake",
      },
    });
  }
});

export default router;
