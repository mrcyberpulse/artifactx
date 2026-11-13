import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { GitBranch } from "lucide-react";
import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { EmptyState } from "@/components/ui/EmptyState";

export function DependencyGraphPage() {
  const { currentWorkspace } = useWorkspace();
  
  // Note: We are fetching for the first project. In a real app, you'd have a project selector.
  const { data: projects } = useQuery({
    queryKey: ["projects", currentWorkspace?.id],
    queryFn: () => api.get<any>(`/workspaces/${currentWorkspace!.id}/projects`),
    enabled: Boolean(currentWorkspace),
  });

  const projectId = projects?.items?.[0]?.id;

  const { data, isLoading } = useQuery({
    queryKey: ["dep-graph", currentWorkspace?.id, projectId],
    queryFn: () => api.get<any>(`/workspaces/${currentWorkspace!.id}/sbom/graph?project_id=${projectId}`),
    enabled: Boolean(currentWorkspace && projectId),
  });

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Dependency Graph</h1>
        <p className="mt-1 text-sm text-muted">Visualize relationships between your components.</p>
      </div>

      {isLoading ? (
        <div className="p-8 text-center">Loading...</div>
      ) : !data || data.nodes.length === 0 ? (
        <EmptyState icon={GitBranch} title="No dependencies found" description="Upload an SBOM with dependency data to see the graph." />
      ) : (
        <div className="card min-h-[500px] flex flex-col items-center justify-center bg-[#0d0d12] border border-border rounded-lg p-8 overflow-auto">
          <div className="text-center mb-8 text-muted text-sm">
            Showing dependencies for project: <span className="text-accent">{projects.items[0].name}</span>
          </div>
          {/* Simple visual representation of nodes and edges */}
          <div className="flex flex-col gap-4 items-center">
            {data.nodes.slice(0, 10).map((node: any) => (
              <div key={node.id} className="flex flex-col items-center">
                <div className="px-4 py-2 bg-primary/20 border border-primary text-primary rounded-md font-mono text-sm shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                  {node.label}
                </div>
                {/* Find outgoing edges for this node */}
                {data.edges.filter((e: any) => e.source === node.id).map((edge: any, i: number) => (
                  <div key={i} className="flex flex-col items-center">
                    <div className="w-px h-6 bg-border" />
                    <div className="text-xs text-muted mb-2">depends on ↓</div>
                    <div className="px-3 py-1.5 bg-background border border-border rounded text-xs text-foreground">
                      {edge.target}
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
