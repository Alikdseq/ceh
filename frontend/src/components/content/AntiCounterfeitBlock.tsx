import Link from "next/link";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AntiCounterfeitBlockProps {
  className?: string;
  compact?: boolean;
}

export function AntiCounterfeitBlock({ className, compact }: AntiCounterfeitBlockProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-[var(--color-border)] bg-[var(--color-brand-blue-light)] p-5",
        className,
      )}
    >
      <div className="flex gap-3">
        <AlertTriangle className="h-5 w-5 shrink-0 text-[var(--color-cta)]" aria-hidden />
        <div>
          <p className="font-semibold text-[var(--color-text-primary)]">Остерегайтесь контрафакта</p>
          <p className={cn("mt-1 text-[var(--color-text-secondary)]", compact ? "text-xs" : "text-sm")}>
            Закупайте контакторы только у официального производителя — АО «Электроконтактор»,
            г. Владикавказ. Продукция завода маркируется «Честным знаком», сопровождается
            паспортами и сертификатами. При сомнениях свяжитесь с отделом сбыта.
          </p>
          {!compact && (
            <Button asChild variant="outline" size="sm" className="mt-3">
              <Link href="/contacts">Связаться с производителем</Link>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
