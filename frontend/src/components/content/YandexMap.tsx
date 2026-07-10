interface YandexMapProps {
  address: string;
  className?: string;
  heightClassName?: string;
}

/** Yandex Maps iframe — coordinates for Kabardinskaya 8, Vladikavkaz */
export function YandexMap({
  address,
  className,
  heightClassName = "h-[420px] sm:h-[480px] lg:h-[560px]",
}: YandexMapProps) {
  const query = encodeURIComponent(address);
  const src = `https://yandex.ru/map-widget/v1/?text=${query}&z=16`;

  return (
    <div className={className}>
      <iframe
        title="Карта — расположение завода"
        src={src}
        className={`w-full rounded-lg border ${heightClassName}`}
        loading="lazy"
        allowFullScreen
      />
    </div>
  );
}
