import bcrypt from "bcrypt";
import jwt, { SignOptions } from "jsonwebtoken";
import { prisma } from "@/lib/prisma";
import { RegisterInput, LoginInput } from "@/schemas/auth";

export class AuthService {
  private static readonly SALT_ROUNDS = 12;
  private static readonly JWT_EXPIRES_IN = 604800; // 7 days in seconds
  private static readonly REFRESH_TOKEN_EXPIRES_IN = 2592000; // 30 days in seconds

  static async register(data: RegisterInput) {
    const { email, managerId, password } = data;

    // Check if email already exists
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      throw new Error("EMAIL_EXISTS");
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, this.SALT_ROUNDS);

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        managerId,
        passwordHash,
      },
      select: {
        id: true,
        email: true,
        managerId: true,
        createdAt: true,
      },
    });

    // Generate tokens
    const { accessToken, refreshToken } = this.generateTokens(user.id);

    // Store session
    await this.createSession(user.id, refreshToken);

    return {
      user,
      accessToken,
      refreshToken,
      expiresIn: this.JWT_EXPIRES_IN,
    };
  }

  static async login(data: LoginInput, ipAddress?: string, userAgent?: string) {
    const { email, password, rememberMe } = data;

    // Find user
    const user = await prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        email: true,
        managerId: true,
        passwordHash: true,
        isActive: true,
      },
    });

    if (!user || !user.isActive) {
      throw new Error("INVALID_CREDENTIALS");
    }

    // Verify password
    if (!user.passwordHash) {
      throw new Error("OAUTH_USER"); // User registered via OAuth
    }

    const isValidPassword = await bcrypt.compare(password, user.passwordHash);
    if (!isValidPassword) {
      throw new Error("INVALID_CREDENTIALS");
    }

    // Update last login
    await prisma.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() },
    });

    // Generate tokens
    const expiresIn = rememberMe
      ? this.REFRESH_TOKEN_EXPIRES_IN
      : this.JWT_EXPIRES_IN;
    const { accessToken, refreshToken } = this.generateTokens(
      user.id,
      expiresIn
    );

    // Store session
    await this.createSession(user.id, refreshToken, ipAddress, userAgent);

    return {
      user: {
        id: user.id,
        email: user.email,
        managerId: user.managerId,
      },
      accessToken,
      refreshToken: rememberMe ? refreshToken : undefined,
      expiresIn,
    };
  }

  static async refreshToken(refreshToken: string) {
    try {
      const jwtSecret = process.env.JWT_SECRET;
      if (!jwtSecret) {
        throw new Error("JWT_SECRET not configured");
      }

      const decoded = jwt.verify(refreshToken, jwtSecret) as { userId: string };

      // Verify session exists and is valid
      const session = await prisma.session.findFirst({
        where: {
          token: refreshToken,
          userId: decoded.userId,
          expiresAt: {
            gt: new Date(),
          },
        },
        include: {
          user: {
            select: {
              id: true,
              email: true,
              managerId: true,
              isActive: true,
            },
          },
        },
      });

      if (!session || !session.user.isActive) {
        throw new Error("INVALID_REFRESH_TOKEN");
      }

      // Generate new access token
      const { accessToken } = this.generateTokens(session.user.id);

      return {
        accessToken,
        expiresIn: this.JWT_EXPIRES_IN,
      };
    } catch (error) {
      throw new Error("INVALID_REFRESH_TOKEN");
    }
  }

  static async logout(refreshToken: string) {
    // Delete the session
    await prisma.session.deleteMany({
      where: { token: refreshToken },
    });
  }

  private static generateTokens(
    userId: string,
    expiresIn: number = this.JWT_EXPIRES_IN
  ) {
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      throw new Error("JWT_SECRET not configured");
    }

    const accessTokenOptions: SignOptions = {
      expiresIn: this.JWT_EXPIRES_IN,
    };

    const refreshTokenOptions: SignOptions = {
      expiresIn,
    };

    const accessToken = jwt.sign({ userId }, jwtSecret, accessTokenOptions);
    const refreshToken = jwt.sign({ userId }, jwtSecret, refreshTokenOptions);

    return { accessToken, refreshToken };
  }

  private static async createSession(
    userId: string,
    refreshToken: string,
    ipAddress?: string,
    userAgent?: string
  ) {
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 30); // 30 days

    return prisma.session.create({
      data: {
        userId,
        token: refreshToken,
        expiresAt,
        ipAddress,
        userAgent,
      },
    });
  }
}
