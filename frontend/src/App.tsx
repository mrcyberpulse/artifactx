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
import { SBOMInventoryPage } from "@/pages/sbom/SBOMInventoryPage";
import { ComponentsPage } from "@/pages/components/ComponentsPage";
import { VulnerabilityPage } from "@/pages/VulnerabilityPage";
import { RemediationPage } from "@/pages/RemediationPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { LicensePage } from "@/pages/LicensePage";
import { RiskAnalyticsPage } from "@/pages/RiskAnalyticsPage";
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<WorkspaceProvider><AppLayout /></WorkspaceProvider>}>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="/sbom-inventory" element={<SBOMInventoryPage />} />
          <Route path="/components" element={<ComponentsPage />} />
          <Route path="/vulnerabilities" element={<VulnerabilityPage />} />
          <Route path="/remediation" element={<RemediationPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/risk-analytics" element={<ComingSoon title="Risk Analytics" />} />
          <Route path="/dependency-graph" element={<ComingSoon title="Dependency Graph" />} />
          <Route path="/license-intelligence" element={<ComingSoon title="License Intelligence" />} />
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
