import { Router } from "express";
import { authenticateToken } from "@/middleware/auth";

const router = Router();

// GET /api/v1/manager/:managerId
router.get("/:managerId", authenticateToken, async (req, res) => {
  try {
    const { managerId } = req.params;

    // Fetch manager history from FPL API
    const response = await fetch(
      `https://fantasy.premierleague.com/api/entry/${managerId}/history/`
    );
    console.log(response)

    if (!response.ok) {
      return res.status(404).json({
        error: {
          code: "NOT_FOUND",
          message: "Manager not found",
        },
      });
    }

    const data = await response.json();

    return res.status(200).json({
      data,
    });
  } catch (error) {
    console.error("Error fetching manager data:", error);
    return res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to fetch manager data",
      },
    });
  }
});

export default router;
