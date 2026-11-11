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
  data: MetricCardData;
}) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p>
          {data.available ? (
            <p className="mt-2 text-2xl font-semibold text-foreground">{data.value}</p>
          ) : (
            <p className="mt-2 text-sm text-muted">Coming soon</p>
          )}
        </div>
        <Icon className="h-5 w-5 text-muted" strokeWidth={1.5} />
      </div>
      {!data.available && data.note && <p className="mt-3 text-xs text-muted/80">{data.note}</p>}
    </Card>
  );
}
