"use client";

import { useEffect, useState } from "react";
import { AuthShell } from "@/components/auth-shell";
import { api, Message } from "@/lib/api";
import { Badge, Card } from "@/components/ui";

export default function MessagesPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  useEffect(() => { api<Message[]>("/api/messages").then(setMessages); }, []);
  return (
    <AuthShell>
      <div className="mb-5">
        <h1 className="text-2xl font-semibold">Messages</h1>
        <p className="text-sm text-slate-600">Outbound history, inbound replies, and provider status.</p>
      </div>
      <div className="space-y-3">
        {messages.map((message) => (
          <Card key={message.id}>
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <Badge>{message.channel}</Badge>
              <Badge tone={message.direction === "inbound" ? "good" : "neutral"}>{message.direction}</Badge>
              <Badge tone={message.status === "FAILED" ? "bad" : "neutral"}>{message.status}</Badge>
              <span className="text-xs text-slate-500">{new Date(message.created_at).toLocaleString()}</span>
            </div>
            {message.subject ? <p className="font-medium">{message.subject}</p> : null}
            <p className="whitespace-pre-wrap text-sm text-slate-700">{message.body}</p>
          </Card>
        ))}
      </div>
    </AuthShell>
  );
}
