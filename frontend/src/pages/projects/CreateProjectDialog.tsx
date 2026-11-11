import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { DialogContent } from "@/components/ui/Dialog";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { api, ApiError } from "@/lib/api-client";
import { projectSchema, type ProjectFormValues } from "@/lib/validation";
import type { Project } from "@/types/api";

export function CreateProjectDialog({
  workspaceId,
  onCreated,
}: {
  workspaceId: string;
  onCreated: () => void;
}) {
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: { environment: "development", business_criticality: "medium" },
  });

  const onSubmit = async (values: ProjectFormValues) => {
    setServerError(null);
    try {
      await api.post<Project>(`/workspaces/${workspaceId}/projects`, {
        ...values,
        repository_url: values.repository_url || null,
        description: values.description || null,
      });
      onCreated();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Unable to create project.");
    }
  };

  return (
    <DialogContent title="New project" description="Add a project to this workspace.">
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
          <Input id="repository_url" placeholder="https://github.com/org/repo" {...register("repository_url")} />
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
        <Button type="submit" className="w-full" isLoading={isSubmitting}>
          Create project
        </Button>
      </form>
    </DialogContent>
  );
}
