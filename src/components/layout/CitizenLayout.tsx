"use client";

import React, { useState } from "react";
import { AppSidebar } from "@/components/common/AppSidebar";
import { AppHeader } from "@/components/common/AppHeader";

export function CitizenLayout({ children }: { children: React.ReactNode }) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <AppSidebar className="hidden lg:flex" />

      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <AppSidebar className="relative z-50 flex" />
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <AppHeader onToggleSidebar={() => setMobileSidebarOpen(!mobileSidebarOpen)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto animate-in fade-in duration-150">
          {children}
        </main>
      </div>
    </div>
  );
}
