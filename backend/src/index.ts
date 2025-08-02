import "dotenv/config";
import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import authRoutes from "@/routes/auth";
import userRoutes from "@/routes/users";

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan("combined"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API v1 routes
app.get("/api/v1/health", (_req, res) => {
  res.status(200).json({
    status: "healthy",
    service: "fantasy-football-api",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// // Authentication routes
app.use("/api/v1/auth", authRoutes);

// User routes
app.use("/api/v1/users", userRoutes);

// 404 handler
app.use("*", (_req, res) => {
  res.status(404).json({
    error: {
      code: "NOT_FOUND",
      message: "The requested resource was not found",
    },
  });
});

// Error handler
app.use(
  (
    err: Error,
    _req: express.Request,
    res: express.Response,
    _next: express.NextFunction
  ) => {
    console.error("Error:", err);
    res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "An internal server error occurred",
      },
    });
  }
);

// Start server
const server = app.listen(PORT, () => {
  console.log(`🚀 Fantasy Football API server running on port ${PORT}`);
  console.log(`📊 Health check available at http://localhost:${PORT}/health`);
  console.log(`🔗 API v1 available at http://localhost:${PORT}/api/v1`);
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("🔄 SIGTERM received, shutting down gracefully");
  server.close(() => {
    console.log("✅ Process terminated");
  });
});

process.on("SIGINT", () => {
  console.log("🔄 SIGINT received, shutting down gracefully");
  server.close(() => {
    console.log("✅ Process terminated");
  });
});

export default app;
