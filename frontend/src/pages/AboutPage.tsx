import { useQuery } from "@tanstack/react-query";
import { ShieldCheck } from "lucide-react";

import { api } from "@/lib/api-client";
import { Card } from "@/components/ui/Card";
import type { AppInfo } from "@/types/api";

export function AboutPage() {
  const { data: info } = useQuery({
    queryKey: ["app-info"],
    queryFn: () => api.get<AppInfo>("/info"),
  });

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <Card className="flex flex-col items-center text-center">
        <ShieldCheck className="mb-3 h-10 w-10 text-primary" strokeWidth={1.5} />
        <h1 className="text-xl font-semibold text-foreground">{info?.app_name ?? "ArtifactX"}</h1>
        <p className="mt-1 text-sm text-muted">{info?.edition ?? "Community Edition"} &middot; v{info?.version ?? "1.0.0"}</p>
        <p className="mt-4 max-w-md text-sm text-muted">
          ArtifactX is an open-source Software Bill of Materials (SBOM) intelligence platform for
          software supply-chain security: component inventory, vulnerability intelligence, risk
          scoring, license analysis, and remediation tracking.
        </p>
      </Card>

      <Card>
        <h2 className="mb-3 text-sm font-medium text-muted">Roadmap</h2>
        <ul className="space-y-2 text-sm text-foreground">
          <li>&bull; Part 1 (this release): architecture, authentication, workspaces, projects</li>
          <li>&bull; Part 2: SBOM ingestion, parsing, and component inventory</li>
          <li>&bull; Part 3: Vulnerability intelligence, risk analytics, remediation</li>
          <li>&bull; Part 4: Reporting, CLI, CI/CD integrations, cross-platform release</li>
        </ul>
      </Card>

      <p className="text-center text-xs text-muted">
        {info?.footer ??
          "ArtifactX v1.0.0 | Created by MR Cyber Pulse (Harsh saini) | Open-Source SBOM Intelligence Platform"}
        <br />
        Licensed under MIT. Source on{" "}
        <a
          href="https://github.com/mrcyberharsh"
          target="_blank"
          rel="noreferrer"
          className="text-accent hover:underline"
        >
          GitHub
        </a>
        .
      </p>
    </div>
  );
}
