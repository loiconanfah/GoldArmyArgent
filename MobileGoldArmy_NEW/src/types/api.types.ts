/**
 * API Types
 * Type definitions for all API requests and responses
 */

export type ApiResponse<T> = {
  data: T;
  message: string;
  success: boolean;
};

export type ApiError = {
  message: string;
  statusCode: number;
  errors?: Record<string, string[]>;
};

export type PaginatedResponse<T> = {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
};

// Auth Types
export type User = {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type LoginResponse = {
  user: User;
  accessToken: string;
  refreshToken: string;
};

export type RegisterRequest = {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
};

export type RegisterResponse = {
  user: User;
  accessToken: string;
  refreshToken: string;
};

export type RefreshTokenRequest = {
  refreshToken: string;
};

export type RefreshTokenResponse = {
  accessToken: string;
  refreshToken: string;
};

export type ForgotPasswordRequest = {
  email: string;
};

export type ResetPasswordRequest = {
  token: string;
  password: string;
};
