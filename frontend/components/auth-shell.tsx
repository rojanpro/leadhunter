"use client";

import { useEffect, useState } from "react";
import { Login } from "@/components/login";

export function AuthShell({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  useEffect(() => {
    setLoggedIn(Boolean(localStorage.getItem("lead_hunter_token")));
    setReady(true);
  }, []);
  if (!ready) return null;
  if (!loggedIn) return <Login onLogin={() => setLoggedIn(true)} />;
  return <>{children}</>;
}
