export type User = {
  id: string;
  email: string;
  managerId: string;
  createdAt: string;
  teamCount?: number;
}

export type AuthResponse = {
  user: User;
  accessToken: string;
  refreshToken?: string;
  expiresIn: number;
}

export type LoginCredentials = {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export type RegisterCredentials = {
  email: string;
  managerId: string;
  password: string;
}

export type ApiError = {
  error: {
    code: string;
    message: string;
    details?: Array<{
      field: string;
      message: string;
    }>;
  };
}