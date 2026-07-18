"use client";

import Link from "next/link";
import { GitCompare, Menu, Phone, ShoppingCart } from "lucide-react";

import { BrandLogo } from "@/components/layout/BrandLogo";
import { SearchAutocomplete } from "@/components/layout/SearchAutocomplete";
import { HeaderLeadActions } from "@/components/leads/HeaderLeadActions";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTrigger,
} from "@/components/ui/sheet";
import { NAV_LINKS } from "@/lib/catalog-meta";

interface MobileNavProps {
  phone: string;
  telHref: string;
}

export function MobileNav({ phone, telHref }: MobileNavProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 shrink-0 text-white hover:bg-white/10 hover:text-white lg:hidden"
          aria-label="Открыть меню"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="flex w-[min(100vw-2rem,320px)] flex-col gap-0 p-0">
        <SheetHeader className="shrink-0 space-y-0 border-b px-5 pb-4 pt-5 pr-14">
          <BrandLogo variant="footer" className="h-10 sm:h-11" linked={false} />
        </SheetHeader>
        <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-5 pb-6 pt-4" aria-label="Мобильная навигация">
          <SearchAutocomplete
            className="mb-5"
            variant="default"
            submitLayout="aside"
            placeholder="Поиск по артикулу…"
          />
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-md px-3 py-2.5 text-base font-medium hover:bg-muted"
            >
              {link.label}
            </Link>
          ))}
          <Link
            href="/compare/"
            className="flex items-center gap-2 rounded-md px-3 py-2.5 text-base font-medium hover:bg-muted"
          >
            <GitCompare className="h-4 w-4" />
            Сравнение
          </Link>
          <div className="mt-4 flex flex-col gap-2 border-t pt-4 2xl:hidden">
            <HeaderLeadActions mobile />
          </div>
          <Link
            href="/cart/"
            className="mt-2 flex items-center gap-2 rounded-md bg-primary px-3 py-2.5 text-sm font-medium text-primary-foreground"
          >
            <ShoppingCart className="h-4 w-4" />
            Корзина-заявка
          </Link>
          <Button asChild variant="accent" className="mt-3 w-full gap-2">
            <a href={telHref}>
              <Phone className="h-4 w-4" />
              {phone}
            </a>
          </Button>
        </nav>
      </SheetContent>
    </Sheet>
  );
}
