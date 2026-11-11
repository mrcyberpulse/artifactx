import { Routes, Route, Navigate } from "react-router-dom";

import { WorkspaceProvider } from "@/features/workspace/WorkspaceContext";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { ComingSoon } from "@/components/ComingSoon";

import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { OverviewPage } from "@/pages/OverviewPage";
import { ProjectsPage } from "@/pages/projects/ProjectsPage";
import { ProjectDetailPage } from "@/pages/projects/ProjectDetailPage";
import { AuditLogsPage } from "@/pages/AuditLogsPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { AboutPage } from "@/pages/AboutPage";
import { NoWorkspacePage } from "@/pages/NoWorkspacePage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route
          element={
            <WorkspaceProvider>
              <AppLayout />
            </WorkspaceProvider>
          }
        >
          <Route path="/" element={<OverviewPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="/sbom-inventory" element={<ComingSoon title="SBOM Inventory" />} />
          <Route path="/components" element={<ComingSoon title="Components" />} />
          <Route path="/vulnerabilities" element={<ComingSoon title="Vulnerability Intelligence" />} />
          <Route path="/risk-analytics" element={<ComingSoon title="Risk Analytics" />} />
          <Route path="/dependency-graph" element={<ComingSoon title="Dependency Graph" />} />
          <Route path="/license-intelligence" element={<ComingSoon title="License Intelligence" />} />
          <Route path="/remediation" element={<ComingSoon title="Remediation Center" />} />
          <Route path="/reports" element={<ComingSoon title="Reports" />} />
          <Route path="/notifications" element={<ComingSoon title="Notifications" />} />
          <Route path="/audit-logs" element={<AuditLogsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/no-workspace" element={<NoWorkspacePage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
