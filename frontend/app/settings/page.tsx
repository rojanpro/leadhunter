"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { AuthShell } from "@/components/auth-shell";
import { api } from "@/lib/api";
import { Card } from "@/components/ui";

type Status = Record<string, boolean | number>;

export default function SettingsPage() {
  const [status, setStatus] = useState<Status>({});
  useEffect(() => { api<Status>("/api/settings/status").then(setStatus); }, []);
  return (
    <AuthShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-slate-600">Configuration is read from environment variables and secrets stay out of source.</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {Object.entries(status).map(([key, value]) => (
          <Card key={key}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{key.replaceAll("_", " ")}</span>
              {typeof value === "boolean" ? value ? <CheckCircle2 className="h-5 w-5 text-emerald-700" /> : <XCircle className="h-5 w-5 text-rose-700" /> : <span>{value}</span>}
            </div>
          </Card>
        ))}
      </div>
    </AuthShell>
  );
}
