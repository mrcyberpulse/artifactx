import { useState } from "react";
import { FileBarChart, Download, FileText, Loader2 } from "lucide-react";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { Button } from "@/components/ui/Button";
import { getAccessToken } from "@/lib/token-store";

type ReportFormat = "csv" | "pdf";

export function ReportsPage() {
  const { currentWorkspace } = useWorkspace();
  const [downloading, setDownloading] = useState<ReportFormat | null>(null);

  const downloadFile = async (format: ReportFormat) => {
    if (!currentWorkspace) return;
    setDownloading(format);
    try {
      const token = getAccessToken();
      const response = await fetch(
        `http://localhost:8000/api/workspaces/${currentWorkspace.id}/reports/export/${format}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!response.ok) throw new Error(`Export failed (${response.status})`);

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `artifactx_report.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Report download failed:", err);
    } finally {
      setDownloading(null);
    }
  };

  if (!currentWorkspace) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-foreground">Reports</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileBarChart className="h-8 w-8 text-primary" />
            <div>
              <h2 className="text-sm font-medium text-foreground">Vulnerability Report (CSV)</h2>
              <p className="text-xs text-muted">Export all vulnerabilities and risk scores.</p>
            </div>
          </div>
          <Button
            onClick={() => downloadFile("csv")}
            variant="secondary"
            disabled={downloading !== null}
          >
            {downloading === "csv" ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Download className="h-4 w-4 mr-2" />
            )}
            CSV
          </Button>
        </div>

        <div className="card flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="h-8 w-8 text-accent" />
            <div>
              <h2 className="text-sm font-medium text-foreground">Executive Summary (PDF)</h2>
              <p className="text-xs text-muted">Professional report with risk breakdown.</p>
            </div>
          </div>
          <Button
            onClick={() => downloadFile("pdf")}
            variant="primary"
            disabled={downloading !== null}
          >
            {downloading === "pdf" ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Download className="h-4 w-4 mr-2" />
            )}
            PDF
          </Button>
        </div>
      </div>
    </div>
  );
}
