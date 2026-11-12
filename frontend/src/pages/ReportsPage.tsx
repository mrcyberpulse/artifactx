import { FileBarChart, Download } from "lucide-react";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { Button } from "@/components/ui/Button";
import { getAccessToken } from "@/lib/token-store";

export function ReportsPage() {
  const { currentWorkspace } = useWorkspace();

  const handleDownload = async () => {
    const token = getAccessToken();
    const response = await fetch(`http://localhost:8000/api/workspaces/${currentWorkspace!.id}/reports/export/csv`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `artifactx_report.csv`;
    a.click();
  };

  if (!currentWorkspace) return null;
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-foreground">Reports</h1>
      <div className="card flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileBarChart className="h-8 w-8 text-primary" />
          <div>
            <h2 className="text-sm font-medium text-foreground">Vulnerability Report (CSV)</h2>
            <p className="text-xs text-muted">Export all vulnerabilities and risk scores.</p>
          </div>
        </div>
        <Button onClick={handleDownload}><Download className="h-4 w-4 mr-2" /> Download</Button>
      </div>
    </div>
  );
}
