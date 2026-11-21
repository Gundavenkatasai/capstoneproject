import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { OfficerLayout } from "./OfficerLayout";
import { useAuthStore } from "@/stores/authStore";

export function OfficerRootLayout() {
  const { role, switchRole } = useAuthStore();

  useEffect(() => {
    if (role !== "officer") {
      switchRole("officer");
    }
  }, [role, switchRole]);

  return (
    <OfficerLayout>
      <Outlet />
    </OfficerLayout>
  );
}
