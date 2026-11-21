import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { CitizenLayout } from "./CitizenLayout";
import { useAuthStore } from "@/stores/authStore";

export function CitizenRootLayout() {
  const { role, switchRole } = useAuthStore();

  useEffect(() => {
    if (role !== "citizen") {
      switchRole("citizen");
    }
  }, [role, switchRole]);

  return (
    <CitizenLayout>
      <Outlet />
    </CitizenLayout>
  );
}
