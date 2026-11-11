import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Plus, Search, FolderKanban } from "lucide-react";

import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Dialog, DialogTrigger } from "@/components/ui/Dialog";
import { formatDate } from "@/lib/utils";
import type { Page, Project, Environment, Criticality } from "@/types/api";
import { CreateProjectDialog } from "@/pages/projects/CreateProjectDialog";

const CRITICALITY_TONE: Record<Criticality, "neutral" | "warning" | "danger" | "info"> = {
  low: "neutral",
  medium: "info",
  high: "warning",
  critical: "danger",
};

export function ProjectsPage() {
  const { currentWorkspace } = useWorkspace();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [environment, setEnvironment] = useState<Environment | "">("");
  const [page, setPage] = useState(1);
  const [createOpen, setCreateOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["projects", currentWorkspace?.id, search, environment, page],
    queryFn: () => {
      const params = new URLSearchParams({ page: String(page), page_size: "20" });
      if (search) params.set("search", search);
      if (environment) params.set("environment", environment);
      return api.get<Page<Project>>(`/workspaces/${currentWorkspace!.id}/projects?${params}`);
    },
    enabled: Boolean(currentWorkspace),
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["projects"] });

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Projects</h1>
          <p className="mt-1 text-sm text-muted">Manage the projects tracked in {currentWorkspace.name}.</p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4" /> New project
            </Button>
          </DialogTrigger>
          <CreateProjectDialog
            workspaceId={currentWorkspace.id}
            onCreated={() => {
              setCreateOpen(false);
              invalidate();
            }}
          />
        </Dialog>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative max-w-sm flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <Input
            placeholder="Search projects..."
            className="pl-9"
            value={search}
            onChange={(e) => {
              setPage(1);
              setSearch(e.target.value);
            }}
          />
        </div>
        <select
          value={environment}
          onChange={(e) => {
            setPage(1);
            setEnvironment(e.target.value as Environment | "");
          }}
          className="input-field max-w-[180px]"
        >
          <option value="">All environments</option>
          <option value="development">Development</option>
          <option value="staging">Staging</option>
          <option value="production">Production</option>
        </select>
      </div>

      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="No projects found"
          description={
            search || environment
              ? "No projects match your current filters."
              : "Create your first project to start tracking its software supply chain."
          }
          action={
            !search && !environment ? (
              <Button onClick={() => setCreateOpen(true)}>
                <Plus className="h-4 w-4" /> New project
              </Button>
            ) : undefined
          }
        />
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-background-secondary text-left text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Environment</th>
                <th className="px-4 py-3 font-medium">Criticality</th>
                <th className="px-4 py-3 font-medium">Repository</th>
                <th className="px-4 py-3 font-medium">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.items.map((project) => (
                <tr
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="cursor-pointer hover:bg-background-secondary"
                >
                  <td className="px-4 py-3 font-medium text-foreground">{project.name}</td>
                  <td className="px-4 py-3 text-muted capitalize">{project.environment}</td>
                  <td className="px-4 py-3">
                    <Badge tone={CRITICALITY_TONE[project.business_criticality]}>
                      {project.business_criticality}
                    </Badge>
                  </td>
                  <td className="max-w-[220px] truncate px-4 py-3 text-muted">
                    {project.repository_url ?? "\u2014"}
                  </td>
                  <td className="px-4 py-3 text-muted">{formatDate(project.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && data.pages > 1 && (
        <div className="flex items-center justify-between text-sm text-muted">
          <span>
            Page {data.page} of {data.pages} ({data.total} total)
          </span>
          <div className="flex gap-2">
            <Button variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </Button>
            <Button variant="secondary" disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)}>
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
