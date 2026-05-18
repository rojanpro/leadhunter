import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import Link from "next/link";

export function cn(...inputs: Array<string | undefined | false>) {
  return twMerge(clsx(inputs));
}

export function Button({ className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={cn("inline-flex h-9 items-center justify-center gap-2 rounded-md bg-primary px-3 text-sm font-medium text-white transition hover:bg-teal-800 disabled:opacity-50", className)} {...props} />;
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className="h-9 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-primary" {...props} />;
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className="min-h-28 w-full rounded-md border border-border bg-white px-3 py-2 text-sm outline-none focus:border-primary" {...props} />;
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className="h-9 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-primary" {...props} />;
}

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-lg border border-border bg-white p-4 shadow-sm", className)} {...props} />;
}

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "good" | "bad" | "warn" }) {
  const tones = {
    neutral: "bg-muted text-foreground",
    good: "bg-emerald-100 text-emerald-800",
    bad: "bg-rose-100 text-rose-800",
    warn: "bg-amber-100 text-amber-900"
  };
  return <span className={cn("inline-flex rounded px-2 py-1 text-xs font-medium", tones[tone])}>{children}</span>;
}

export function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return <Link className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-muted" href={href}>{children}</Link>;
}
