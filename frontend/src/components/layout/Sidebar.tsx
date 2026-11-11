import { NavLink } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS } from "@/components/layout/nav-items";

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-background-secondary md:flex">
      <div className="flex h-16 items-center gap-2 border-b border-border px-5">
        <ShieldCheck className="h-6 w-6 text-primary" strokeWidth={1.75} />
        <span className="text-base font-semibold tracking-tight text-foreground">ArtifactX</span>
      </div>
      <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4" aria-label="Main navigation">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center justify-between rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted hover:bg-card hover:text-foreground",
              )
            }
          >
            <span className="flex items-center gap-2.5">
              <item.icon className="h-4 w-4" strokeWidth={1.75} />
              {item.label}
            </span>
            {!item.implemented && (
              <span className="rounded-full bg-border/40 px-1.5 py-0.5 text-[10px] font-medium text-muted">
                Soon
              </span>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-border px-4 py-3 text-xs text-muted">
        ArtifactX v1.0.0
        <br />
        Created by Harsh Saini (MR CYBER)
      </div>
    </aside>
  );
}
