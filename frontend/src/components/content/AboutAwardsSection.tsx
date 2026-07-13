import Image from "next/image";
import { Award } from "lucide-react";

import { FACTORY_AWARDS } from "@/lib/awards";
import { cn } from "@/lib/utils";

export function AboutAwardsSection({ className }: { className?: string }) {
  return (
    <section id="awards" className={cn("scroll-mt-28", className)} aria-labelledby="awards-heading">
      <h2 id="awards-heading" className="font-display text-2xl font-bold md:text-3xl">
        Награды
      </h2>
      <p className="mt-3 max-w-3xl text-muted-foreground">
        Достижения и признание продукции завода на всероссийских конкурсах и в отраслевых
        ассоциациях.
      </p>

      <ul className="mt-8 space-y-6">
        {FACTORY_AWARDS.map((award) => (
          <li
            key={award.id}
            className="flex flex-col gap-4 rounded-xl border bg-card p-4 shadow-sm sm:flex-row sm:items-start sm:p-5"
          >
            <div className="relative mx-auto aspect-[4/3] w-full max-w-[220px] shrink-0 overflow-hidden rounded-lg border bg-muted sm:mx-0">
              {award.image ? (
                <Image
                  src={award.image}
                  alt=""
                  fill
                  className="object-contain p-2"
                  sizes="220px"
                />
              ) : (
                <div className="flex h-full min-h-[140px] items-center justify-center text-muted-foreground">
                  <Award className="h-10 w-10 opacity-40" aria-hidden />
                  <span className="sr-only">Изображение награды будет добавлено</span>
                </div>
              )}
            </div>
            <p className="min-w-0 flex-1 text-sm leading-relaxed text-foreground sm:text-base">
              {award.title}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
