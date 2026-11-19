"use client";

import React, { useEffect } from "react";
import { OfficerLayout } from "@/components/layout/OfficerLayout";
import { useAuthStore } from "@/stores/authStore";

export default function OfficerRootLayout({ children }: { children: React.ReactNode }) {
  const { role, switchRole } = useAuthStore();

  useEffect(() => {
    if (role !== "officer") {
      switchRole("officer");
    }
  }, [role, switchRole]);

  return <OfficerLayout>{children}</OfficerLayout>;
}
