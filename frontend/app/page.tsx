"use client";

import { useEffect, useState } from "react";
import { Activity, Mail, MessageCircle, RefreshCw, Reply, Users } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { api } from "@/lib/api";
import { AuthShell } from "@/components/auth-shell";
import { Button, Card } from "@/components/ui";

type Overview = { total_leads: number; qualified_leads: number; whatsapp_sent: number; email_sent: number; replies: number; failed_messages: number };
type Stat = [string, number | undefined, LucideIcon];

export default function OverviewPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState("");
  async function load() {
    try {
      setData(await api<Overview>("/api/overview"));
    } catch (err) {
      setError(String(err));
    }
  }
  useEffect(() => { load(); }, []);
  async function runDiscovery() {
    await api("/api/jobs/run-discovery", { method: "POST" });
  }
  const stats: Stat[] = [
    ["Total leads", data?.total_leads, Users],
    ["Qualified", data?.qualified_leads, Activity],
    ["WhatsApp sent", data?.whatsapp_sent, MessageCircle],
    ["Email sent", data?.email_sent, Mail],
    ["Replies", data?.replies, Reply],
    ["Failed", data?.failed_messages, RefreshCw]
  ];
  return (
    <AuthShell>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Overview</h1>
          <p className="text-sm text-slate-600">Live campaign, lead, message, and reply totals.</p>
        </div>
        <Button onClick={runDiscovery}><RefreshCw className="h-4 w-4" /> Run Discovery</Button>
      </div>
      {error ? <Card className="text-rose-700">{error}</Card> : null}
      <div className="grid gap-4 md:grid-cols-3">
        {stats.map(([label, value, Icon]) => (
          <Card key={String(label)}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">{label}</p>
                <p className="text-3xl font-semibold">{value ?? "-"}</p>
              </div>
              <Icon className="h-6 w-6 text-primary" />
            </div>
          </Card>
        ))}
      </div>
    </AuthShell>
  );
}
