"use client";

import { useEffect, useState } from "react";
import { Pause, Play, Plus, Save } from "lucide-react";
import { AuthShell } from "@/components/auth-shell";
import { api, Campaign } from "@/lib/api";
import { Badge, Button, Card, Input, Textarea } from "@/components/ui";

const whatsappTemplate = `Hi {{business_name}}, I found your business on Google Maps while searching for {{category}} in {{city}}.

I noticed you may not have a proper website yet. We help local businesses create modern websites and improve Google SEO so more customers can find and contact them online.

Would you like me to send a simple example for {{business_name}}?

You can check my work at www.rojan.pro.

Reply STOP if you do not want messages.`;

const emailTemplate = `Hi {{business_name}},

I found your business on Google Maps while searching for {{category}} in {{city}}. I noticed you may not have a proper website yet.

We help local businesses build modern websites and improve Google visibility so more customers can find and contact them online.

Would you like me to send a simple example of how your website could look?

You can check my work at www.rojan.pro.

Regards,
Rojan Shrestha
www.rojan.pro

Reply unsubscribe if you do not want further messages.`;

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [form, setForm] = useState({
    name: "Kathmandu Dental Clinics",
    business_type: "Dental clinics",
    city: "Kathmandu",
    country: "Nepal",
    keywords: "dental clinic,dentist,dental care",
    radius: 8000,
    offer: "Website design and local SEO",
    your_name: "Rojan Shrestha",
    agency_name: "www.rojan.pro",
    whatsapp_template: whatsappTemplate,
    email_subject_template: "Quick idea for {{business_name}}",
    email_template: emailTemplate,
    daily_whatsapp_limit: 30,
    daily_email_limit: 30,
    message_delay_seconds: 90,
    auto_send_whatsapp: false,
    auto_send_email: false,
    active: true
  });

  async function load() {
    setCampaigns(await api<Campaign[]>("/api/campaigns"));
  }
  useEffect(() => { load(); }, []);
  async function create() {
    await api("/api/campaigns", { method: "POST", body: JSON.stringify(form) });
    await load();
  }
  async function toggle(campaign: Campaign) {
    await api(`/api/campaigns/${campaign.id}/${campaign.active ? "pause" : "start"}`, { method: "POST" });
    await load();
  }

  return (
    <AuthShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Campaigns</h1>
        <p className="text-sm text-slate-600">Create local search and outreach campaigns with limits and templates.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-[420px_1fr]">
        <Card>
          <div className="mb-3 flex items-center gap-2 font-semibold"><Plus className="h-4 w-4" /> New Campaign</div>
          <div className="space-y-3">
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <div className="grid grid-cols-2 gap-3">
              <Input value={form.business_type} onChange={(e) => setForm({ ...form, business_type: e.target.value })} />
              <Input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
            </div>
            <Input value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
            <Input value={form.keywords} onChange={(e) => setForm({ ...form, keywords: e.target.value })} />
            <div className="grid grid-cols-3 gap-3">
              <Input type="number" value={form.radius} onChange={(e) => setForm({ ...form, radius: Number(e.target.value) })} />
              <Input type="number" value={form.daily_whatsapp_limit} onChange={(e) => setForm({ ...form, daily_whatsapp_limit: Number(e.target.value) })} />
              <Input type="number" value={form.daily_email_limit} onChange={(e) => setForm({ ...form, daily_email_limit: Number(e.target.value) })} />
            </div>
            <Textarea value={form.whatsapp_template} onChange={(e) => setForm({ ...form, whatsapp_template: e.target.value })} />
            <Textarea value={form.email_template} onChange={(e) => setForm({ ...form, email_template: e.target.value })} />
            <div className="flex gap-4 text-sm">
              <label><input type="checkbox" checked={form.auto_send_whatsapp} onChange={(e) => setForm({ ...form, auto_send_whatsapp: e.target.checked })} /> Auto WhatsApp</label>
              <label><input type="checkbox" checked={form.auto_send_email} onChange={(e) => setForm({ ...form, auto_send_email: e.target.checked })} /> Auto Email</label>
            </div>
            <Button onClick={create}><Save className="h-4 w-4" /> Create</Button>
          </div>
        </Card>
        <div className="space-y-3">
          {campaigns.map((campaign) => (
            <Card key={campaign.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="font-semibold">{campaign.name}</h2>
                    <Badge tone={campaign.active ? "good" : "warn"}>{campaign.active ? "Active" : "Paused"}</Badge>
                  </div>
                  <p className="text-sm text-slate-600">{campaign.business_type} in {campaign.city}, {campaign.country}</p>
                  <p className="mt-2 text-sm">Keywords: {campaign.keywords}</p>
                </div>
                <Button onClick={() => toggle(campaign)}>{campaign.active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}{campaign.active ? "Pause" : "Start"}</Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </AuthShell>
  );
}
