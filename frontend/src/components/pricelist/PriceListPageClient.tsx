import Link from "next/link";
import { Download, FileText } from "lucide-react";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { getPriceList, getPriceListPdfUrl } from "@/lib/api";
import { formatPrice } from "@/lib/utils";

export async function PriceListTable() {
  const sections = await getPriceList();

  if (!sections.length) {
    return (
      <p className="rounded-lg border bg-muted/40 p-6 text-muted-foreground">
        Прайс-лист пока не опубликован. Обратитесь в отдел сбыта.
      </p>
    );
  }

  return (
    <div className="space-y-10">
      {sections.map((section) => (
        <section key={section.id} aria-labelledby={`pricelist-section-${section.id}`}>
          <h2
            id={`pricelist-section-${section.id}`}
            className="font-display text-xl font-semibold text-[var(--color-brand-blue-dark)] md:text-2xl"
          >
            {section.name}
          </h2>
          <div className="mt-4 overflow-x-auto rounded-xl border bg-card shadow-sm">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-[var(--color-brand-blue-dark)] text-left text-white">
                  <th className="px-4 py-3 font-medium">Наименование</th>
                  <th className="px-4 py-3 font-medium whitespace-nowrap">Ток, А</th>
                  <th className="px-4 py-3 font-medium">Примечание</th>
                  <th className="px-4 py-3 text-right font-medium whitespace-nowrap">Без НДС</th>
                  <th className="px-4 py-3 text-right font-medium whitespace-nowrap">С НДС</th>
                </tr>
              </thead>
              <tbody>
                {section.items.map((item, index) => (
                  <tr
                    key={item.id}
                    className={index % 2 === 0 ? "bg-background" : "bg-[var(--color-brand-blue-light)]/35"}
                  >
                    <td className="px-4 py-3 font-medium">{item.name}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {item.nominal_current_a ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{item.notes || "—"}</td>
                    <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">
                      {formatPrice(item.price_without_vat)}
                    </td>
                    <td className="px-4 py-3 text-right font-semibold tabular-nums">
                      {formatPrice(item.price)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </div>
  );
}

export function PriceListDownloadButton() {
  return (
    <Button asChild variant="accent" className="gap-2">
      <a href={getPriceListPdfUrl()} download>
        <Download className="h-4 w-4" />
        Скачать PDF
      </a>
    </Button>
  );
}

export function PriceListPageShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="section-py">
      <div className="container-page">
        <Breadcrumbs
          items={[
            { label: "Главная", href: "/" },
            { label: "Прайс-лист", href: "/pricelist" },
          ]}
          className="mb-6"
        />
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-[var(--color-brand-blue-light)] px-3 py-1 text-sm font-medium text-[var(--color-brand-blue-dark)]">
              <FileText className="h-4 w-4" />
              Актуальные цены завода
            </div>
            <h1 className="font-display text-3xl font-bold md:text-4xl">Прайс-лист</h1>
            <p className="mt-3 max-w-2xl text-muted-foreground">
              Оптовые цены на контакторы, выключатели и комплектующие АО «Электроконтактор».
              Цены указаны с НДС и не являются публичной офертой.
            </p>
          </div>
          <PriceListDownloadButton />
        </div>
        <div className="mt-10">{children}</div>
        <p className="mt-8 text-sm text-muted-foreground">
          Для уточнения условий поставки и скидок обращайтесь в{" "}
          <Link href="/contacts/" className="text-primary hover:underline">
            отдел сбыта
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
