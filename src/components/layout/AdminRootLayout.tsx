import React, { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { AdminLayout } from "./AdminLayout";
import { useAuthStore } from "@/stores/authStore";

export function AdminRootLayout() {
  const { role, switchRole } = useAuthStore();

  useEffect(() => {
    if (role !== "admin") {
      switchRole("admin");
    }
  }, [role, switchRole]);

  return (
    <AdminLayout>
      <Outlet />
    </AdminLayout>
  );
}
