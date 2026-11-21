import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Loader2 } from "lucide-react";

// Layouts
import { AdminRootLayout } from "@/components/layout/AdminRootLayout";
import { CitizenRootLayout } from "@/components/layout/CitizenRootLayout";
import { OfficerRootLayout } from "@/components/layout/OfficerRootLayout";

// Public Pages
import HomePage from "@/pages/HomePage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import ForgotPasswordPage from "@/pages/ForgotPasswordPage";
import NotFoundPage from "@/pages/NotFoundPage";
import GoogleCallbackPage from "@/pages/auth/GoogleCallbackPage";

// Citizen Pages
import CitizenDashboardPage from "@/pages/citizen/CitizenDashboardPage";
import CitizenSubmitPage from "@/pages/citizen/CitizenSubmitPage";
import CitizenGrievancesPage from "@/pages/citizen/CitizenGrievancesPage";
import CitizenGrievanceDetailPage from "@/pages/citizen/CitizenGrievanceDetailPage";
import CitizenAppealsPage from "@/pages/citizen/CitizenAppealsPage";
import CitizenNotificationsPage from "@/pages/citizen/CitizenNotificationsPage";
import CitizenProfilePage from "@/pages/citizen/CitizenProfilePage";

// Officer Pages
import OfficerDashboardPage from "@/pages/officer/OfficerDashboardPage";
import OfficerAssignedPage from "@/pages/officer/OfficerAssignedPage";
import OfficerEscalationsPage from "@/pages/officer/OfficerEscalationsPage";
import OfficerGrievanceActionPage from "@/pages/officer/OfficerGrievanceActionPage";
import OfficerPerformancePage from "@/pages/officer/OfficerPerformancePage";
import OfficerProfilePage from "@/pages/officer/OfficerProfilePage";

// Admin Pages
import AdminDashboardPage from "@/pages/admin/AdminDashboardPage";
import AdminGrievancesPage from "@/pages/admin/AdminGrievancesPage";
import AdminGrievanceDetailPage from "@/pages/admin/AdminGrievanceDetailPage";
import AdminEarlyWarningPage from "@/pages/admin/AdminEarlyWarningPage";
import AdminSimulatorPage from "@/pages/admin/AdminSimulatorPage";
import AdminDuplicatesPage from "@/pages/admin/AdminDuplicatesPage";
import AdminPredictionsPage from "@/pages/admin/AdminPredictionsPage";
import AdminExplainabilityPage from "@/pages/admin/AdminExplainabilityPage";
import AdminModelsPage from "@/pages/admin/AdminModelsPage";
import AdminDatasetsPage from "@/pages/admin/AdminDatasetsPage";
import AdminAuditLogsPage from "@/pages/admin/AdminAuditLogsPage";
import AdminKnowledgeGraphPage from "@/pages/admin/AdminKnowledgeGraphPage";
import AdminResolutionVerificationPage from "@/pages/admin/AdminResolutionVerificationPage";
import AdminWorkloadPage from "@/pages/admin/AdminWorkloadPage";
import AdminSettingsPage from "@/pages/admin/AdminSettingsPage";
import AdminExperimentsPage from "@/pages/admin/AdminExperimentsPage";

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-slate-500">
      <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-3" />
      <span className="text-xs font-medium font-mono">Loading CivicMind AI Workspace...</span>
    </div>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          {/* Public Authentication & Landing Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/auth/callback/google" element={<GoogleCallbackPage />} />

          {/* Citizen Portal Routes */}
          <Route element={<CitizenRootLayout />}>
            <Route path="/citizen" element={<Navigate to="/citizen/dashboard" replace />} />
            <Route path="/citizen/dashboard" element={<CitizenDashboardPage />} />
            <Route path="/citizen/submit" element={<CitizenSubmitPage />} />
            <Route path="/citizen/grievances" element={<CitizenGrievancesPage />} />
            <Route path="/citizen/grievances/:id" element={<CitizenGrievanceDetailPage />} />
            <Route path="/citizen/appeals" element={<CitizenAppealsPage />} />
            <Route path="/citizen/notifications" element={<CitizenNotificationsPage />} />
            <Route path="/citizen/profile" element={<CitizenProfilePage />} />
          </Route>

          {/* Officer Portal Routes */}
          <Route element={<OfficerRootLayout />}>
            <Route path="/officer" element={<Navigate to="/officer/dashboard" replace />} />
            <Route path="/officer/dashboard" element={<OfficerDashboardPage />} />
            <Route path="/officer/assigned" element={<OfficerAssignedPage />} />
            <Route path="/officer/escalations" element={<OfficerEscalationsPage />} />
            <Route path="/officer/grievances/:id" element={<OfficerGrievanceActionPage />} />
            <Route path="/officer/performance" element={<OfficerPerformancePage />} />
            <Route path="/officer/profile" element={<OfficerProfilePage />} />
          </Route>

          {/* Admin Intelligence Command Center Routes */}
          <Route element={<AdminRootLayout />}>
            <Route path="/admin" element={<AdminDashboardPage />} />
            <Route path="/admin/grievances" element={<AdminGrievancesPage />} />
            <Route path="/admin/grievances/:id" element={<AdminGrievanceDetailPage />} />
            <Route path="/admin/early-warning" element={<AdminEarlyWarningPage />} />
            <Route path="/admin/simulator" element={<AdminSimulatorPage />} />
            <Route path="/admin/duplicates" element={<AdminDuplicatesPage />} />
            <Route path="/admin/predictions" element={<AdminPredictionsPage />} />
            <Route path="/admin/explainability" element={<AdminExplainabilityPage />} />
            <Route path="/admin/models" element={<AdminModelsPage />} />
            <Route path="/admin/datasets" element={<AdminDatasetsPage />} />
            <Route path="/admin/audit-logs" element={<AdminAuditLogsPage />} />
            <Route path="/admin/knowledge-graph" element={<AdminKnowledgeGraphPage />} />
            <Route path="/admin/resolution-verification" element={<AdminResolutionVerificationPage />} />
            <Route path="/admin/workload" element={<AdminWorkloadPage />} />
            <Route path="/admin/settings" element={<AdminSettingsPage />} />
            <Route path="/admin/experiments" element={<AdminExperimentsPage />} />
          </Route>

          {/* 404 Catch-All */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
