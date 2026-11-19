"use client";

import React, { useEffect } from "react";
import { CitizenLayout } from "@/components/layout/CitizenLayout";
import { useAuthStore } from "@/stores/authStore";

export default function CitizenRootLayout({ children }: { children: React.ReactNode }) {
  const { role, switchRole } = useAuthStore();

  useEffect(() => {
    if (role !== "citizen") {
      switchRole("citizen");
    }
  }, [role, switchRole]);

  return <CitizenLayout>{children}</CitizenLayout>;
}
