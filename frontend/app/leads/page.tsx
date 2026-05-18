"use client";

import { useEffect, useState } from "react";
import { Mail, MessageCircle, Search, ShieldX } from "lucide-react";
import { AuthShell } from "@/components/auth-shell";
import { api, Lead } from "@/lib/api";
import { Badge, Button, Card, Select } from "@/components/ui";

function tone(status: string) {
  if (status.includes("NO") || status.includes("BAD")) return "bad" as const;
  if (status.includes("SOCIAL")) return "warn" as const;
  return "neutral" as const;
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [websiteStatus, setWebsiteStatus] = useState("");
  const [running, setRunning] = useState(false);
  async function load() {
    const query = websiteStatus ? `?website_status=${websiteStatus}` : "";
    setLeads(await api<Lead[]>(`/api/leads${query}`));
  }
  useEffect(() => { load(); }, [websiteStatus]);
  async function action(id: number, path: string) {
    await api(`/api/leads/${id}/${path}`, { method: "POST" });
    await load();
  }
  async function runDiscovery() {
    setRunning(true);
    try {
      await api("/api/jobs/run-discovery", { method: "POST" });
    } finally {
      setRunning(false);
    }
  }
  return (
    <AuthShell>
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Leads</h1>
          <p className="text-sm text-slate-600">Qualified businesses with outreach actions and contact controls.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <div className="w-52">
            <Select value={websiteStatus} onChange={(e) => setWebsiteStatus(e.target.value)}>
              <option value="">All website statuses</option>
              <option value="NO_WEBSITE">No website</option>
              <option value="SOCIAL_ONLY">Social only</option>
              <option value="BAD_WEBSITE">Bad website</option>
              <option value="HAS_WEBSITE">Has website</option>
            </Select>
          </div>
          <Button onClick={runDiscovery} disabled={running}><Search className="h-4 w-4" /> {running ? "Queued" : "Run discovery"}</Button>
        </div>
      </div>
      <Card className="overflow-x-auto p-0">
        <table className="w-full min-w-[1050px] text-left text-sm">
          <thead className="bg-muted text-xs uppercase text-slate-600">
            <tr>
              <th className="px-3 py-3">Business</th>
              <th className="px-3 py-3">Phone</th>
              <th className="px-3 py-3">Website</th>
              <th className="px-3 py-3">Score</th>
              <th className="px-3 py-3">Status</th>
              <th className="px-3 py-3">Reason</th>
              <th className="px-3 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} className="border-t border-border align-top">
                <td className="px-3 py-3">
                  <div className="font-medium">{lead.business_name}</div>
                  <div className="text-xs text-slate-600">{lead.category} · {lead.city}</div>
                </td>
                <td className="px-3 py-3">{lead.phone_normalized || lead.phone || "-"}</td>
                <td className="px-3 py-3"><Badge tone={tone(lead.website_status)}>{lead.website_status}</Badge></td>
                <td className="px-3 py-3 font-semibold">{lead.seo_score}</td>
                <td className="px-3 py-3">{lead.do_not_contact ? <Badge tone="bad">DO NOT CONTACT</Badge> : <Badge>{lead.contact_status}</Badge>}</td>
                <td className="max-w-xs px-3 py-3 text-xs text-slate-600">{lead.lead_reason}</td>
                <td className="px-3 py-3">
                  <div className="flex flex-wrap gap-2">
                    <Button onClick={() => action(lead.id, "send-whatsapp")}><MessageCircle className="h-4 w-4" /> WA</Button>
                    <Button onClick={() => action(lead.id, "send-email")}><Mail className="h-4 w-4" /> Email</Button>
                    <Button className="bg-rose-700 hover:bg-rose-800" onClick={() => action(lead.id, "mark-do-not-contact")}><ShieldX className="h-4 w-4" /> DNC</Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </AuthShell>
  );
}
