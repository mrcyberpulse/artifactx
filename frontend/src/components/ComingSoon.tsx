import { Construction } from "lucide-react";

export function ComingSoon({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border py-24 text-center">
      <Construction className="mb-4 h-10 w-10 text-muted" strokeWidth={1.5} />
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      <p className="mt-2 max-w-md text-sm text-muted">
        This module is not yet implemented in ArtifactX Community Edition v1.0.0. It is planned
        for a future release as the platform's SBOM, vulnerability intelligence, and reporting
        capabilities are built out.
      </p>
    </div>
  );
}
