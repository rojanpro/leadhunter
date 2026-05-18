import type { Metadata } from "next";
import "./globals.css";
import { BarChart3, Megaphone, MessageSquareText, Settings, Users } from "lucide-react";
import { NavLink } from "@/components/ui";

export const metadata: Metadata = {
  title: "AI Lead Hunter",
  description: "Autonomous local lead discovery and outreach dashboard"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-border bg-white">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
              <div className="flex items-center gap-2 font-semibold">
                <Megaphone className="h-5 w-5 text-primary" />
                AI Lead Hunter
              </div>
              <nav className="flex flex-wrap items-center gap-1">
                <NavLink href="/"><BarChart3 className="inline h-4 w-4" /> Overview</NavLink>
                <NavLink href="/campaigns"><Megaphone className="inline h-4 w-4" /> Campaigns</NavLink>
                <NavLink href="/leads"><Users className="inline h-4 w-4" /> Leads</NavLink>
                <NavLink href="/messages"><MessageSquareText className="inline h-4 w-4" /> Messages</NavLink>
                <NavLink href="/settings"><Settings className="inline h-4 w-4" /> Settings</NavLink>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
