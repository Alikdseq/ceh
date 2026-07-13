"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { submitQuote } from "@/lib/api/quotes";
import { ApiError } from "@/lib/api/client";
import { cn } from "@/lib/utils";

type CustomerType = "individual" | "company";

interface QuoteFormProps {
  disabled?: boolean;
}

export function QuoteForm({ disabled }: QuoteFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [customerType, setCustomerType] = useState<CustomerType>("company");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [privacy, setPrivacy] = useState(false);
  const privacyPolicyVersion = "2026-07-07";

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const form = new FormData(e.currentTarget);

    if (!privacy) {
      setError("Необходимо согласие на обработку персональных данных");
      return;
    }

    setLoading(true);
    try {
      const isIndividual = customerType === "individual";
      const result = await submitQuote({
        contact_name: String(form.get("contact_name")),
        company_name: isIndividual ? "Физическое лицо" : String(form.get("company_name")),
        email: String(form.get("email")),
        phone: String(form.get("phone")),
        city: isIndividual ? "" : String(form.get("city") || ""),
        inn: String(form.get("inn") || ""),
        kpp: isIndividual ? "" : String(form.get("kpp") || ""),
        comment: String(form.get("comment") || ""),
        privacy_accepted: true,
        privacy_policy_version: privacyPolicyVersion,
        website: String(form.get("website") || ""),
        utm_source: searchParams.get("utm_source") || "",
        utm_medium: searchParams.get("utm_medium") || "",
        utm_campaign: searchParams.get("utm_campaign") || "",
      });
      router.push(`/order/success?number=${encodeURIComponent(result.number)}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось отправить заявку. Попробуйте позже.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          size="sm"
          variant={customerType === "individual" ? "default" : "outline"}
          className={cn("flex-1 sm:flex-none")}
          onClick={() => setCustomerType("individual")}
        >
          Физическое лицо
        </Button>
        <Button
          type="button"
          size="sm"
          variant={customerType === "company" ? "default" : "outline"}
          className={cn("flex-1 sm:flex-none")}
          onClick={() => setCustomerType("company")}
        >
          Юридическое лицо
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="contact_name">ФИО *</Label>
          <Input id="contact_name" name="contact_name" required autoComplete="name" />
        </div>

        {customerType === "individual" && (
          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="inn">ИНН</Label>
            <Input id="inn" name="inn" inputMode="numeric" pattern="[0-9]{10}|[0-9]{12}" placeholder="10 или 12 цифр" />
          </div>
        )}

        {customerType === "company" && (
          <>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="company_name">Компания *</Label>
              <Input id="company_name" name="company_name" required autoComplete="organization" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="city">Город</Label>
              <Input id="city" name="city" autoComplete="address-level2" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="inn_company">ИНН</Label>
              <Input id="inn_company" name="inn" inputMode="numeric" pattern="[0-9]{10}|[0-9]{12}" />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="kpp">КПП</Label>
              <Input id="kpp" name="kpp" inputMode="numeric" pattern="[0-9]{9}" />
            </div>
          </>
        )}

        <div className="space-y-2">
          <Label htmlFor="email">Email *</Label>
          <Input id="email" name="email" type="email" required autoComplete="email" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="phone">Телефон *</Label>
          <Input id="phone" name="phone" type="tel" required placeholder="+7 (999) 123-45-67" />
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="comment">Комментарий</Label>
          <textarea
            id="comment"
            name="comment"
            rows={3}
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
      </div>

      <div className="absolute -left-[9999px]" aria-hidden>
        <Label htmlFor="website">Website</Label>
        <Input id="website" name="website" tabIndex={-1} autoComplete="off" />
      </div>

      <div className="relative flex items-start gap-2">
        <input
          id="privacy"
          type="checkbox"
          checked={privacy}
          onChange={(e) => setPrivacy(e.target.checked)}
          className="mt-1 h-4 w-4 rounded border-input"
          required
        />
        <Label htmlFor="privacy" className="text-sm leading-snug font-normal">
          Даю согласие на{" "}
          <Link href="/privacy" className="text-primary hover:underline">
            обработку персональных данных
          </Link>{" "}
          *
        </Label>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Button type="submit" size="lg" variant="accent" className="w-full sm:w-auto" disabled={disabled || loading}>
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Отправить заявку
      </Button>
    </form>
  );
}
