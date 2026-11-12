import { LayoutDashboard, FolderKanban, FileStack, Boxes, ShieldAlert, LineChart, GitBranch, ScrollText, Wrench, FileBarChart, Bell, History, Settings as SettingsIcon, Info } from "lucide-react";

export const NAV_ITEMS = [
  { label: "Overview", path: "/", icon: LayoutDashboard, implemented: true },
  { label: "Projects", path: "/projects", icon: FolderKanban, implemented: true },
  { label: "SBOM Inventory", path: "/sbom-inventory", icon: FileStack, implemented: true },
  { label: "Components", path: "/components", icon: Boxes, implemented: true },
  { label: "Vulnerability Intelligence", path: "/vulnerabilities", icon: ShieldAlert, implemented: true },
  { label: "Risk Analytics", path: "/risk-analytics", icon: LineChart, implemented: false },
  { label: "Dependency Graph", path: "/dependency-graph", icon: GitBranch, implemented: false },
  { label: "License Intelligence", path: "/license-intelligence", icon: ScrollText, implemented: false },
  { label: "Remediation Center", path: "/remediation", icon: Wrench, implemented: true },
  { label: "Reports", path: "/reports", icon: FileBarChart, implemented: true },
  { label: "Notifications", path: "/notifications", icon: Bell, implemented: false },
  { label: "Audit Logs", path: "/audit-logs", icon: History, implemented: true },
  { label: "Settings", path: "/settings", icon: SettingsIcon, implemented: true },
  { label: "About ArtifactX", path: "/about", icon: Info, implemented: true },
];
