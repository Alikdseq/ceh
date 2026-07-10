export const APPLICATION_PAGES = [
  {
    slug: "crane",
    title: "Крановое оборудование",
    description: "Контакторы КТ и КТП для управления механизмами подъёма и перемещения грузов.",
    categorySlug: "kontaktory-kt",
    href: "/applications/crane",
    metaTitle: "Контакторы для кранового оборудования",
  },
  {
    slug: "nku",
    title: "Низковольтные комплектные устройства (НКУ)",
    description: "Аппаратура для силовых щитов, ГРЩ и распределительных устройств.",
    categorySlug: "kontaktory-kt",
    href: "/applications/nku",
    metaTitle: "Контакторы для НКУ",
  },
  {
    slug: "transport",
    title: "Электротранспорт",
    description: "Контакторы КТЭ для троллейбусов, трамваев и городского электротранспорта.",
    categorySlug: "kontaktory-kte",
    href: "/applications/transport",
    metaTitle: "Контакторы для электротранспорта",
  },
] as const;

export function getApplicationBySlug(slug: string) {
  return APPLICATION_PAGES.find((p) => p.slug === slug);
}
