export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export type WorkspaceRole = "owner" | "admin" | "member" | "viewer";

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  role: WorkspaceRole;
  created_at: string;
}

export type Environment = "development" | "staging" | "production";
export type Criticality = "low" | "medium" | "high" | "critical";

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  repository_url: string | null;
  owner_id: string | null;
  environment: Environment;
  business_criticality: Criticality;
  created_at: string;
  updated_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface MetricCard {
  value: number | null;
  available: boolean;
  note: string | null;
}

export interface DashboardSummary {
  total_projects: MetricCard;
  sbom_documents: MetricCard;
  components: MetricCard;
  vulnerability_findings: MetricCard;
  critical_findings: MetricCard;
  high_risk_findings: MetricCard;
  outdated_components: MetricCard;
  remediation_progress: MetricCard;
}

export interface AuditEvent {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  summary: Record<string, unknown>;
  actor_name: string | null;
  created_at: string;
}

export interface AppInfo {
  app_name: string;
  edition: string;
  version: string;
  brand: string;
  creator: string;
  footer: string;
}
