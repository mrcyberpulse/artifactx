import { useQuery } from "@tanstack/react-query";
import { LineChart } from "lucide-react";
import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";

export function RiskAnalyticsPage() {
  const { currentWorkspace } = useWorkspace();
  const { data, isLoading } = useQuery({
    queryKey: ["risk-dist", currentWorkspace?.id],
    queryFn: () => api.get<any>(`/workspaces/${currentWorkspace!.id}/analytics/risk-distribution`),
    enabled: Boolean(currentWorkspace),
  });

  if (!currentWorkspace) return null;

  const severities = [
    { key: "CRITICAL", color: "bg-danger", label: "Critical" },
    { key: "HIGH", color: "bg-warning", label: "High" },
    { key: "MEDIUM", color: "bg-yellow-500", label: "Medium" },
    { key: "LOW", color: "bg-success", label: "Low" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Risk Analytics</h1>
        <p className="mt-1 text-sm text-muted">Vulnerability severity breakdown across the workspace.</p>
      </div>

      {isLoading ? (
        <div className="p-8 text-center">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-sm font-medium text-foreground mb-6 flex items-center gap-2">
              <LineChart className="h-4 w-4" /> Findings by Severity
            </h2>
            <div className="space-y-4">
              {severities.map((sev) => (
                <div key={sev.key} className="flex items-center gap-4">
                  <span className="w-20 text-sm text-muted">{sev.label}</span>
                  <div className="flex-1 bg-background rounded-full h-4">
                    <div 
                      className={`${sev.color} h-4 rounded-full`} 
                      style={{ width: `${Math.min((data[sev.key] / Math.max(data.CRITICAL + data.HIGH + data.MEDIUM + data.LOW + data.UNKNOWN, 1)) * 100, 100)}%` }} 
                    />
                  </div>
                  <span className="w-8 text-sm font-bold text-foreground text-right">{data[sev.key]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
