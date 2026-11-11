import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import {
  FolderKanban,
  FileStack,
  Boxes,
  ShieldAlert,
  AlertTriangle,
  Flame,
  PackageX,
  Wrench,
} from "lucide-react";

import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { MetricCardView } from "@/components/ui/MetricCard";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import type { DashboardSummary } from "@/types/api";

export function OverviewPage() {
  const { currentWorkspace, isLoading: workspacesLoading, workspaces } = useWorkspace();

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-summary", currentWorkspace?.id],
    queryFn: () => api.get<DashboardSummary>(`/workspaces/${currentWorkspace!.id}/dashboard/summary`),
    enabled: Boolean(currentWorkspace),
  });

  if (!workspacesLoading && workspaces.length === 0) {
    return <Navigate to="/no-workspace" replace />;
  }

  if (workspacesLoading || isLoading || !data) {
    return (
      <div className="flex h-64 items-center justify-center">
        <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Overview</h1>
        <p className="mt-1 text-sm text-muted">{currentWorkspace?.name}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCardView label="Total Projects" icon={FolderKanban} data={data.total_projects} />
        <MetricCardView label="SBOM Documents" icon={FileStack} data={data.sbom_documents} />
        <MetricCardView label="Components" icon={Boxes} data={data.components} />
        <MetricCardView label="Vulnerability Findings" icon={ShieldAlert} data={data.vulnerability_findings} />
        <MetricCardView label="Critical Findings" icon={Flame} data={data.critical_findings} />
        <MetricCardView label="High-Risk Findings" icon={AlertTriangle} data={data.high_risk_findings} />
        <MetricCardView label="Outdated Components" icon={PackageX} data={data.outdated_components} />
        <MetricCardView label="Remediation Progress" icon={Wrench} data={data.remediation_progress} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Vulnerability Severity</CardTitle>
          </CardHeader>
          <EmptyState
            icon={ShieldAlert}
            title="No vulnerability data yet"
            description="Severity breakdown appears once SBOM scanning and vulnerability intelligence are available in a future release."
          />
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Risk Trends</CardTitle>
          </CardHeader>
          <EmptyState
            icon={AlertTriangle}
            title="No risk data yet"
            description="Risk trend charts appear once the risk engine is available in a future release."
          />
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Components by Ecosystem</CardTitle>
          </CardHeader>
          <EmptyState
            icon={Boxes}
            title="No component data yet"
            description="Import an SBOM in a future release to see components grouped by ecosystem."
          />
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent Project Activity</CardTitle>
          </CardHeader>
          <EmptyState
            icon={FolderKanban}
            title="No activity yet"
            description="Recent project and SBOM activity will appear here."
          />
        </Card>
      </div>
    </div>
  );
}
