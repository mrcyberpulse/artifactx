import { useQuery } from "@tanstack/react-query";
import { ScrollText } from "lucide-react";
import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { EmptyState } from "@/components/ui/EmptyState";

export function LicensePage() {
  const { currentWorkspace } = useWorkspace();
  const { data, isLoading } = useQuery({
    queryKey: ["licenses", currentWorkspace?.id],
    queryFn: () => api.get<any>(`/workspaces/${currentWorkspace!.id}/analytics/licenses`),
    enabled: Boolean(currentWorkspace),
  });

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">License Intelligence</h1>
        <p className="mt-1 text-sm text-muted">Open-source license distribution across your components.</p>
      </div>

      {isLoading ? (
        <div className="p-8 text-center">Loading...</div>
      ) : !data || data.total === 0 ? (
        <EmptyState icon={ScrollText} title="No license data" description="Import an SBOM to analyze licenses." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-sm font-medium text-foreground mb-4">License Distribution</h2>
            <div className="space-y-3">
              {data.licenses.map((lic: any) => (
                <div key={lic.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted">{lic.name}</span>
                    <span className="text-foreground">{lic.count} ({lic.percentage}%)</span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <div className="bg-primary h-2 rounded-full" style={{ width: `${lic.percentage}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
