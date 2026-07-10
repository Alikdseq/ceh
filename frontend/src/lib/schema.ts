import type { FAQItem } from "@/lib/types";

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

  return [
    {
      "@context": "https://schema.org",
      "@type": "Product",
      name: product.name,
      description: product.short_description,
      sku: variant?.sku_code ?? product.series_code,
      image: product.primary_image?.url,
      brand: {
        "@type": "Brand",
        name: "Электроконтактор",
      },
      manufacturer,
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
