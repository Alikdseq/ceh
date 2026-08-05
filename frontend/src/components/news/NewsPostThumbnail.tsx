import Image from "next/image";

import { cn, normalizeMediaUrl } from "@/lib/utils";

interface NewsPostThumbnailProps {
  src: string;
  alt: string;
  className?: string;
  sizes?: string;
  priority?: boolean;
}

export function NewsPostThumbnail({
  src,
  alt,
  className,
  sizes = "(max-width:768px) 100vw, 320px",
  priority = false,
}: NewsPostThumbnailProps) {
  const imageSrc = normalizeMediaUrl(src);

  return (
    <div className={cn("relative overflow-hidden rounded-md bg-muted", className)}>
      <Image
        src={imageSrc}
        alt={alt}
        fill
        priority={priority}
        unoptimized
        className="object-cover"
        sizes={sizes}
      />
    </div>
  );
}
