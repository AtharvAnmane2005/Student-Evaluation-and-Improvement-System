export type UserRole = "student" | "tpo" | "admin";

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
  profile_incomplete?: boolean;
}
