"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { subscribeNewsletter } from "@/lib/api/newsletter";
import { ApiError } from "@/lib/api/client";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface SubscribeFormProps {
  variant?: "footer" | "inline" | "sidebar";
  className?: string;
}

export function SubscribeForm({ variant = "inline", className }: SubscribeFormProps) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "already" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [marketingAccepted, setMarketingAccepted] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    if (!marketingAccepted) {
      setStatus("error");
      setError("Для подписки необходимо согласие на получение рассылки и обработку персональных данных");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await subscribeNewsletter(email.trim(), name.trim(), true, "2026-07-07");
      setStatus(result === "already_subscribed" ? "already" : "success");
      setEmail("");
      setName("");
      setMarketingAccepted(false);
    } catch (err) {
      setStatus("error");
      setError(err instanceof ApiError ? err.message : "Не удалось подписаться");
    } finally {
      setLoading(false);
    }
  }

  if (status === "success") {
    return (
      <p className={cn("mt-3 text-sm text-emerald-400", className)} role="status">
        Проверьте почту — мы отправили ссылку для подтверждения подписки.
      </p>
    );
  }

  if (status === "already") {
    return (
      <p className={cn("mt-3 text-sm text-emerald-400", className)} role="status">
        Этот адрес уже подписан на новости завода.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className={cn("mt-3 space-y-2", className)}>
      {variant === "sidebar" && (
        <Input
          type="text"
          placeholder="Имя (необязательно)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      )}
      <div className="flex gap-2">
        <Input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={cn(
            variant === "footer" && "border-white/20 bg-white/10 text-white placeholder:text-white/50",
          )}
          aria-label="Email для подписки"
        />
        <Button
          type="submit"
          variant={variant === "footer" ? "accent" : "default"}
          size="sm"
          disabled={loading}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "OK"}
        </Button>
      </div>
      <label className={cn("flex items-start gap-2 text-xs", variant === "footer" ? "text-white/70" : "text-muted-foreground")}>
        <input
          type="checkbox"
          checked={marketingAccepted}
          onChange={(e) => setMarketingAccepted(e.target.checked)}
          className="mt-0.5 h-4 w-4 rounded border-input"
          required
        />
        <span className="leading-snug">
          Даю согласие на получение новостей и{" "}
          <Link href="/privacy/" className={cn("underline underline-offset-2", variant === "footer" ? "text-white" : "text-primary")}>
            обработку персональных данных
          </Link>
          .
        </span>
      </label>
      {status === "error" && error && (
        <p className="text-xs text-red-400">{error}</p>
      )}
    </form>
  );
}
