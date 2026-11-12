import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Boxes, Search } from "lucide-react";
import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";

export function ComponentsPage() {
  const { currentWorkspace } = useWorkspace();
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["components", currentWorkspace?.id, search],
    queryFn: () => {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      return api.get<any>(`/workspaces/${currentWorkspace!.id}/sbom/components?${params}`);
    },
    enabled: Boolean(currentWorkspace),
  });

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Components</h1>
        <p className="mt-1 text-sm text-muted">All software components extracted from SBOMs.</p>
      </div>

      <div className="relative max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
        <Input
          placeholder="Search components..."
          className="pl-9"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={Boxes}
          title="No components found"
          description={search ? "No components match your search." : "Import an SBOM to see components."}
        />
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-background-secondary text-left text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Version</th>
                <th className="px-4 py-3 font-medium">Ecosystem</th>
                <th className="px-4 py-3 font-medium">PURL</th>
                <th className="px-4 py-3 font-medium">License</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((item: any) => (
                <tr key={item.id} className="hover:bg-background-secondary">
                  <td className="px-4 py-3 font-medium text-foreground">{item.name}</td>
                  <td className="px-4 py-3 text-muted">{item.version || "-"}</td>
                  <td className="px-4 py-3 text-muted capitalize">{item.ecosystem || "-"}</td>
                  <td className="max-w-[200px] truncate px-4 py-3 text-muted" title={item.purl}>{item.purl || "-"}</td>
                  <td className="px-4 py-3 text-muted">{item.license || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
