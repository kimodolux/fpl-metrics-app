import { Router } from "express";
import { AuthService } from "@/services/auth";
import {
  registerSchema,
  loginSchema,
  refreshTokenSchema,
} from "@/schemas/auth";
import { AuthRequest, authenticateToken } from "@/middleware/auth";
import { ZodError, ZodIssue } from "zod";

const router = Router();

// POST /api/v1/auth/register
router.post("/register", async (req, res) => {
  try {
    const validatedData = registerSchema.parse(req.body);

    const result = await AuthService.register(validatedData);

    res.status(201).json(result);
  } catch (error) {
    if (error instanceof Error) {
      switch (error.message) {
        case "EMAIL_EXISTS":
          return res.status(400).json({
            error: {
              code: "VALIDATION_ERROR",
              message: "Email already exists",
              details: [
                { field: "email", message: "This email is already registered" },
              ],
            },
          });
        case "USERNAME_EXISTS":
          return res.status(400).json({
            error: {
              code: "VALIDATION_ERROR",
              message: "Username already exists",
              details: [
                {
                  field: "username",
                  message: "This username is already taken",
                },
              ],
            },
          });
      }
    }

    // Handle Zod validation errors
    if (error instanceof ZodError) {
      const zodError = error;
      return res.status(400).json({
        error: {
          code: "VALIDATION_ERROR",
          message: "Invalid request data",
          details: zodError.errors.map((err: ZodIssue) => ({
            field: err.path.join("."),
            message: err.message,
          })),
        },
      });
    }

    console.error("Registration error:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Registration failed",
      },
    });
  }
});

// POST /api/v1/auth/login
router.post("/login", async (req, res) => {
  try {
    const validatedData = loginSchema.parse(req.body);
    const ipAddress = req.ip;
    const userAgent = req.get("User-Agent");

    const result = await AuthService.login(validatedData, ipAddress, userAgent);

    res.status(200).json(result);
  } catch (error) {
    if (error instanceof Error) {
      switch (error.message) {
        case "INVALID_CREDENTIALS":
          return res.status(401).json({
            error: {
              code: "AUTHENTICATION_ERROR",
              message: "Invalid email or password",
            },
          });
        case "OAUTH_USER":
          return res.status(400).json({
            error: {
              code: "AUTHENTICATION_ERROR",
              message: "Please use OAuth to sign in",
            },
          });
      }
    }

    // Handle Zod validation errors
    if (error instanceof ZodError) {
      const zodError = error;
      return res.status(400).json({
        error: {
          code: "VALIDATION_ERROR",
          message: "Invalid request data",
          details: zodError.errors.map((err: ZodIssue) => ({
            field: err.path.join("."),
            message: err.message,
          })),
        },
      });
    }

    console.error("Login error:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Login failed",
      },
    });
  }
});

// POST /api/v1/auth/refresh
router.post("/refresh", async (req, res) => {
  try {
    const validatedData = refreshTokenSchema.parse(req.body);

    const result = await AuthService.refreshToken(validatedData.refreshToken);

    res.status(200).json(result);
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_REFRESH_TOKEN") {
      return res.status(401).json({
        error: {
          code: "AUTHENTICATION_ERROR",
          message: "Invalid or expired refresh token",
        },
      });
    }

    // Handle Zod validation errors
    if (error instanceof ZodError) {
      const zodError = error;
      return res.status(400).json({
        error: {
          code: "VALIDATION_ERROR",
          message: "Invalid request data",
          details: zodError.errors.map((err: ZodIssue) => ({
            field: err.path.join("."),
            message: err.message,
          })),
        },
      });
    }

    console.error("Refresh token error:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Token refresh failed",
      },
    });
  }
});

// POST /api/v1/auth/logout
router.post("/logout", authenticateToken, async (req: AuthRequest, res) => {
  try {
    const refreshToken = req.body.refreshToken;

    if (refreshToken) {
      await AuthService.logout(refreshToken);
    }

    res.status(200).json({
      message: "Logged out successfully",
    });
  } catch (error) {
    console.error("Logout error:", error);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Logout failed",
      },
    });
  }
});

export default router;
