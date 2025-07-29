import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { prisma } from '@/lib/prisma';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    username: string;
  };
}

export const authenticateToken = async (req: AuthRequest, res: Response, next: NextFunction): Promise<void> => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    res.status(401).json({
      error: {
        code: 'AUTHENTICATION_ERROR',
        message: 'Access token is required'
      }
    });
    return;
  }

  try {
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error('JWT_SECRET not configured');
    }

    const decoded = jwt.verify(token, jwtSecret) as { userId: string };
    
    // Get user from database
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
      select: {
        id: true,
        email: true,
        username: true,
        isActive: true
      }
    });

    if (!user || !user.isActive) {
      res.status(401).json({
        error: {
          code: 'AUTHENTICATION_ERROR',
          message: 'Invalid or expired token'
        }
      });
      return;
    }

    req.user = {
      id: user.id,
      email: user.email,
      username: user.username
    };

    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(401).json({
      error: {
        code: 'AUTHENTICATION_ERROR',
        message: 'Invalid or expired token'
      }
    });
    return;
  }
};