"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";

import { confirmNewsletter } from "@/lib/api/newsletter";

export default function ConfirmSubscribePage() {
  const params = useParams<{ token: string }>();
  const [state, setState] = useState<"loading" | "ok" | "error">("loading");

  useEffect(() => {
    if (!params.token) return;
    confirmNewsletter(params.token)
      .then(() => setState("ok"))
      .catch(() => setState("error"));
  }, [params.token]);

  return (
    <div className="section-py container-page max-w-lg text-center">
      {state === "loading" && <Loader2 className="mx-auto h-8 w-8 animate-spin" />}
      {state === "ok" && (
        <>
          <h1 className="font-display text-2xl font-bold">Подписка подтверждена</h1>
          <p className="mt-3 text-muted-foreground">Спасибо! Вы будете получать новости завода.</p>
          <Link href="/news/" className="mt-6 inline-block text-primary hover:underline">
            Перейти к новостям
          </Link>
        </>
      )}
      {state === "error" && (
        <>
          <h1 className="font-display text-2xl font-bold">Ссылка недействительна</h1>
          <p className="mt-3 text-muted-foreground">Возможно, подписка уже подтверждена или ссылка устарела.</p>
        </>
      )}
    </div>
  );
}
