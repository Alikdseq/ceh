import type { Metadata } from "next";

import { PartnersCarousel } from "@/components/home/PartnersCarousel";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { PARTNERS } from "@/lib/partners";

export const metadata: Metadata = {
  title: "Партнёры | Электроконтактор",
  description:
    "Официальные партнёры и дилеры АО «Электроконтактор» — поставки контакторов КТ, КТП, КТЭ по России.",
};

export default function PartnersPage() {
  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Партнёры", href: "/partners" },
          ]}
          className="mb-6"
        />
        <h1 className="font-display text-3xl font-bold md:text-4xl">Партнёры</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Компании, с которыми завод сотрудничает в сфере поставок и дистрибуции низковольтной
          аппаратуры. Для уточнения условий сотрудничества обращайтесь в отдел сбыта производителя.
        </p>

        <div className="mt-10 rounded-xl border bg-muted/30 p-6 md:p-8">
          <PartnersCarousel partners={PARTNERS} />
        </div>

        <p className="mt-8 text-sm text-muted-foreground">
          Всего партнёров: {PARTNERS.length}. Если вы представляете компанию из списка и хотите
          обновить реквизиты — напишите на{" "}
          <a href="mailto:info@ekontaktor.ru" className="text-primary underline-offset-4 hover:underline">
            info@ekontaktor.ru
          </a>
          .
        </p>
      </div>
    </div>
  );
}
