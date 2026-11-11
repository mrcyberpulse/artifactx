import type { ReactNode } from "react";
import { ShieldCheck } from "lucide-react";

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center text-center">
          <ShieldCheck className="mb-3 h-9 w-9 text-primary" strokeWidth={1.5} />
          <h1 className="text-xl font-semibold text-foreground">ArtifactX</h1>
          <p className="mt-1 text-sm text-muted">{subtitle}</p>
        </div>
        <div className="card">
          <h2 className="mb-5 text-base font-semibold text-foreground">{title}</h2>
          {children}
        </div>
        <p className="mt-6 text-center text-xs text-muted">
          ArtifactX v1.0.0 | Created by Harsh Saini (MR CYBER)
        </p>
      </div>
    </div>
  );
}
