import { Router } from 'express';
import { AuthRequest, authenticateToken } from '@/middleware/auth';
import { prisma } from '@/lib/prisma';

const router = Router();

// GET /api/v1/users/me
router.get('/me', authenticateToken, async (req: AuthRequest, res) => {
  try {
    const userId = req.user!.id;
    
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        username: true,
        createdAt: true,
        _count: {
          select: {
            teams: true
          }
        }
      }
    });

    if (!user) {
      return res.status(404).json({
        error: {
          code: 'NOT_FOUND',
          message: 'User not found'
        }
      });
    }

    res.status(200).json({
      id: user.id,
      email: user.email,
      username: user.username,
      createdAt: user.createdAt,
      teamCount: user._count.teams
    });
  } catch (error) {
    console.error('Get user profile error:', error);
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to retrieve user profile'
      }
    });
  }
});

// PATCH /api/v1/users/me
router.patch('/me', authenticateToken, async (req: AuthRequest, res) => {
  try {
    const userId = req.user!.id;
    const { username } = req.body;

    // Validate username if provided
    if (username) {
      if (typeof username !== 'string' || username.length < 3 || username.length > 50) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Username must be 3-50 characters long'
          }
        });
      }

      if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Username can only contain letters, numbers, and underscores'
          }
        });
      }

      // Check if username is already taken
      const existingUser = await prisma.user.findFirst({
        where: {
          username,
          id: { not: userId }
        }
      });

      if (existingUser) {
        return res.status(400).json({
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Username already taken'
          }
        });
      }
    }

    const updatedUser = await prisma.user.update({
      where: { id: userId },
      data: {
        ...(username && { username })
      },
      select: {
        id: true,
        email: true,
        username: true,
        updatedAt: true
      }
    });

    res.status(200).json(updatedUser);
  } catch (error) {
    console.error('Update user profile error:', error);
    res.status(500).json({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to update user profile'
      }
    });
  }
});

export default router;