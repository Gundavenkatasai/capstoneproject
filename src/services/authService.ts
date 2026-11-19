import { User, UserRole } from "@/types";
import { MOCK_USERS } from "@/mocks/mockData";
import { mockDelay, USE_MOCK, apiClient } from "./apiClient";

export interface LoginCredentials {
  email: string;
  role?: UserRole;
  password?: string;
  rememberMe?: boolean;
}

export const authService = {
  async login(creds: LoginCredentials): Promise<{ user: User; token: string }> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.post<{ user: User; token: string }>("/auth/login", creds);
        return res.data;
      } catch (err) {
        console.warn("Auth request failed, using mock auth:", err);
      }
    }

    // Find mock user by role or email
    let user = MOCK_USERS.find((u) => u.email.toLowerCase() === creds.email.toLowerCase());
    if (!user && creds.role) {
      user = MOCK_USERS.find((u) => u.role === creds.role);
    }
    if (!user) {
      user = MOCK_USERS[0]; // fallback to citizen
    }

    const token = `civicmind_jwt_${user.id}_${Date.now()}`;
    if (typeof window !== "undefined") {
      localStorage.setItem("civicmind_auth_token", token);
      localStorage.setItem("civicmind_user", JSON.stringify(user));
    }

    return mockDelay({ user, token }, 300);
  },

  async register(data: { name: string; email: string; phone?: string; role: UserRole }): Promise<{ user: User; token: string }> {
    const newUser: User = {
      id: `usr_${Date.now()}`,
      name: data.name,
      email: data.email,
      phone: data.phone || "+91 98000 00000",
      role: data.role,
      ward: "Ward 14 (Central)",
    };

    const token = `civicmind_jwt_${newUser.id}_${Date.now()}`;
    if (typeof window !== "undefined") {
      localStorage.setItem("civicmind_auth_token", token);
      localStorage.setItem("civicmind_user", JSON.stringify(newUser));
    }

    return mockDelay({ user: newUser, token }, 300);
  },

  async getCurrentUser(): Promise<User | null> {
    if (typeof window === "undefined") return null;
    const stored = localStorage.getItem("civicmind_user");
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        return null;
      }
    }
    // Default to admin for full exploration if not logged in
    return MOCK_USERS[2]; // Dr. Sunita Rao, IAS
  },

  logout(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("civicmind_auth_token");
      localStorage.removeItem("civicmind_user");
    }
  },
};
