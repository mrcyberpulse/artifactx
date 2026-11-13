import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/Card";
import type { MetricCard as MetricCardData } from "@/types/api";

export function MetricCardView({
  label,
  icon: Icon,
  data,
}: {
  label: string;
  icon: LucideIcon;
  data?: MetricCardData; // Made optional to prevent crash
}) {
  // Safe fallback if backend doesn't send this metric yet
  const isAvailable = data?.available ?? false;
  const value = data?.value ?? 0;
  const note = data?.note ?? "Available in a future release.";

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
          {isAvailable ? (
            <p className="mt-2 text-2xl font-semibold text-foreground">{value}</p>
          ) : (
            <p className="mt-2 text-sm text-muted">Coming soon</p>
          )}
        </div>
        <Icon className="h-5 w-5 text-muted" strokeWidth={1.5} />
      </div>
      {!isAvailable && <p className="mt-3 text-xs text-muted/80">{note}</p>}
    </Card>
  );
}
