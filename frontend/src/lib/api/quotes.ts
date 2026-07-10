import { fetchCartApi } from "@/lib/api/client";

import type { QuoteSubmitPayload, QuoteSubmitResponse } from "./cart-types";

export async function submitQuote(payload: QuoteSubmitPayload): Promise<QuoteSubmitResponse> {
  const { data } = await fetchCartApi<QuoteSubmitResponse>("/quotes/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return data;
}
