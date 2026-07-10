import Link from "next/link";

import { ProductCard } from "@/components/catalog/ProductCard";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import type { FAQItem, ProductGroup } from "@/lib/types";

interface ProductRelatedProps {
  related: ProductGroup[];
  accessories: ProductGroup[];
  categoryPathMap: (slug: string) => string[];
}

export function ProductRelated({ related, accessories, categoryPathMap }: ProductRelatedProps) {
  if (related.length === 0 && accessories.length === 0) return null;

  return (
    <div className="mt-16 space-y-12">
      {related.length > 0 && (
        <section aria-labelledby="related-heading">
          <h2 id="related-heading" className="font-display text-2xl font-bold">
            Похожие товары
          </h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {related.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                categoryPath={categoryPathMap(p.category_slug)}
              />
            ))}
          </div>
        </section>
      )}

      {accessories.length > 0 && (
        <section aria-labelledby="accessories-heading">
          <div className="flex items-end justify-between gap-4">
            <h2 id="accessories-heading" className="font-display text-2xl font-bold">
              Аксессуары
            </h2>
            <Link href="/catalog/aksessuary-kontaktorov" className="text-sm text-primary hover:underline">
              Все аксессуары
            </Link>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {accessories.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                categoryPath={categoryPathMap(p.category_slug)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

const DEFAULT_FAQ: FAQItem[] = [
  {
    id: 1,
    category: "products",
    question: "Как выбрать напряжение катушки?",
    answer: "Напряжение катушки должно соответствовать напряжению цепи управления вашей схемы.",
    sort_order: 1,
  },
  {
    id: 2,
    category: "products",
    question: "Чем отличаются исполнения Б и БС?",
    answer: "Исполнение Б — базовое, БС — с расширенной комплектацией вспомогательными контактами.",
    sort_order: 2,
  },
  {
    id: 3,
    category: "products",
    question: "Есть ли маркировка «Честный знак»?",
    answer: "Контакторы серии КТ внесены в систему обязательной маркировки «Честный знак».",
    sort_order: 3,
  },
];

export function ProductFAQ({ items }: { items: FAQItem[] }) {
  const faq = items.length > 0 ? items.slice(0, 5) : DEFAULT_FAQ;

  return (
    <section className="mt-16" aria-labelledby="faq-heading">
      <h2 id="faq-heading" className="font-display text-2xl font-bold">
        Частые вопросы
      </h2>
      <Accordion type="single" collapsible className="mt-4">
        {faq.map((item) => (
          <AccordionItem key={item.id} value={`faq-${item.id}`}>
            <AccordionTrigger>{item.question}</AccordionTrigger>
            <AccordionContent>{item.answer}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  );
}
