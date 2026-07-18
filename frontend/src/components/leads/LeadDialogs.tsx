"use client";

import { useState } from "react";
import { Loader2, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { submitContactLead } from "@/lib/api/leads";
import { ApiError } from "@/lib/api/client";
import Link from "next/link";

function Honeypot() {
  return (
    <div className="absolute -left-[9999px]" aria-hidden>
      <input name="website" tabIndex={-1} autoComplete="off" />
    </div>
  );
}

interface LeadDialogOptions {
  trigger?: React.ReactNode;
  mobile?: boolean;
}

export function ContactLeadDialog({ trigger, mobile }: LeadDialogOptions) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [privacy, setPrivacy] = useState(false);

  function handleClose() {
    setOpen(false);
    setDone(false);
    setError(null);
    setPrivacy(false);
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    if (!privacy) {
      setError("Необходимо согласие на обработку персональных данных");
      return;
    }
    setLoading(true);
    const form = new FormData(e.currentTarget);
    try {
      await submitContactLead({
        name: String(form.get("name")),
        email: String(form.get("email")),
        phone: String(form.get("phone") || ""),
        message: String(form.get("message")),
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

  const defaultTrigger = mobile ? (
    <Button variant="outline" className="w-full justify-start gap-2">
      <Mail className="h-4 w-4" />
      Написать
    </Button>
  ) : (
    <Button variant="ghost" size="sm" className="gap-1.5 text-white hover:bg-white/10 hover:text-white">
      <Mail className="h-4 w-4 shrink-0" />
      <span className="hidden lg:inline">Написать</span>
    </Button>
  );

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) {
          setDone(false);
          setError(null);
        }
      }}
    >
      <DialogTrigger asChild>{trigger ?? defaultTrigger}</DialogTrigger>
      {open ? (
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Написать нам</DialogTitle>
        </DialogHeader>
        {done ? (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Сообщение отправлено. Мы ответим на указанный email.
            </p>
            <Button type="button" variant="outline" className="w-full" onClick={handleClose}>
              Закрыть
            </Button>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="relative space-y-4">
            <Honeypot />
            <div className="space-y-2">
              <Label htmlFor="contact-name">ФИО *</Label>
              <Input id="contact-name" name="name" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact-email">Email *</Label>
              <Input id="contact-email" name="email" type="email" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact-phone">Телефон</Label>
              <Input id="contact-phone" name="phone" type="tel" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact-message">Сообщение *</Label>
              <textarea
                id="contact-message"
                name="message"
                required
                rows={4}
                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <div className="relative flex items-start gap-2">
              <input
                id="contact-privacy"
                type="checkbox"
                checked={privacy}
                onChange={(e) => setPrivacy(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-input"
                required
              />
              <Label htmlFor="contact-privacy" className="text-sm leading-snug font-normal">
                Даю согласие на{" "}
                <Link href="/privacy/" className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                  обработку персональных данных
                </Link>{" "}
                *
              </Label>
            </div>
            <Button type="submit" variant="accent" disabled={loading} className="w-full">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Отправить
            </Button>
          </form>
        )}
      </DialogContent>
      ) : null}
    </Dialog>
  );
}
