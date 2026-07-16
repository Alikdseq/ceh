import type { FAQItem } from "@/lib/types";
import { productImageSrc } from "@/lib/utils";

const DEFAULT_SITE_URL = "https://ekontaktor.ru";

function siteUrl(): string {
  return (process.env.NEXT_PUBLIC_SITE_URL ?? DEFAULT_SITE_URL).replace(/\/$/, "");
}

export function buildOrganizationSchema(settings?: {
  company_name?: string;
  phone_main?: string;
  email_main?: string;
  address?: string;
}) {
  const base = siteUrl();
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: settings?.company_name ?? 'АО «Электроконтактор»',
    url: base,
    logo: `${base}/photos/kt.png`,
    telephone: settings?.phone_main,
    email: settings?.email_main,
    address: {
      "@type": "PostalAddress",
      streetAddress: settings?.address,
      addressCountry: "RU",
    },
  };
}

export function buildWebSiteSchema(settings?: { company_name?: string }) {
  const base = siteUrl();
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: settings?.company_name ?? 'АО «Электроконтактор»',
    url: base,
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: `${base}/search?q={search_term_string}`,
      },
      "query-input": "required name=search_term_string",
    },
  };
}

export function buildBreadcrumbListSchema(
  breadcrumbs: { name: string; url: string }[],
) {
  if (!breadcrumbs.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: breadcrumbs.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

export function buildCollectionPageSchema(input: {
  name: string;
  description?: string;
  url: string;
  items: { name: string; url: string }[];
}) {
  return {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: input.name,
    description: input.description,
    url: input.url,
    mainEntity: {
      "@type": "ItemList",
      itemListElement: input.items.map((item, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: item.name,
        url: item.url,
      })),
    },
  };
}

export function buildCaseStudySchema(study: {
  title: string;
  excerpt?: string;
  slug: string;
  published_at: string;
}) {
  const base = siteUrl();
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: study.title,
    description: study.excerpt,
    datePublished: study.published_at,
    url: `${base}/cases/${study.slug}/`,
    author: {
      "@type": "Organization",
      name: 'АО «Электроконтактор»',
      url: base,
    },
    publisher: {
      "@type": "Organization",
      name: 'АО «Электроконтактор»',
      url: base,
    },
  };
}

export function buildProductSchema(
  product: {
    name: string;
    slug: string;
    short_description: string;
    category_slug: string;
    category_path?: string[];
    primary_image?: { url: string } | null;
    price_from: string | null;
    series_code: string;
    product_type?: string;
    specs?: { spec_key: string; spec_value: string; spec_unit?: string }[];
  },
  variant: {
    sku_code: string;
    price: string;
  } | null,
  breadcrumbs: { name: string; url: string }[],
  baseUrl?: string,
) {
  const resolvedBase = (baseUrl ?? siteUrl()).replace(/\/$/, "");
  const pathSlugs = product.category_path?.length
    ? product.category_path
    : [product.category_slug];
  const productUrl = `${resolvedBase}/catalog/${[...pathSlugs, product.slug].join("/")}`;
  const price =
    variant?.price && parseFloat(variant.price) > 0 ? variant.price : product.price_from;
  const manufacturer = {
    "@type": "Organization" as const,
    name: 'АО «Электроконтактор»',
    url: resolvedBase,
  };

  const series = product.series_code;
  const alternateName: string[] = [];
  if (series) {
    for (const prefix of ["КТ", "KT", "КТП", "KTP"]) {
      alternateName.push(`${prefix}${series}`, `${prefix} ${series}`, `${prefix}-${series}`);
    }
    alternateName.push(series);
  }

  const additionalProperty =
    product.specs?.slice(0, 12).map((spec) => ({
      "@type": "PropertyValue" as const,
      name: spec.spec_key,
      value: `${spec.spec_value}${spec.spec_unit ? ` ${spec.spec_unit}` : ""}`,
    })) ?? undefined;

  return [
    {
      "@context": "https://schema.org",
      "@type": "Product",
      name: product.name,
      alternateName: alternateName.length ? alternateName : undefined,
      description: product.short_description,
      sku: variant?.sku_code ?? product.series_code,
      image: productImageSrc(product.primary_image?.url, {
        name: product.name,
        slug: product.slug,
        series_code: product.series_code,
        product_type: product.product_type,
      }),
      brand: {
        "@type": "Brand",
        name: "Электроконтактор",
      },
      manufacturer,
      additionalProperty,
      offers: price
        ? {
            "@type": "Offer",
            priceCurrency: "RUB",
            price,
            availability: "https://schema.org/InStock",
            url: productUrl,
            seller: manufacturer,
          }
        : undefined,
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: breadcrumbs.map((item, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: item.name,
        item: item.url,
      })),
    },
  ];
}

/** Product + breadcrumbs + optional FAQ for JSON-LD on PDP. */
export function buildProductPageSchema(
  product: Parameters<typeof buildProductSchema>[0],
  variant: Parameters<typeof buildProductSchema>[1],
  breadcrumbs: { name: string; url: string }[],
  faq: Pick<FAQItem, "question" | "answer">[],
  baseUrl?: string,
): Record<string, unknown>[] {
  const blocks: Record<string, unknown>[] = [...buildProductSchema(product, variant, breadcrumbs, baseUrl)];
  const faqSchema = buildFAQPageSchema(faq);
  if (faqSchema) blocks.push(faqSchema);
  return blocks;
}

export function buildFAQPageSchema(items: Pick<FAQItem, "question" | "answer">[]) {
  if (!items.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}

export function buildNewsArticleSchema(post: {
  title: string;
  excerpt?: string;
  body?: string;
  published_at: string;
  slug: string;
}) {
  const base = siteUrl();
  return {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: post.title,
    description: post.excerpt,
    datePublished: post.published_at,
    dateModified: post.published_at,
    url: `${base}/news/${post.slug}/`,
    author: {
      "@type": "Organization",
      name: 'АО «Электроконтактор»',
      url: base,
    },
    publisher: {
      "@type": "Organization",
      name: 'АО «Электроконтактор»',
      url: base,
      logo: {
        "@type": "ImageObject",
        url: `${base}/photos/kt.png`,
      },
    },
  };
}
