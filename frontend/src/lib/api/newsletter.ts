import { fetchApiClient } from "@/lib/api/client";

export type SubscribeResult = "confirm_email_sent" | "already_subscribed";

export async function subscribeNewsletter(
  email: string,
  name = "",
  marketingAccepted: boolean,
  privacyPolicyVersion: string,
): Promise<SubscribeResult> {
  const data = await fetchApiClient<{ detail?: string }>("/newsletter/subscribe/", {
    method: "POST",
    body: JSON.stringify({
      email,
      name,
      marketing_accepted: marketingAccepted,
      privacy_policy_version: privacyPolicyVersion,
      website: "",
    }),
  });
  return data.detail === "already_subscribed" ? "already_subscribed" : "confirm_email_sent";
}

export async function confirmNewsletter(token: string): Promise<{ email: string }> {
  return fetchApiClient(`/newsletter/confirm/${token}/`);
}

export async function unsubscribeNewsletter(token: string): Promise<{ email: string }> {
  return fetchApiClient(`/newsletter/unsubscribe/${token}/`);
}
