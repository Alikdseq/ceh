import Image from "next/image";
import Link from "next/link";
import { CheckCircle2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { HONEST_SIGN_DESCRIPTION, HONEST_SIGN_LOGO_PARTNER } from "@/lib/honest-sign";
import { cn, publicAssetSrc } from "@/lib/utils";

const HIGHLIGHTS = [
  "Уникальный код Data Matrix на каждой единице",
  "Прослеживаемость от завода до покупателя",
  "Защита от контрафакта и серого импорта",
] as const;

export function HonestSignSection({ className }: { className?: string }) {
  return (
    <section
      className={cn(
        "border-y border-[#53565A]/15 bg-gradient-to-r from-[#FAFF00]/20 via-[#FAFF00]/10 to-background",
        className,
      )}
      aria-labelledby="honest-sign-heading"
    >
      <div className="container-page grid items-center gap-8 py-10 md:grid-cols-[minmax(0,280px)_1fr] md:gap-10 lg:py-12">
        <div className="mx-auto w-full max-w-[280px] md:mx-0">
          <Image
            src={publicAssetSrc(HONEST_SIGN_LOGO_PARTNER)}
            alt="Партнёр оператора маркировки «Честный знак»"
            width={560}
            height={320}
            unoptimized
            className="h-auto w-full rounded-xl object-contain drop-shadow-md"
            priority
          />
        </div>

        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--color-brand-blue)]">
            Национальная система маркировки
          </p>
          <h2
            id="honest-sign-heading"
            className="mt-2 font-display text-2xl font-bold text-[var(--color-brand-blue-dark)] md:text-3xl"
          >
            Работаем с «Честным знаком»
          </h2>
          <p className="mt-4 max-w-2xl text-muted-foreground md:text-base">{HONEST_SIGN_DESCRIPTION}</p>

          <ul className="mt-5 space-y-2">
            {HIGHLIGHTS.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm md:text-base">
                <CheckCircle2
                  className="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-brand-blue)]"
                  aria-hidden
                />
                <span>{item}</span>
              </li>
            ))}
          </ul>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild variant="default">
              <Link href="/catalog/">Каталог с маркировкой</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="https://честныйзнак.рф/" target="_blank" rel="noopener noreferrer">
                О системе «Честный знак»
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
