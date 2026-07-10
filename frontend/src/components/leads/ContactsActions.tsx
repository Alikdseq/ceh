"use client";

import { ContactLeadDialog } from "@/components/leads/LeadDialogs";
import { Button } from "@/components/ui/button";

export function ContactsActions() {
  return (
    <div className="flex flex-wrap gap-2">
      <ContactLeadDialog trigger={<Button variant="outline" size="sm">Задать вопрос</Button>} />
    </div>
  );
}
