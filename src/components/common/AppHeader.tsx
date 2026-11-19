"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { NotificationCenter } from "./NotificationCenter";
import { CommandPalette } from "./CommandPalette";
import {
  Search,
  Plus,
  LogOut,
  User,
  Shield,
  HelpCircle,
  Menu,
  ChevronDown,
} from "lucide-react";

interface AppHeaderProps {
  onToggleSidebar?: () => void;
}

export function AppHeader({ onToggleSidebar }: AppHeaderProps) {
  const router = useRouter();
  const { user, role, logout } = useAuthStore();
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="h-14 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <CommandPalette />

      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 rounded-md text-slate-500 hover:text-slate-800 hover:bg-slate-100 lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Global Search Bar (clicking opens Command Palette) */}
        <button
          onClick={() => {
            const event = new KeyboardEvent("keydown", { key: "k", metaKey: true });
            window.dispatchEvent(event);
          }}
          className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded bg-slate-50 border border-slate-200/80 text-xs text-slate-400 hover:border-slate-300 hover:bg-slate-100/70 transition-all w-64 md:w-80 text-left shadow-subtle"
        >
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <span className="truncate">Search intelligence, grievances, wards...</span>
          <kbd className="ml-auto px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-white border border-slate-200 rounded">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2.5">
        {/* Quick action button */}
        {role === "citizen" && (
          <Link
            href="/citizen/submit"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-subtle transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            File Grievance
          </Link>
        )}

        {role === "admin" && (
          <Link
            href="/admin/simulator"
            className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
          >
            Run Workload Sim
          </Link>
        )}

        {/* Notification Bell */}
        <NotificationCenter />

        {/* Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 p-1 rounded-md hover:bg-slate-100 transition-colors"
          >
            <div className="w-7 h-7 rounded-full bg-slate-200 border border-slate-300 overflow-hidden flex items-center justify-center text-xs font-bold text-slate-700">
              {user?.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
              ) : (
                user?.name?.charAt(0) || "U"
              )}
            </div>
            <span className="hidden md:inline-block text-xs font-semibold text-slate-800 max-w-[120px] truncate">
              {user?.name}
            </span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {profileOpen && (
            <>
              <div className="fixed inset-0 z-30" onClick={() => setProfileOpen(false)} />
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-dropdown border border-slate-200 z-40 py-1.5 text-xs">
                <div className="px-3.5 py-2 border-b border-slate-100">
                  <p className="font-semibold text-slate-900 truncate">{user?.name}</p>
                  <p className="text-[11px] text-slate-500 font-mono truncate">{user?.email}</p>
                  <span className="mt-1 inline-block text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 border border-slate-200">
                    Role: {role}
                  </span>
                </div>

                <Link
                  href={role === "admin" ? "/admin/settings" : `/${role}/profile`}
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-2 px-3.5 py-2 text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  <User className="w-3.5 h-3.5 text-slate-400" />
                  Account Profile
                </Link>

                <Link
                  href="/"
                  onClick={() => setProfileOpen(false)}
                  className="flex items-center gap-2 px-3.5 py-2 text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                  Public Portal & Info
                </Link>

                <div className="border-t border-slate-100 my-1" />

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-3.5 py-2 text-red-600 hover:bg-red-50 transition-colors text-left font-medium"
                >
                  <LogOut className="w-3.5 h-3.5 text-red-500" />
                  Sign Out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
