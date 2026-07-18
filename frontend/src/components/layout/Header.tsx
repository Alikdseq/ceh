import Link from "next/link";
import { GitCompare, Phone, ShoppingCart } from "lucide-react";

import { BrandLogo } from "@/components/layout/BrandLogo";
import { SearchAutocomplete } from "@/components/layout/SearchAutocomplete";
import { MobileNav } from "@/components/layout/MobileNav";
import { CartBadge } from "@/components/layout/CartBadge";
import { CompareBadge } from "@/components/layout/CompareBadge";
import { Button } from "@/components/ui/button";
import { getSiteSettings } from "@/lib/api";
import { HeaderLeadActions } from "@/components/leads/HeaderLeadActions";
import { NAV_LINKS } from "@/lib/catalog-meta";
import { FACTORY_PHONE, phoneToTelHref } from "@/lib/site-links";

export async function Header() {
  const settings = await getSiteSettings();
  const phone = settings?.phone_main ?? FACTORY_PHONE;
  const telHref = phoneToTelHref(phone);

  return (
    <header className="fixed inset-x-0 top-0 z-50 max-w-[100vw] overflow-visible border-b border-white/10 bg-[var(--color-brand-blue-dark)] text-white shadow-md">
      <div className="container-page min-w-0">
        {/* Верхняя строка: логотип · поиск · действия */}
        <div className="flex min-w-0 items-center gap-1.5 py-2 sm:gap-2 md:gap-3 md:py-2.5">
          <div className="flex min-w-0 shrink-0 items-center gap-1 sm:gap-2">
            <MobileNav phone={phone} telHref={telHref} />
            <BrandLogo variant="header" />
          </div>

          <div className="hidden min-w-0 flex-1 md:block md:max-w-sm lg:max-w-md">
            <SearchAutocomplete className="w-full" />
          </div>

          <div className="ml-auto flex shrink-0 items-center gap-0.5 sm:gap-1">
            <div className="hidden items-center gap-0.5 2xl:flex">
              <HeaderLeadActions />
            </div>

            <Button
              asChild
              variant="ghost"
              size="sm"
              className="h-9 shrink-0 px-2 text-white hover:bg-white/10 hover:text-white lg:px-3"
            >
              <Link href="/compare/" title="Сравнение" className="inline-flex items-center gap-1.5">
                <GitCompare className="h-4 w-4 shrink-0" />
                <span className="hidden lg:inline">Сравнение</span>
                <CompareBadge />
              </Link>
            </Button>

            <Button
              asChild
              variant="ghost"
              size="sm"
              className="h-9 shrink-0 px-2 text-white hover:bg-white/10 hover:text-white lg:px-3"
            >
              <Link href="/cart/" title="Корзина-заявка" className="inline-flex items-center gap-1.5">
                <ShoppingCart className="h-4 w-4 shrink-0" />
                <span className="hidden lg:inline">Заявка</span>
                <CartBadge />
              </Link>
            </Button>

            <Button asChild variant="accent" size="sm" className="h-9 shrink-0 px-2.5 sm:px-3">
              <a href={telHref} title={phone} className="inline-flex items-center gap-1.5">
                <Phone className="h-4 w-4 shrink-0" />
                <span className="hidden whitespace-nowrap xl:inline">{phone}</span>
              </a>
            </Button>
          </div>
        </div>

        {/* Нижняя строка: навигация (от lg) — отдельно, без наложений */}
        <nav
          className="hidden items-center gap-1 border-t border-white/10 py-1 lg:flex"
          aria-label="Основная навигация"
        >
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-white/10 hover:text-[var(--color-cta)]"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
