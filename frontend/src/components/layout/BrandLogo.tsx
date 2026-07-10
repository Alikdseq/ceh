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
        "w-auto object-contain",
        variant === "header" && "h-10 sm:h-12 md:h-14",
        variant === "footer" && "h-14 sm:h-16 md:h-20",
        className,
      )}
    />
  );

  if (!linked) {
    return (
      <span className="inline-flex shrink-0 items-center gap-2 sm:gap-3">
        {img}
        {variant === "header" && (
          <span className="font-display text-base font-bold tracking-tight text-white sm:text-lg md:text-xl">
            Электроконтактор
          </span>
        )}
      </span>
    );
  }

  return (
    <Link
      href="/"
      className="inline-flex shrink-0 items-center gap-2 rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/40 sm:gap-3"
      aria-label="Электроконтактор — на главную"
    >
      {img}
      {variant === "header" && (
        <span className="font-display text-base font-bold tracking-tight text-white sm:text-lg md:text-xl">
          Электроконтактор
        </span>
      )}
    </Link>
  );
}
