"use client";

import { useEffect, useRef, useState } from "react";
import { Button, Card, Input } from "@/components/ui";
import { apiUrl } from "@/lib/api";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: { credential: string }) => void }) => void;
          renderButton: (element: HTMLElement, options: Record<string, string | number | boolean>) => void;
        };
      };
    };
  }
}

export function Login({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    const response = await fetch(apiUrl("/api/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) {
      setError("Login failed");
      return;
    }
    const data = await response.json();
    localStorage.setItem("lead_hunter_token", data.access_token);
    onLogin();
  }

  useEffect(() => {
    if (!googleClientId || !googleButtonRef.current) return;
    const render = () => {
      if (!window.google || !googleButtonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: async ({ credential }) => {
          setError("");
          const response = await fetch(apiUrl("/api/auth/google"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ credential })
          });
          if (!response.ok) {
            setError("Google login failed");
            return;
          }
          const data = await response.json();
          localStorage.setItem("lead_hunter_token", data.access_token);
          onLogin();
        }
      });
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: "outline",
        size: "large",
        width: 360,
        text: "signin_with"
      });
    };
    if (window.google) {
      render();
      return;
    }
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = render;
    document.head.appendChild(script);
  }, [googleClientId, onLogin]);

  return (
    <div className="mx-auto max-w-md pt-16">
      <Card>
        <form className="space-y-4" onSubmit={submit}>
          <div>
            <h1 className="text-xl font-semibold">Dashboard Login</h1>
            <p className="text-sm text-slate-600">Sign in with the configured dashboard Gmail or admin password.</p>
          </div>
          {googleClientId ? <div ref={googleButtonRef} /> : null}
          <Input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
          <Input value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="Password" />
          {error ? <p className="text-sm text-rose-700">{error}</p> : null}
          <Button className="w-full">Sign in</Button>
        </form>
      </Card>
    </div>
  );
}
