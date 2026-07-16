export const APPLICATION_PAGES = [
  {
    slug: "crane",
    title: "Крановое оборудование",
    description: "Контакторы КТ и КТП для управления механизмами подъёма и перемещения грузов.",
    categorySlug: "kontaktory-kt",
    href: "/applications/crane/",
    metaTitle: "Контакторы для кранового оборудования — купить у производителя",
  },
  {
    slug: "nku",
    title: "Низковольтные комплектные устройства (НКУ)",
    description: "Аппаратура для силовых щитов, ГРЩ и распределительных устройств.",
    categorySlug: "kontaktory-kt",
    href: "/applications/nku/",
    metaTitle: "Контакторы для НКУ и щитового оборудования",
  },
  {
    slug: "transport",
    title: "Электротранспорт",
    description: "Контакторы КТЭ для троллейбусов, трамваев и городского электротранспорта.",
    categorySlug: "kontaktory-kte",
    href: "/applications/transport/",
    metaTitle: "Контакторы КТЭ для электротранспорта",
  },
  {
    slug: "energy",
    title: "Энергетика",
    description: "Контакторы для распределительных устройств подстанций, ГРЩ и силовых линий.",
    categorySlug: "kontaktory-kt",
    href: "/applications/energy/",
    metaTitle: "Контакторы для энергетики и подстанций",
  },
  {
    slug: "metallurgy",
    title: "Металлургия и горная промышленность",
    description: "Надёжные контакторы для тяжёлых пусков, конвейеров и механизмов металлургических цехов.",
    categorySlug: "kontaktory-kt",
    href: "/applications/metallurgy/",
    metaTitle: "Контакторы для металлургии и горной отрасли",
  },
  {
    slug: "utilities",
    title: "ЖКХ и коммунальная инфраструктура",
    description: "Аппаратура для насосных станций, вентиляции и инженерных систем зданий.",
    categorySlug: "kontaktory-kt",
    href: "/applications/utilities/",
    metaTitle: "Контакторы для ЖКХ и инженерных систем",
  },
  {
    slug: "mining",
    title: "Шахты и карьеры",
    description: "Исполнения для агрессивной среды, частых пусков и длительных циклов работы.",
    categorySlug: "kontaktory-ktp",
    href: "/applications/mining/",
    metaTitle: "Контакторы КТП для шахтного оборудования",
  },
  {
    slug: "elevator",
    title: "Лифты и подъёмники",
    description: "Компактные и надёжные контакторы для лифтового оборудования и малых механизмов.",
    categorySlug: "kontaktory-kt",
    href: "/applications/elevator/",
    metaTitle: "Контакторы для лифтов и подъёмного оборудования",
  },
] as const;

export function getApplicationBySlug(slug: string) {
  return APPLICATION_PAGES.find((p) => p.slug === slug);
}
