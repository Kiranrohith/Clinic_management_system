import { createContext, useMemo, useState, type ReactNode } from "react";

import type { AuthUser } from "../types/auth";
import { clearStoredSession, getStoredAccessToken, getStoredRefreshToken, getStoredUserJson, setStoredSession } from "../utils/storage";

type AuthContextType = {
  token: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  setSession: (accessToken: string, refreshToken: string, authUser: AuthUser) => void;
  clearSession: () => void;
};

export const AuthContext = createContext<AuthContextType | null>(null);

type Props = {
  children: ReactNode;
};

export function AuthProvider({ children }: Props) {
  const [token, setToken] = useState<string | null>(() => getStoredAccessToken());
  const [refreshToken, setRefreshToken] = useState<string | null>(() => getStoredRefreshToken());
  const [user, setUser] = useState<AuthUser | null>(() => {
    const raw = getStoredUserJson();
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as AuthUser;
    } catch {
      return null;
    }
  });

  const value = useMemo(
    () => ({
      token,
      refreshToken,
      user,
      setSession: (accessToken: string, nextRefreshToken: string, authUser: AuthUser) => {
        setToken(accessToken);
        setRefreshToken(nextRefreshToken);
        setUser(authUser);
        setStoredSession(accessToken, nextRefreshToken, JSON.stringify(authUser));
      },
      clearSession: () => {
        setToken(null);
        setRefreshToken(null);
        setUser(null);
        clearStoredSession();
      }
    }),
    [token, refreshToken, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
