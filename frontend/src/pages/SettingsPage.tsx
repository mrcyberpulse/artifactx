import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api-client";
import { useAuth } from "@/features/auth/AuthContext";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { AppInfo } from "@/types/api";

export function SettingsPage() {
  const { user } = useAuth();
  const { currentWorkspace } = useWorkspace();

  const { data: info } = useQuery({
    queryKey: ["app-info"],
    queryFn: () => api.get<AppInfo>("/info"),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Settings</h1>
        <p className="mt-1 text-sm text-muted">Account, workspace, and application preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <dl className="grid grid-cols-[120px_1fr] gap-y-2 text-sm">
          <dt className="text-muted">Name</dt>
          <dd className="text-foreground">{user?.full_name}</dd>
          <dt className="text-muted">Email</dt>
          <dd className="text-foreground">{user?.email}</dd>
        </dl>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Current Workspace</CardTitle>
        </CardHeader>
        {currentWorkspace ? (
          <dl className="grid grid-cols-[120px_1fr] gap-y-2 text-sm">
            <dt className="text-muted">Name</dt>
            <dd className="text-foreground">{currentWorkspace.name}</dd>
            <dt className="text-muted">Slug</dt>
            <dd className="font-mono text-foreground">{currentWorkspace.slug}</dd>
            <dt className="text-muted">Your role</dt>
            <dd>
              <Badge tone="info">{currentWorkspace.role}</Badge>
            </dd>
          </dl>
        ) : (
          <p className="text-sm text-muted">No workspace selected.</p>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
        </CardHeader>
        <div className="flex items-center justify-between text-sm">
          <span className="text-foreground">Theme</span>
          <Badge tone="neutral">Dark (default) &mdash; additional themes coming soon</Badge>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Application</CardTitle>
        </CardHeader>
        <dl className="grid grid-cols-[120px_1fr] gap-y-2 text-sm">
          <dt className="text-muted">Name</dt>
          <dd className="text-foreground">{info?.app_name ?? "ArtifactX"}</dd>
          <dt className="text-muted">Edition</dt>
          <dd className="text-foreground">{info?.edition ?? "Community Edition"}</dd>
          <dt className="text-muted">Version</dt>
          <dd className="text-foreground">{info?.version ?? "1.0.0"}</dd>
        </dl>
      </Card>
    </div>
  );
}
