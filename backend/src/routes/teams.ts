import { Router } from "express";
import { authenticateToken } from "@/middleware/auth";
import { snowflakeClient } from "@/lib/snowflake";

const router = Router();

// GET /api/v1/teams
router.get("/", authenticateToken, async (req, res) => {
  try {
    const query = `
      SELECT
        team_id,
        code,
        name,
        short_name,
        position,
        played,
        win,
        draw,
        loss,
        points,
        form,
        strength,
        strength_overall_home,
        strength_overall_away,
        strength_attack_home,
        strength_attack_away,
        strength_defence_home,
        strength_defence_away,
        pulse_id,
        unavailable,
        team_division,
        extraction_timestamp,
        extraction_date
      FROM SOURCE_TEAMS
      ORDER BY position
    `;

    const teams = await snowflakeClient.execute(query);

    res.status(200).json({
      data: teams,
      count: teams.length,
    });
  } catch (error) {
    console.error("Error fetching teams:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to fetch teams from Snowflake",
      },
    });
  }
});

router.get("/test", async (req, res) => {
  try {
    const teams = await snowflakeClient.execute(
      "SELECT * FROM SOURCE_TEAMS ORDER BY team_id"
    );

    res.status(200).json({
      data: teams,
      count: teams.length,
    });
  } catch (error) {
    console.error("Error fetching teams:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to fetch teams from Snowflake",
      },
    });
  }
});

export default router;
