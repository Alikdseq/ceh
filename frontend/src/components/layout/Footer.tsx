"use client";

import Link from "next/link";

import { BrandLogo } from "@/components/layout/BrandLogo";
import { SubscribeForm } from "@/components/home/SubscribeForm";
import { requestOpenCookieSettings } from "@/components/privacy/CookieConsentProvider";

import type { ProductGroup } from "@/lib/types";
import { catalogProductHref } from "@/lib/catalog-url";

interface FooterProps {
  companyName: string;
  address: string;
  email: string;
  phone: string;
  requisites?: string;
  popularProducts?: ProductGroup[];
}

export function Footer({ companyName, address, email, phone, requisites, popularProducts }: FooterProps) {
  return (
    <footer className="mt-auto border-t border-[var(--color-border)] bg-[var(--color-brand-blue-dark)] text-white">
      <div className="container-page grid gap-10 py-12 md:grid-cols-2 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <BrandLogo variant="footer" />
          <p className="mt-4 font-display text-base font-semibold">{companyName}</p>
          <p className="mt-2 text-sm text-white/70">
            Производитель контакторов и низковольтной аппаратуры с 1956 года
          </p>
          {requisites && (
            <p className="mt-3 text-xs text-white/50">{requisites}</p>
          )}
        </div>

        <div className="text-sm">
          <p className="font-semibold">Контакты</p>
          <address className="mt-3 space-y-1 not-italic text-white/70">
            <p>{address}</p>
            <p>
              <a href={`mailto:${email}`} className="hover:text-white">
                {email}
              </a>
            </p>
            <p>
              <a href={`tel:${phone.replace(/\D/g, "")}`} className="hover:text-white">
                {phone}
              </a>
            </p>
          </address>
        </div>

        <div className="text-sm">
          <p className="font-semibold">Разделы</p>
          <ul className="mt-3 space-y-2 text-white/70">
            <li>
              <Link href="/catalog/" className="hover:text-white">
                Каталог продукции
              </Link>
            </li>
            <li>
              <Link href="/about/" className="hover:text-white">
                О заводе
              </Link>
            </li>
            <li>
              <Link href="/news/" className="hover:text-white">
                Новости
              </Link>
            </li>
            <li>
              <Link href="/cases/" className="hover:text-white">
                Кейсы и объекты
              </Link>
            </li>
            <li>
              <Link href="/delivery/" className="hover:text-white">
                Доставка по России
              </Link>
            </li>
            <li>
              <Link href="/privacy/" className="hover:text-white">
                Политика конфиденциальности
              </Link>
            </li>
            <li>
              <Link href="/terms/" className="hover:text-white">
                Пользовательское соглашение
              </Link>
            </li>
            <li>
              <Link href="/cookies/" className="hover:text-white">
                Политика cookie
              </Link>
            </li>
            <li>
              <button
                type="button"
                className="text-left hover:text-white"
                onClick={() => requestOpenCookieSettings()}
              >
                Настройки cookie
              </button>
            </li>
          </ul>
          {popularProducts && popularProducts.length > 0 && (
            <>
              <p className="mt-6 font-semibold">Популярные модели</p>
              <ul className="mt-3 space-y-2 text-white/70">
                {popularProducts.map((p) => (
                  <li key={p.id}>
                    <Link href={catalogProductHref(p)} className="hover:text-white">
                      {p.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div>
          <p className="text-sm font-semibold">Подписка на новости</p>
          <p className="mt-2 text-sm text-white/70">
            Анонсы продукции и обновления прайс-листа
          </p>
          <SubscribeForm variant="footer" />
        </div>
      </div>
      <div className="border-t border-white/10 py-4 text-center text-xs text-white/50">
        © {new Date().getFullYear()} {companyName}
      </div>
    </footer>
  );
}
