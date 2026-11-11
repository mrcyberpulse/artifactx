import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api-client";
import { useAuth } from "@/features/auth/AuthContext";
import type { Workspace } from "@/types/api";

const STORAGE_KEY = "artifactx.currentWorkspaceId";

interface WorkspaceContextValue {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  isLoading: boolean;
  setCurrentWorkspaceId: (id: string) => void;
  refetch: () => void;
}

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY),
  );

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => api.get<Workspace[]>("/workspaces"),
    enabled: isAuthenticated,
  });

  const workspaces = useMemo(() => data ?? [], [data]);

  useEffect(() => {
    if (workspaces.length === 0) return;
    const stillExists = workspaces.some((w) => w.id === currentWorkspaceId);
    if (!stillExists) {
      setCurrentWorkspaceId(workspaces[0].id);
    }
  }, [workspaces, currentWorkspaceId]);

  const handleSetCurrentWorkspaceId = (id: string) => {
    setCurrentWorkspaceId(id);
    localStorage.setItem(STORAGE_KEY, id);
  };

  const currentWorkspace = workspaces.find((w) => w.id === currentWorkspaceId) ?? null;

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        currentWorkspace,
        isLoading,
        setCurrentWorkspaceId: handleSetCurrentWorkspaceId,
        refetch,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within WorkspaceProvider.");
  return ctx;
}
