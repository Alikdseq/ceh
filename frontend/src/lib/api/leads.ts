import { fetchApiClient } from "@/lib/api/client";

export async function submitContactLead(data: {
  name: string;
  email: string;
  phone?: string;
  message: string;
  privacy_accepted: boolean;
  privacy_policy_version: string;
}): Promise<void> {
  await fetchApiClient("/leads/contact/", {
    method: "POST",
    body: JSON.stringify({ ...data, website: "" }),
  });
}

export async function submitCallbackLead(data: {
  name: string;
  phone: string;
  preferred_time?: string;
}): Promise<void> {
  await fetchApiClient("/leads/callback/", {
    method: "POST",
    body: JSON.stringify({ ...data, website: "" }),
  });
}
