import { Bell, Search, Moon, ChevronDown, LogOut, User as UserIcon } from "lucide-react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

import { useAuth } from "@/features/auth/AuthContext";
import { useWorkspace } from "@/features/workspace/WorkspaceContext";
import { cn } from "@/lib/utils";

export function Topbar() {
  const { user, logout } = useAuth();
  const { workspaces, currentWorkspace, setCurrentWorkspaceId } = useWorkspace();

  return (
    <header className="flex h-16 items-center justify-between gap-4 border-b border-border bg-background-secondary px-6">
      <div className="flex flex-1 items-center gap-3">
        <div className="relative hidden max-w-sm flex-1 sm:block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            placeholder="Search ArtifactX (coming soon)"
            disabled
            aria-label="Global search (coming in a future release)"
            className="w-full rounded-md border border-border bg-background py-2 pl-9 pr-3 text-sm text-muted placeholder:text-muted/70 disabled:cursor-not-allowed"
          />
        </div>

        {workspaces.length > 0 && (
          <DropdownMenu.Root>
            <DropdownMenu.Trigger className="flex items-center gap-1.5 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground hover:bg-card">
              {currentWorkspace?.name ?? "Select workspace"}
              <ChevronDown className="h-3.5 w-3.5 text-muted" />
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
              <DropdownMenu.Content
                align="start"
                className="z-50 min-w-[200px] rounded-md border border-border bg-card p-1 shadow-lg animate-fade-in"
              >
                {workspaces.map((ws) => (
                  <DropdownMenu.Item
                    key={ws.id}
                    onSelect={() => setCurrentWorkspaceId(ws.id)}
                    className={cn(
                      "cursor-pointer rounded-sm px-2.5 py-1.5 text-sm text-foreground outline-none hover:bg-background-secondary",
                      ws.id === currentWorkspace?.id && "text-primary",
                    )}
                  >
                    {ws.name}
                  </DropdownMenu.Item>
                ))}
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          disabled
          aria-label="Notifications (coming in a future release)"
          className="rounded-md p-2 text-muted disabled:cursor-not-allowed"
        >
          <Bell className="h-4.5 w-4.5" />
        </button>
        <button
          disabled
          aria-label="Theme settings (dark theme only in this release)"
          className="rounded-md p-2 text-muted disabled:cursor-not-allowed"
        >
          <Moon className="h-4.5 w-4.5" />
        </button>

        <DropdownMenu.Root>
          <DropdownMenu.Trigger className="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-card">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/20 text-xs font-medium text-primary">
              {user?.full_name?.slice(0, 1).toUpperCase() ?? <UserIcon className="h-3.5 w-3.5" />}
            </span>
            <span className="hidden text-sm text-foreground sm:inline">{user?.full_name}</span>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              align="end"
              className="z-50 min-w-[180px] rounded-md border border-border bg-card p-1 shadow-lg animate-fade-in"
            >
              <DropdownMenu.Item
                onSelect={() => void logout()}
                className="flex cursor-pointer items-center gap-2 rounded-sm px-2.5 py-1.5 text-sm text-foreground outline-none hover:bg-background-secondary"
              >
                <LogOut className="h-4 w-4" /> Log out
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>
    </header>
  );
}
