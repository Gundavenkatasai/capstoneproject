import { create } from "zustand";
import { User, UserRole } from "@/types";
import { MOCK_USERS } from "@/mocks/mockData";
import { authService, LoginCredentials } from "@/services/authService";

interface AuthState {
  user: User | null;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  switchRole: (role: UserRole) => void;
  login: (creds: LoginCredentials) => Promise<void>;
  logout: () => void;
  initAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: MOCK_USERS[2], // Default to Admin for comprehensive demo
  role: "admin",
  isAuthenticated: true,
  isLoading: false,

  setUser: (user) => {
    if (user) {
      set({ user, role: user.role, isAuthenticated: true });
    } else {
      set({ user: null, role: "citizen", isAuthenticated: false });
    }
  },

  switchRole: (newRole: UserRole) => {
    const targetUser = MOCK_USERS.find((u) => u.role === newRole) || MOCK_USERS[0];
    if (typeof window !== "undefined") {
      localStorage.setItem("civicmind_user", JSON.stringify(targetUser));
    }
    set({ user: targetUser, role: newRole, isAuthenticated: true });
  },

  login: async (creds: LoginCredentials) => {
    set({ isLoading: true });
    try {
      const res = await authService.login(creds);
      set({ user: res.user, role: res.user.role, isAuthenticated: true, isLoading: false });
    } catch (err) {
      set({ isLoading: false });
      throw err;
    }
  },

  logout: () => {
    authService.logout();
    set({ user: null, role: "citizen", isAuthenticated: false });
  },

  initAuth: async () => {
    const user = await authService.getCurrentUser();
    if (user) {
      set({ user, role: user.role, isAuthenticated: true });
    }
  },
}));
