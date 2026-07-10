import type { Metadata } from "next";

import { PriceListPageShell, PriceListTable } from "@/components/pricelist/PriceListPageClient";

export const metadata: Metadata = {
  title: "Прайс-лист | Электроконтактор",
  description:
    "Актуальный прайс-лист на контакторы КТ, КТП, КТЭ и комплектующие от производителя АО «Электроконтактор».",
};

export default function PriceListPage() {
  return (
    <PriceListPageShell>
      <PriceListTable />
    </PriceListPageShell>
  );
}
