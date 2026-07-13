import type { LucideIcon } from "lucide-react";
import {
  Bus,
  Cable,
  Grid3X3,
  Package,
  ToggleLeft,
  Zap,
} from "lucide-react";

export interface CategoryMeta {
  icon: LucideIcon;
  color: string;
  description?: string;
  /** Product photo for category card (replaces icon when set) */
  image?: string;
}

const CATEGORY_META: Record<string, CategoryMeta> = {
  "kontaktory-kt": {
    icon: Zap,
    color: "bg-[var(--color-brand-blue-light)] text-[var(--color-brand-blue)]",
    description: "КТ 6000, 6600, 7200 — переменный ток",
    image: "/photos/КТ6033(2)-fotor-bg-remover-20260706185032.png",
  },
  "kontaktory-ktp": {
    icon: Cable,
    color: "bg-[var(--color-brand-blue-light)] text-[var(--color-brand-blue-dark)]",
    description: "Контакторы постоянного тока",
    image: "/photos/КТП6032-fotor-bg-remover-20260706185239.png",
  },
  "kontaktory-kte": {
    icon: Bus,
    color: "bg-[#e8f5ee] text-[var(--color-success)]",
    description: "Для троллейбуса и трамвая",
  },
  vyklyuchateli: {
    icon: ToggleLeft,
    color: "bg-[var(--color-bg-light)] text-[var(--color-text-secondary)]",
    description: "Путевые и силовые выключатели",
  },
  "kulachkovye-elementy": {
    icon: Grid3X3,
    color: "bg-[var(--color-brand-blue-light)] text-[var(--color-brand-blue)]",
    description: "КЭ и ЭУ серии",
    image: "/photos/КЭ.png",
  },
  "paketnye-pereklyuchateli": {
    icon: Grid3X3,
    color: "bg-[var(--color-bg-light)] text-[var(--color-text-primary)]",
    description: "ПВП 17-29, 17-31",
    image: "/photos/Пакет перекл.png",
  },
};

export function getCategoryMeta(slug: string): CategoryMeta {
  return (
    CATEGORY_META[slug] ?? {
      icon: Package,
      color: "bg-[var(--color-bg-light)] text-[var(--color-text-secondary)]",
    }
  );
}

export const NAV_LINKS = [
  { href: "/catalog", label: "Каталог" },
  { href: "/pricelist", label: "Прайс-лист" },
  { href: "/about", label: "О заводе" },
  { href: "/partners", label: "Партнёры" },
  { href: "/shareholders", label: "Акционерам" },
  { href: "/news", label: "Новости" },
  { href: "/contacts", label: "Контакты" },
] as const;

export const SERIES_BLOCKS = [
  {
    title: "КТ 6000",
    description: "80–630 А, исполнения Б и БС",
    href: "/catalog/kontaktory-kt/kt-6000b",
  },
  {
    title: "КТ 6600",
    description: "100–1000 А, исполнение С",
    href: "/catalog/kontaktory-kt/kt-6600s",
  },
  {
    title: "КТП",
    description: "Контакторы постоянного тока",
    href: "/catalog/kontaktory-ktp",
  },
  {
    title: "КТЭ",
    description: "Электротранспорт",
    href: "/catalog/kontaktory-kte",
  },
] as const;
