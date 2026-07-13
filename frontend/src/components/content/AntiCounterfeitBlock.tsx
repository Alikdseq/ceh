import Link from "next/link";
import Image from "next/image";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { HONEST_SIGN_LOGO_HORIZONTAL } from "@/lib/honest-sign";
import { cn, publicAssetSrc } from "@/lib/utils";

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
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        <Image
          src={publicAssetSrc(HONEST_SIGN_LOGO_HORIZONTAL)}
          alt="Честный знак — партнёр оператора маркировки"
          width={240}
          height={120}
          unoptimized
          className={cn(
            "mx-auto h-auto w-full max-w-[200px] shrink-0 object-contain sm:mx-0",
            compact && "max-w-[160px]",
          )}
        />
        <div className="flex min-w-0 gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[var(--color-cta)] sm:hidden" aria-hidden />
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
    </div>
  );
}
