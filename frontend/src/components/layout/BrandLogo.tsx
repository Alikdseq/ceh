import Image from "next/image";
import Link from "next/link";

import { cn } from "@/lib/utils";

const LOGO_SRC = "/photos/logonobag.png";

interface BrandLogoProps {
  variant?: "header" | "footer";
  className?: string;
  linked?: boolean;
}

export function BrandLogo({ variant = "header", className, linked = true }: BrandLogoProps) {
  const img = (
    <Image
      src={LOGO_SRC}
      alt="Электроконтактор — производитель контакторов"
      width={280}
      height={72}
      priority={variant === "header"}
      unoptimized
      className={cn(
        "w-auto max-w-[min(100%,9rem)] object-contain sm:max-w-none",
        variant === "header" && "h-8 sm:h-10 md:h-12 lg:h-14",
        variant === "footer" && "h-14 sm:h-16 md:h-20",
        className,
      )}
    />
  );

  if (!linked) {
    return (
      <span className="inline-flex min-w-0 shrink items-center gap-1.5 sm:gap-2 md:gap-3">
        {img}
        {variant === "header" && (
          <span className="hidden font-display text-sm font-bold tracking-tight text-white sm:inline md:text-lg lg:text-xl">
            Электроконтактор
          </span>
        )}
      </span>
    );
  }

  return (
    <Link
      href="/"
      className="inline-flex min-w-0 shrink items-center gap-1.5 rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40 sm:gap-2 md:gap-3"
      aria-label="Электроконтактор — на главную"
    >
      {img}
      {variant === "header" && (
        <span className="hidden font-display text-sm font-bold tracking-tight text-white sm:inline md:text-lg lg:text-xl">
          Электроконтактор
        </span>
      )}
    </Link>
  );
}
