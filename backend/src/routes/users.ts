import { Router } from "express";
import { authenticateToken } from "@/middleware/auth";
import { prisma } from "@/lib/prisma";

const router = Router();

// GET /api/v1/users/me
router.get("/me", authenticateToken, async (req, res) => {
  try {
    const userId = req.user!.id;

    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        managerId: true,
        createdAt: true,
        _count: {
          select: {
            teams: true,
          },
        },
      },
    });

    if (!user) {
      return res.status(404).json({
        error: {
          code: "NOT_FOUND",
          message: "User not found",
        },
      });
    }

    res.status(200).json({
      id: user.id,
      email: user.email,
      managerId: user.managerId,
      createdAt: user.createdAt,
      teamCount: user._count.teams,
    });
  } catch (error) {
    console.error("Get user profile error:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to retrieve user profile",
      },
    });
  }
  return;
});

// PATCH /api/v1/users/me
router.patch("/me", authenticateToken, async (req, res) => {
  try {
    const userId = req.user!.id;
    const { managerId } = req.body;

    // Validate managerId if provided
    if (managerId) {
      if (typeof managerId !== "string" || managerId.length < 1) {
        return res.status(400).json({
          error: {
            code: "VALIDATION_ERROR",
            message: "Manager ID is required",
          },
        });
      }

      if (!/^\d+$/.test(managerId)) {
        return res.status(400).json({
          error: {
            code: "VALIDATION_ERROR",
            message: "Manager ID must be a valid number",
          },
        });
      }
    }

    const updatedUser = await prisma.user.update({
      where: { id: userId },
      data: {
        ...(managerId && { managerId }),
      },
      select: {
        id: true,
        email: true,
        managerId: true,
        updatedAt: true,
      },
    });

    res.status(200).json(updatedUser);
  } catch (error) {
    console.error("Update user profile error:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to update user profile",
      },
    });
  }
  return;
});

export default router;
