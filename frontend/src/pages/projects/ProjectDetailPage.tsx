import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Trash2 } from "lucide-react";

import { api, ApiError } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/Dialog";
import { projectSchema, type ProjectFormValues } from "@/lib/validation";
import { formatDateTime } from "@/lib/utils";
import type { Project } from "@/types/api";

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentWorkspace } = useWorkspace();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", currentWorkspace?.id, projectId],
    queryFn: () => api.get<Project>(`/workspaces/${currentWorkspace!.id}/projects/${projectId}`),
    enabled: Boolean(currentWorkspace && projectId),
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    values: project
      ? {
          name: project.name,
          description: project.description ?? "",
          repository_url: project.repository_url ?? "",
          environment: project.environment,
          business_criticality: project.business_criticality,
        }
      : undefined,
  });

  const onSubmit = async (values: ProjectFormValues) => {
    if (!currentWorkspace || !projectId) return;
    setServerError(null);
    try {
      const updated = await api.patch<Project>(
        `/workspaces/${currentWorkspace.id}/projects/${projectId}`,
        {
          ...values,
          repository_url: values.repository_url || null,
          description: values.description || null,
        },
      );
      queryClient.setQueryData(["project", currentWorkspace.id, projectId], updated);
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      reset(values);
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Unable to save changes.");
    }
  };

  const handleDelete = async () => {
    if (!currentWorkspace || !projectId) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await api.delete(`/workspaces/${currentWorkspace.id}/projects/${projectId}`);
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      navigate("/projects", { replace: true });
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Unable to delete project.");
      setIsDeleting(false);
    }
  };

  if (isLoading || !project) {
    return (
      <div className="flex h-64 items-center justify-center">
        <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <button
        onClick={() => navigate("/projects")}
        className="flex items-center gap-1.5 text-sm text-muted hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> Back to projects
      </button>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">{project.name}</h1>
          <p className="mt-1 text-xs text-muted">
            Created {formatDateTime(project.created_at)} &middot; Updated {formatDateTime(project.updated_at)}
          </p>
        </div>
        <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <DialogTrigger asChild>
            <Button variant="danger">
              <Trash2 className="h-4 w-4" /> Delete
            </Button>
          </DialogTrigger>
          <DialogContent
            title="Delete this project?"
            description="This cannot be undone. The project and its metadata will be permanently removed from this workspace."
          >
            {deleteError && <p className="mb-3 text-sm text-danger">{deleteError}</p>}
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setDeleteOpen(false)} disabled={isDeleting}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDelete} isLoading={isDeleting}>
                Delete project
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
          <div>
            <Label htmlFor="name">Project name</Label>
            <Input id="name" {...register("name")} />
            {errors.name && <p className="mt-1 text-xs text-danger">{errors.name.message}</p>}
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Input id="description" {...register("description")} />
          </div>
          <div>
            <Label htmlFor="repository_url">Repository URL</Label>
            <Input id="repository_url" {...register("repository_url")} />
            {errors.repository_url && (
              <p className="mt-1 text-xs text-danger">{errors.repository_url.message}</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="environment">Environment</Label>
              <select id="environment" className="input-field" {...register("environment")}>
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
              </select>
            </div>
            <div>
              <Label htmlFor="business_criticality">Criticality</Label>
              <select id="business_criticality" className="input-field" {...register("business_criticality")}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>
          {serverError && <p className="text-sm text-danger" role="alert">{serverError}</p>}
          <div className="flex justify-end">
            <Button type="submit" isLoading={isSubmitting} disabled={!isDirty}>
              Save changes
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
