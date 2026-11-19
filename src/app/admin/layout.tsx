"use client";

import React, { useEffect } from "react";
import { AdminLayout } from "@/components/layout/AdminLayout";
import { useAuthStore } from "@/stores/authStore";

export default function AdminRootLayout({ children }: { children: React.ReactNode }) {
  const { role, switchRole } = useAuthStore();

  useEffect(() => {
    if (role !== "admin") {
      switchRole("admin");
    }
  }, [role, switchRole]);

  return <AdminLayout>{children}</AdminLayout>;
}
