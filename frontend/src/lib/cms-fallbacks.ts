import type { ContentPage } from "@/lib/types";

/** Fallback CMS pages when API has no seed data (e.g. fresh deploy before loaddata). */
export const CMS_PAGE_FALLBACKS: Record<string, ContentPage> = {
  about: {
    title: "О заводе",
    slug: "about",
    body: "<p>АО «Владикавказский завод «Электроконтактор»» — ведущий российский производитель контакторов серий КТ, КТП, КТЭ с <strong>1956 года</strong>.</p><p>Завод расположен во Владикавказе и поставляет продукцию по всей России и странам СНГ.</p>",
    meta_title: "О заводе Электроконтактор | Производитель контакторов КТ",
    meta_description:
      "История и возможности АО «Электроконтактор» — производителя контакторов КТ, КТП, КТЭ во Владикавказе.",
    h1: "О заводе «Электроконтактор»",
    updated_at: "2026-01-01T12:00:00Z",
  },
  contacts: {
    title: "Контакты",
    slug: "contacts",
    body: "<p><strong>Адрес:</strong> 362003, г. Владикавказ, ул. Кабардинская, 8</p><p><strong>Телефон:</strong> (8672) 53-33-44</p><p><strong>Email:</strong> info@ekontaktor.ru</p>",
    meta_title: "Контакты Электроконтактор",
    meta_description: "Контактная информация АО «Электроконтактор».",
    h1: "Контакты",
    updated_at: "2026-01-01T12:00:00Z",
  },
  "about-production": {
    title: "Производство",
    slug: "about-production",
    body: "<p>Полный цикл производства контакторов на площадке во Владикавказе: механическая обработка, сборка, испытания и маркировка «Честный знак».</p>",
    meta_title: "Производство | Электроконтактор",
    meta_description: "Производственные мощности АО «Электроконтактор» во Владикавказе.",
    h1: "Производство",
    updated_at: "2026-01-01T12:00:00Z",
  },
  "about-certificates": {
    title: "Сертификаты",
    slug: "about-certificates",
    body: "<p>Завод имеет сертификаты соответствия EAC на выпускаемую продукцию.</p>",
    meta_title: "Сертификаты | Электроконтактор",
    meta_description: "Сертификаты и декларации соответствия продукции Электроконтактор.",
    h1: "Сертификаты завода",
    updated_at: "2026-01-01T12:00:00Z",
  },
  support: {
    title: "Поддержка",
    slug: "support",
    body: "<p>Ответы на частые вопросы по подбору, заказу и документации на контакторы.</p>",
    meta_title: "Поддержка | Электроконтактор",
    meta_description: "FAQ и помощь по продукции Электроконтактор.",
    h1: "Поддержка",
    updated_at: "2026-01-01T12:00:00Z",
  },
};

export function getCmsPageFallback(slug: string): ContentPage | null {
  return CMS_PAGE_FALLBACKS[slug] ?? null;
}
