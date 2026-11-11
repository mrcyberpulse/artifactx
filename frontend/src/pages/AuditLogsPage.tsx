import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { History } from "lucide-react";

import { api } from "@/lib/api-client";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { formatDateTime } from "@/lib/utils";
import type { AuditEvent, Page } from "@/types/api";

const ACTION_LABELS: Record<string, string> = {
  "auth.register": "User registered",
  "auth.login": "User signed in",
  "auth.password_reset_requested": "Password reset requested",
  "auth.password_reset_completed": "Password reset completed",
  "workspace.created": "Workspace created",
  "project.created": "Project created",
  "project.updated": "Project updated",
  "project.deleted": "Project deleted",
};

export function AuditLogsPage() {
  const { currentWorkspace } = useWorkspace();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["audit-events", currentWorkspace?.id, page],
    queryFn: () =>
      api.get<Page<AuditEvent>>(
        `/workspaces/${currentWorkspace!.id}/audit-events?page=${page}&page_size=25`,
      ),
    enabled: Boolean(currentWorkspace),
  });

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Audit Logs</h1>
        <p className="mt-1 text-sm text-muted">
          Security-relevant events recorded for {currentWorkspace.name}.
        </p>
      </div>

      {isLoading ? (
        <div className="flex h-48 items-center justify-center">
          <span className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          icon={History}
          title="No audit events yet"
          description="Actions like workspace and project changes will appear here as they happen."
        />
      ) : (
        <>
          <div className="overflow-hidden rounded-lg border border-border">
            <table className="w-full text-sm">
              <thead className="bg-background-secondary text-left text-xs uppercase tracking-wide text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Event</th>
                  <th className="px-4 py-3 font-medium">Actor</th>
                  <th className="px-4 py-3 font-medium">Resource</th>
                  <th className="px-4 py-3 font-medium">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.items.map((event) => (
                  <tr key={event.id}>
                    <td className="px-4 py-3 font-medium text-foreground">
                      {ACTION_LABELS[event.action] ?? event.action}
                    </td>
                    <td className="px-4 py-3 text-muted">{event.actor_name ?? "System"}</td>
                    <td className="px-4 py-3 text-muted">{event.resource_type}</td>
                    <td className="px-4 py-3 text-muted">{formatDateTime(event.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.pages > 1 && (
            <div className="flex items-center justify-between text-sm text-muted">
              <span>
                Page {data.page} of {data.pages} ({data.total} total)
              </span>
              <div className="flex gap-2">
                <Button variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  disabled={page >= data.pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
