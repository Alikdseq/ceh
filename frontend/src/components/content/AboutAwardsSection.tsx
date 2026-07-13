import Image from "next/image";

import { FACTORY_AWARDS } from "@/lib/awards";
import { cn, publicAssetSrc } from "@/lib/utils";

export function AboutAwardsSection({ className }: { className?: string }) {
  return (
    <section id="awards" className={cn("scroll-mt-28", className)} aria-labelledby="awards-heading">
      <div className="rounded-xl border bg-gradient-to-br from-[var(--color-brand-blue-light)]/60 to-card p-6 md:p-8">
        <h2
          id="awards-heading"
          className="font-display text-2xl font-bold text-[var(--color-brand-blue-dark)] md:text-3xl"
        >
          Награды
        </h2>
        <p className="mt-3 max-w-3xl text-muted-foreground">
          Достижения и признание продукции завода на всероссийских конкурсах, отраслевых выставках и
          в работе с партнёрами.
        </p>
      </div>

      <ul className="mt-6 space-y-5">
        {FACTORY_AWARDS.map((award, index) => (
          <li
            key={award.id}
            className="group relative overflow-hidden rounded-xl border border-[var(--color-border)] bg-card shadow-sm transition-shadow hover:shadow-md"
          >
            <div
              className="absolute inset-y-0 left-0 w-1 bg-[var(--color-brand-blue)] opacity-80 transition-opacity group-hover:opacity-100"
              aria-hidden
            />
            <div className="flex flex-col gap-0 sm:flex-row">
              <div className="relative w-full shrink-0 border-b bg-gradient-to-br from-[var(--color-brand-blue-light)]/40 to-muted sm:w-[220px] sm:border-b-0 sm:border-r md:w-[260px] lg:w-[280px]">
                <div className="relative mx-auto aspect-[3/4] w-full max-w-[280px] p-3 sm:max-w-none sm:p-4">
                  <Image
                    src={publicAssetSrc(award.image)}
                    alt={award.title}
                    fill
                    className="object-contain drop-shadow-sm"
                    sizes="(max-width: 640px) 100vw, 280px"
                    priority={index < 2}
                    unoptimized
                  />
                </div>
              </div>
              <div className="flex min-w-0 flex-1 flex-col justify-center px-5 py-5 sm:px-6 sm:py-6">
                <p className="text-xs font-semibold uppercase tracking-wide text-[var(--color-brand-blue)]">
                  {award.label}
                </p>
                <h3 className="mt-2 font-display text-lg font-bold text-[var(--color-brand-blue-dark)] md:text-xl">
                  {award.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground md:text-base">
                  {award.description}
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
