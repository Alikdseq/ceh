"use client";

import { ContactLeadDialog } from "@/components/leads/LeadDialogs";
import { Button } from "@/components/ui/button";

export function SupportContactSection() {
  return (
    <section className="mt-10 rounded-lg border p-6">
      <h2 className="font-display text-xl font-semibold">Не нашли ответ?</h2>
      <p className="mt-2 text-sm text-muted-foreground">Напишите нам — ответим в рабочее время.</p>
      <div className="mt-4">
        <ContactLeadDialog trigger={<Button>Задать вопрос</Button>} />
      </div>
    </section>
  );
}
