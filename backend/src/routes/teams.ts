import { Router } from "express";
import { authenticateToken } from "@/middleware/auth";
import { snowflakeClient } from "@/lib/snowflake";

const router = Router();

// GET /api/v1/teams
router.get("/", authenticateToken, async (req, res) => {
  try {
    const teams = await snowflakeClient.execute(
      "SELECT * FROM SOURCE_TEAMS ORDER BY position"
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
