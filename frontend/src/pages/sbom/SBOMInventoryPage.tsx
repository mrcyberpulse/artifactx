import { useQuery } from "@tanstack/react-query";
import { FileStack, Upload } from "lucide-react";
import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { formatDateTime } from "@/lib/utils";

export function SBOMInventoryPage() {
  const { currentWorkspace } = useWorkspace();
  
  const { data, isLoading } = useQuery({
    queryKey: ["sbom-imports", currentWorkspace?.id],
    queryFn: () => api.get<any>(`/workspaces/${currentWorkspace!.id}/sbom/imports`),
    enabled: Boolean(currentWorkspace),
  });

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">SBOM Inventory</h1>
          <p className="mt-1 text-sm text-muted">Manage SBOM documents imported into {currentWorkspace.name}.</p>
        </div>
        <Button disabled>
          <Upload className="h-4 w-4" /> Upload SBOM (Coming Soon)
        </Button>
      </div>

      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={FileStack}
          title="No SBOMs imported yet"
          description="Upload a CycloneDX or SPDX SBOM file to see it here."
        />
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-background-secondary text-left text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">File Name</th>
                <th className="px-4 py-3 font-medium">Format</th>
                <th className="px-4 py-3 font-medium">Components</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((item: any) => (
                <tr key={item.id} className="hover:bg-background-secondary">
                  <td className="px-4 py-3 font-medium text-foreground">{item.source_filename}</td>
                  <td className="px-4 py-3 text-muted">{item.detected_format || "Unknown"}</td>
                  <td className="px-4 py-3 text-muted">{item.component_count}</td>
                  <td className="px-4 py-3">
                    <span className="status-badge bg-success/15 text-success">{item.status}</span>
                  </td>
                  <td className="px-4 py-3 text-muted">{formatDateTime(item.started_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
