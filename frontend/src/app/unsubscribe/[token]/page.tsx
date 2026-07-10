"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";

import { unsubscribeNewsletter } from "@/lib/api/newsletter";

export default function UnsubscribePage() {
  const params = useParams<{ token: string }>();
  const [state, setState] = useState<"loading" | "ok" | "error">("loading");

  useEffect(() => {
    if (!params.token) return;
    unsubscribeNewsletter(params.token)
      .then(() => setState("ok"))
      .catch(() => setState("error"));
  }, [params.token]);

  return (
    <div className="section-py container-page max-w-lg text-center">
      {state === "loading" && <Loader2 className="mx-auto h-8 w-8 animate-spin" />}
      {state === "ok" && (
        <>
          <h1 className="font-display text-2xl font-bold">Вы отписаны</h1>
          <p className="mt-3 text-muted-foreground">Мы больше не будем отправлять вам рассылку.</p>
        </>
      )}
      {state === "error" && (
        <p className="text-muted-foreground">Ссылка отписки недействительна.</p>
      )}
    </div>
  );
}
