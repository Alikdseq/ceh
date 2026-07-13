import Image from "next/image";

import { HONEST_SIGN_LOGO_COMPACT } from "@/lib/honest-sign";
import { cn, publicAssetSrc } from "@/lib/utils";

const SIZE_CLASS = {
  xs: "h-8 w-6",
  sm: "h-10 w-8",
  md: "h-14 w-11",
  lg: "h-[72px] w-14",
} as const;

interface HonestSignMarkProps {
  className?: string;
  size?: keyof typeof SIZE_CLASS;
  title?: string;
}

export function HonestSignMark({
  className,
  size = "sm",
  title = "Маркировка «Честный знак»",
}: HonestSignMarkProps) {
  return (
    <span
      className={cn("inline-flex shrink-0", className)}
      title={title}
      aria-label={title}
      role="img"
    >
      <Image
        src={publicAssetSrc(HONEST_SIGN_LOGO_COMPACT)}
        alt=""
        width={32}
        height={40}
        unoptimized
        className={cn("object-contain drop-shadow-sm", SIZE_CLASS[size])}
      />
    </span>
  );
}
