import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Building2 } from "lucide-react";

import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api-client";
import { ApiError } from "@/lib/api-client";
import { workspaceSchema, type WorkspaceFormValues } from "@/lib/validation";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import type { Workspace } from "@/types/api";

export function NoWorkspacePage() {
  const { refetch } = useWorkspace();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<WorkspaceFormValues>({ resolver: zodResolver(workspaceSchema) });

  const onSubmit = async (values: WorkspaceFormValues) => {
    setServerError(null);
    try {
      await api.post<Workspace>("/workspaces", {
        name: values.name,
        description: values.description || null,
      });
      refetch();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Unable to create workspace.");
    }
  };

  return (
    <div className="mx-auto max-w-md pt-16">
      <div className="card">
        <div className="mb-4 flex flex-col items-center text-center">
          <Building2 className="mb-2 h-8 w-8 text-primary" strokeWidth={1.5} />
          <h2 className="text-base font-semibold text-foreground">Create your first workspace</h2>
          <p className="mt-1 text-sm text-muted">
            Workspaces organize your projects, SBOMs, and team members in ArtifactX.
          </p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
          <div>
            <Label htmlFor="name">Workspace name</Label>
            <Input id="name" placeholder="Acme Security" {...register("name")} />
            {errors.name && <p className="mt-1 text-xs text-danger">{errors.name.message}</p>}
          </div>
          <div>
            <Label htmlFor="description">Description (optional)</Label>
            <Input id="description" {...register("description")} />
          </div>
          {serverError && <p className="text-sm text-danger" role="alert">{serverError}</p>}
          <Button type="submit" className="w-full" isLoading={isSubmitting}>
            Create workspace
          </Button>
        </form>
      </div>
    </div>
  );
}
