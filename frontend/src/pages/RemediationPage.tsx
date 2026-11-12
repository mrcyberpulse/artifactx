import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus } from "lucide-react";
import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { formatDate } from "@/lib/utils";

export function RemediationPage() {
  const { currentWorkspace } = useWorkspace();
  const queryClient = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);
  const [title, setTitle] = useState("");

  const { data: tasks, isLoading } = useQuery({
    queryKey: ["remediation-tasks", currentWorkspace?.id],
    queryFn: () => api.get<any[]>(`/workspaces/${currentWorkspace!.id}/vulnerabilities/remediation/tasks`),
    enabled: Boolean(currentWorkspace),
  });

  const { data: findings } = useQuery({
    queryKey: ["vulnerabilities", currentWorkspace?.id],
    queryFn: () => api.get<any[]>(`/workspaces/${currentWorkspace!.id}/vulnerabilities/findings`),
    enabled: Boolean(currentWorkspace),
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !findings || findings.length === 0) {
      alert("Title is required and you must have at least one finding.");
      return;
    }
    try {
      await api.post(`/workspaces/${currentWorkspace!.id}/vulnerabilities/remediation/tasks`, {
        finding_id: findings[0].id,
        title: title,
        priority: "high"
      });
      setTitle("");
      setIsCreating(false);
      queryClient.invalidateQueries({ queryKey: ["remediation-tasks"] });
    } catch (err) {
      console.error(err);
    }
  };

  const handleStatusChange = async (taskId: string, newStatus: string) => {
    try {
      await api.patch(`/workspaces/${currentWorkspace!.id}/vulnerabilities/remediation/tasks/${taskId}`, {
        status: newStatus
      });
      queryClient.invalidateQueries({ queryKey: ["remediation-tasks"] });
    } catch (err) {
      console.error(err);
    }
  };

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Remediation Center</h1>
          <p className="mt-1 text-sm text-muted">Track and fix vulnerabilities found in your projects.</p>
        </div>
        <Button onClick={() => setIsCreating(!isCreating)}>
          <Plus className="h-4 w-4 mr-2" /> New Task
        </Button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="flex gap-2 p-4 border border-border rounded-lg bg-card">
          <input
            type="text"
            placeholder="Task title (e.g., Upgrade lodash to 4.17.21)"
            className="input-field flex-1"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Button type="submit">Save Task</Button>
        </form>
      )}

      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : !tasks || tasks.length === 0 ? (
        <EmptyState
          icon={Wrench}
          title="No remediation tasks"
          description="Create a task to fix a vulnerability."
        />
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-background-secondary text-left text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Task</th>
                <th className="px-4 py-3 font-medium">Priority</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {tasks.map((t: any) => (
                <tr key={t.id} className="hover:bg-background-secondary">
                  <td className="px-4 py-3 font-medium text-foreground">{t.title}</td>
                  <td className="px-4 py-3">
                    <span className="status-badge bg-warning/15 text-warning capitalize">{t.priority}</span>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={t.status}
                      onChange={(e) => handleStatusChange(t.id, e.target.value)}
                      className="bg-transparent text-foreground text-sm outline-none cursor-pointer"
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 text-muted">{formatDate(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
