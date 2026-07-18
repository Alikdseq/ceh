"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { submitContactLead } from "@/lib/api/leads";
import { ApiError } from "@/lib/api/client";
import { cn } from "@/lib/utils";
import Link from "next/link";

export function DealerForm({ className }: { className?: string }) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [privacy, setPrivacy] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!privacy) {
      setError("Необходимо согласие на обработку персональных данных");
      return;
    }
    setLoading(true);
    setError(null);
    const form = new FormData(e.currentTarget);
    const company = String(form.get("company"));
    const message = `Партнёрство: ${company}\n${String(form.get("message") || "")}`;
    try {
      await submitContactLead({
        name: String(form.get("name")),
        email: String(form.get("email")),
        phone: String(form.get("phone") || ""),
        message,
        privacy_accepted: true,
        privacy_policy_version: "2026-07-07",
      });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Ошибка отправки");
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return <p className="text-sm text-muted-foreground">Заявка отправлена. Мы свяжемся с вами.</p>;
  }

  return (
    <form onSubmit={onSubmit} className={cn("space-y-4", className)}>
      <div className="space-y-2">
        <Label htmlFor="dealer-name">Контактное лицо *</Label>
        <Input id="dealer-name" name="name" required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="dealer-company">Компания *</Label>
        <Input id="dealer-company" name="company" required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="dealer-email">Email *</Label>
        <Input id="dealer-email" name="email" type="email" required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="dealer-phone">Телефон</Label>
        <Input id="dealer-phone" name="phone" type="tel" />
      </div>
      <div className="space-y-2">
        <Label htmlFor="dealer-message">Комментарий</Label>
        <textarea
          id="dealer-message"
          name="message"
          rows={3}
          className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="relative flex items-start gap-2">
        <input
          id="dealer-privacy"
          type="checkbox"
          checked={privacy}
          onChange={(e) => setPrivacy(e.target.checked)}
          className="mt-1 h-4 w-4 rounded border-input"
          required
        />
        <Label htmlFor="dealer-privacy" className="text-sm leading-snug font-normal">
          Даю согласие на{" "}
          <Link href="/privacy/" className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
            обработку персональных данных
          </Link>{" "}
          *
        </Label>
      </div>
      <Button type="submit" variant="accent" disabled={loading}>
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Отправить заявку
      </Button>
    </form>
  );
}
