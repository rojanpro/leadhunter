export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function apiUrl(path: string) {
  if (API_URL.endsWith("?path=")) {
    return `${API_URL}${encodeURIComponent(path)}`;
  }
  return `${API_URL}${path}`;
}

export type Campaign = {
  id: number;
  name: string;
  business_type: string;
  city: string;
  country: string;
  keywords: string;
  radius: number;
  offer: string;
  your_name: string;
  agency_name: string;
  whatsapp_template: string;
  email_subject_template: string;
  email_template: string;
  daily_whatsapp_limit: number;
  daily_email_limit: number;
  message_delay_seconds: number;
  auto_send_whatsapp: boolean;
  auto_send_email: boolean;
  active: boolean;
};

export type Lead = {
  id: number;
  campaign_id: number;
  business_name: string;
  category: string | null;
  city: string;
  country: string;
  address: string | null;
  phone: string | null;
  phone_normalized: string | null;
  whatsapp_exists: boolean | null;
  email: string | null;
  website: string | null;
  website_status: string;
  google_maps_url: string | null;
  rating: number | null;
  review_count: number | null;
  seo_score: number;
  lead_reason: string | null;
  contact_status: string;
  do_not_contact: boolean;
  reply_message: string | null;
  created_at: string;
};

export type Message = {
  id: number;
  lead_id: number;
  channel: string;
  direction: string;
  subject: string | null;
  body: string;
  status: string;
  created_at: string;
};

export function getToken() {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("lead_hunter_token") || "";
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(apiUrl(path), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}
