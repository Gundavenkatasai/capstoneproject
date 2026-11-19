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

  async googleLogin(payload: { id_token?: string; credential?: string; code?: string; redirect_uri?: string }): Promise<{ user: User; token: string }> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.post<{ user: User; token: string }>("/auth/google", payload);
        if (typeof window !== "undefined") {
          localStorage.setItem("civicmind_auth_token", res.data.token);
          localStorage.setItem("civicmind_user", JSON.stringify(res.data.user));
        }
        return res.data;
      } catch (err: any) {
        console.warn("Google auth API request failed, falling back to mock Google user:", err);
      }
    }

    // Mock Google citizen profile fallback for testing/offline mode
    const googleUser: User = {
      id: `usr_google_${Date.now()}`,
      name: "Google Authenticated Citizen",
      email: "citizen.google@gmail.com",
      role: "citizen",
      ward: "Ward 12 (Indiranagar)",
      avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
    };

    const token = `civicmind_google_jwt_${googleUser.id}_${Date.now()}`;
    if (typeof window !== "undefined") {
      localStorage.setItem("civicmind_auth_token", token);
      localStorage.setItem("civicmind_user", JSON.stringify(googleUser));
    }

    return mockDelay({ user: googleUser, token }, 300);
  },

  async getGoogleAuthUrl(redirect_uri?: string): Promise<{ auth_url: string; client_id: string }> {
    if (!USE_MOCK) {
      try {
        const res = await apiClient.get<{ auth_url: string; client_id: string }>("/auth/google/url", {
          params: { redirect_uri },
        });
        return res.data;
      } catch (err) {
        console.warn("Failed to fetch Google auth URL from API:", err);
      }
    }
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";
    const redirect = redirect_uri || (typeof window !== "undefined" ? `${window.location.origin}/auth/callback/google` : "http://localhost:3000/auth/callback/google");
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirect)}&response_type=code&scope=openid%20email%20profile&access_type=offline&prompt=select_account`;
    return { auth_url: authUrl, client_id: clientId };
  },

  logout(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("civicmind_auth_token");
      localStorage.removeItem("civicmind_user");
    }
  },
};
