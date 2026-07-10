"use client";

import { ContactLeadDialog } from "@/components/leads/LeadDialogs";

interface HeaderLeadActionsProps {
  mobile?: boolean;
}

export function HeaderLeadActions({ mobile }: HeaderLeadActionsProps) {
  return <ContactLeadDialog mobile={mobile} />;
}
