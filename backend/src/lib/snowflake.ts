import snowflake from "snowflake-sdk";

interface SnowflakeConfig {
  account: string;
  username: string;
  password: string;
  database: string;
  warehouse: string;
  schema?: string;
  role?: string;
}

class SnowflakeClient {
  private connection: snowflake.Connection | null = null;
  private config: SnowflakeConfig;

  constructor() {
    this.config = {
      account: process.env.SNOWFLAKE_ACCOUNT || "",
      username: process.env.SNOWFLAKE_USER || "",
      password: process.env.SNOWFLAKE_PASSWORD || "",
      database: process.env.SNOWFLAKE_DATABASE || "",
      warehouse: process.env.SNOWFLAKE_WAREHOUSE || "",
      schema: process.env.SNOWFLAKE_SCHEMA || "PUBLIC",
      role: process.env.SNOWFLAKE_ROLE,
    };
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.connection = snowflake.createConnection(this.config);

      this.connection.connect((err, conn) => {
        if (err) {
          console.error("Unable to connect to Snowflake:", err.message);
          reject(err);
        } else {
          console.log("Successfully connected to Snowflake");
          resolve();
        }
      });
    });
  }

  async execute<T = any>(sqlText: string, binds?: any[]): Promise<T[]> {
    if (!this.connection) {
      await this.connect();
    }

    return new Promise((resolve, reject) => {
      this.connection!.execute({
        sqlText,
        binds,
        complete: (err, stmt, rows) => {
          if (err) {
            console.error("Failed to execute statement:", err.message);
            reject(err);
          } else {
            resolve(rows as T[]);
          }
        },
      });
    });
  }

  async destroy(): Promise<void> {
    if (!this.connection) {
      return;
    }

    return new Promise((resolve, reject) => {
      this.connection!.destroy((err) => {
        if (err) {
          console.error("Unable to disconnect from Snowflake:", err.message);
          reject(err);
        } else {
          console.log("Disconnected from Snowflake");
          this.connection = null;
          resolve();
        }
      });
    });
  }
}

export const snowflakeClient = new SnowflakeClient();
